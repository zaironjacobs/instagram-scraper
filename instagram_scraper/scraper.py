import os
import sys
import time
import getpass
import logging
import json

from json.decoder import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.support.wait import WebDriverWait
import colorama

from instagram_scraper import constants
from instagram_scraper.progress_bar import ProgressBar
from instagram_scraper import helper
from instagram_scraper.url_saver import save_image, save_video

WEBDRIVER_TIMEOUT = 1800000

logger = logging.getLogger('__name__')


class Scraper:

    def __init__(self, database, webdriver_interface, headful, maximum_download, login_username):
        self.__database = database
        self.__login_username = None
        self.__webdriver_interface = webdriver_interface
        self.__headful = headful
        self.__browser = None
        self.__maximum_download = maximum_download
        self.__login_username = login_username
        self.__post_save_success_count = 0
        self.__is_logged_in = False
        self.__download_stories = False
        self.__page_load_tries = 0
        self.__c_fore = colorama.Fore
        self.__c_style = colorama.Style
        colorama.init()

        # Stat the webdriver
        self.__start_browser()

        # Login if login_username was provided
        if self.__login_username is not None:
            login_password = getpass.getpass(prompt='Enter your password: ')
            if self.__login(login_password):
                self.__is_logged_in = True
                print('Login success.')
                answer = helper.yes_or_no('Would you like to download stories?')
                if answer:
                    self.__download_stories = True
            else:
                print('Login failed.')
                self.stop()

    def __check_ip_restriction(self):
        # Check if the official Instagram profile can be seen
        # If not, then Instagram has temporarily restricted the ip address (login required to view profiles)
        if self.__login_username is None and self.__get_id_by_username('instagram') is None:
            print(self.__c_fore.RED +
                  'Unable to load profiles at this time (IP temporarily restricted by Instagram).' +
                  self.__c_style.RESET_ALL)
            print(self.__c_fore.RED + 'Try logging in.' + self.__c_style.RESET_ALL)
            self.stop()

    def init_scrape_users(self, users):
        """ Start function for scraping users """

        helper.create_dir(constants.USERS_DIR)

        for x, user in enumerate(users):

            self.__check_ip_restriction()
            
            if x == 0:
                sys.stdout.write('\n')
            print('\033[1m' + 'Username: ' + user.username + '\033[0;0m')

            user.create_user_output_directories()
            self.__post_save_success_count = 0

            userid = self.__get_id_by_username(user.username)
            if userid is None:
                print(self.__c_fore.RED + 'Could not find the profile.' +
                      self.__c_style.RESET_ALL)
                continue

            self.__scrape_user_dp(user)
            if not self.__database.user_exists(user.username):
                self.__database.insert_userid_and_username(userid, user.username)

            # Download stories if logged in
            if self.__is_logged_in and self.__download_stories:
                stories_count = self.__count_user_stories(user)
                if stories_count > 0:
                    print('Downloading stories: ')
                    self.__scrape_user_stories(user, stories_count)

            # Check if posts are visible
            if not self.__profile_has_posts(user):
                if self.__is_account_private(user):
                    print(self.__c_fore.RED + 'Account is private.' + self.__c_style.RESET_ALL)
                else:
                    print(self.__c_fore.RED + 'No posts found.' + self.__c_style.RESET_ALL)

                sys.stdout.write('\n')
                continue

            print('Retrieving post links from profile, please wait... ')
            user.post_links = self.__scroll_down_and_grab_post_links(user.profile_link)

            # Check if the post link is already in the database, if yes then skip it
            # (if the post link was added by scraping a profile, not a tag)
            filtered_post_links = []
            for link in user.post_links:
                if not self.__database.user_post_link_exists(user.username, link):
                    filtered_post_links.append(link)
            user.post_links = filtered_post_links

            if len(user.post_links) <= 0:
                print('No new posts to download.')
            else:
                print(self.__c_fore.GREEN + str(len(user.post_links)) +
                      ' post(s) will be downloaded: ' + self.__c_style.RESET_ALL)

                progress_bar = ProgressBar(len(user.post_links), show_count=True)
                for link in user.post_links:
                    if self.__prepare_scrape_page(link, user.output_user_posts_path, userid):
                        progress_bar.update(1)
                progress_bar.close()

                if self.__post_save_success_count == len(user.post_links):
                    print('All posts downloaded.')
                else:
                    print(
                        self.__c_fore.RED + 'Not all posts have been saved. For more information check the log file.' +
                        self.__c_style.RESET_ALL)

            sys.stdout.write('\n')

    def init_scrape_tags(self, tags, tag_term):
        """ Start function for scraping tags """

        helper.create_dir(constants.TAGS_DIR)

        for tag in tags:

            self.__check_ip_restriction()

            print('\033[1m' + 'Tag: #' + tag.tagname + '\033[0;0m')

            tag.create_tag_output_directories()
            self.__post_save_success_count = 0
            link = 'https://www.instagram.com/explore/tags/' + tag.tagname + '/'
            self.__database.insert_tag(tag.tagname)

            if tag_term == constants.TAG_TERM_TOP:
                self.__scrape_top_tags(link, tag)
            elif tag_term == constants.TAG_TERM_RECENT:
                self.__scrape_recent_tags(link, tag)

        sys.stdout.write('\n')

    def __start_browser(self):
        """ Start the browser session """

        if self.__browser is None:

            if self.__webdriver_interface == constants.CHROMEDRIVER:
                driver_options = ChromeOptions()
                driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver_options.headless = not self.__headful

                webdriver_path = None
                for root, dirs, files in os.walk(constants.WEBDRIVERS_DIR):
                    for file in files:
                        if file[:len(constants.CHROMEDRIVER)].lower() == constants.CHROMEDRIVER.lower():
                            webdriver_path = constants.WEBDRIVERS_DIR + '/' + file
                            break
                    else:
                        print(self.__c_fore.RED + 'Webdriver for Google Chrome not found.' + self.__c_style.RESET_ALL)
                        self.stop()

                try:
                    self.__browser = webdriver.Chrome(
                        executable_path=webdriver_path,
                        service_log_path=os.devnull, options=driver_options)
                except SessionNotCreatedException as err:
                    logger.error(err)
                    print('Could not start session.')
                    self.stop()
                except WebDriverException as err:
                    logger.error(err)
                    print('Could not launch Google Chrome: ')
                    print(' Make sure Google Chrome is installed on your machine and is up to date.')
                    self.stop()

                self.__browser.maximize_window()
                self.__browser.set_page_load_timeout(WEBDRIVER_TIMEOUT)

            else:
                print(self.__c_fore.RED + 'No webdriver provided.' + self.__c_style.RESET_ALL)
                self.stop()

    def __go_to_link(self, link, force=False):
        """ Go to a given link """

        if self.__page_load_tries > 15:
            logger.error('Page load timeout.')
            print('\nPage load timeout.')
            self.stop()

        current_link = self.__browser.current_url
        current_link = current_link.strip('/')
        link = link.strip('/')

        if not force:
            if current_link == link:
                return

        try:
            self.__browser.get(link)

            WebDriverWait(self.__browser, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete')

            try:
                self.__browser.find_element_by_id(constants.CHROME_RELOAD_BUTTON_ID)
                self.__page_load_tries += 1
                logger.warning('Could not load page.')
                self.__go_to_link(link)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            try:
                self.__browser.find_element_by_id(constants.SORRY_ID)
                self.__page_load_tries += 1
                logger.warning('Facebook error.')
                self.__go_to_link(link)
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        except (TimeoutException, WebDriverException) as err:
            logger.error(err)
            logger.error('Page load timeout.')
            print('\nPage load timeout.')
            self.stop()

        self.__page_load_tries = 0

    def stop(self):
        """ Stop the program """

        if self.__is_logged_in:
            if not self.__logout():
                print('Logout failed.')

        if self.__browser is not None:
            self.__browser.quit()

        self.__database.close_connection()

        sys.exit(0)

    def __get_id_by_username(self, username):
        """ Return the user id """

        url = 'https://www.instagram.com/{}/?__a=1'
        self.__go_to_link(url.format(username))

        try:
            data = json.loads(self.__browser.find_element_by_tag_name('body').text)
            user_id = data['graphql']['user']['id']
            return user_id
        except JSONDecodeError as err:
            logger.error('Could not retrieve user id -> JSONDecodeError: %s', str(err))

    def __scroll_down_and_grab_post_links(self, link, xpath=None):
        """
        Scroll all the way to to the bottom of the page
        When xpath is given, only links inside the xpath will be retrieved
        """

        self.__go_to_link(link)

        post_links = []

        increment_browser_height = True

        while True:

            def grab_links():
                """ Search for links on the page and retrieve them """

                links = []

                # Grab post links inside the xpath only
                if xpath:
                    try:
                        element_box = self.__browser.find_element_by_xpath(xpath)
                        posts_element = element_box.find_elements_by_css_selector(constants.POSTS_CSS + ' [href]')
                        links += [post_element.get_attribute('href') for post_element in posts_element]
                    except (NoSuchElementException, StaleElementReferenceException) as err:
                        logger.error(err)
                        return []

                # Grab all post links
                else:
                    try:
                        elements = self.__browser.find_elements_by_css_selector(constants.POSTS_CSS + ' [href]')
                    except (NoSuchElementException, StaleElementReferenceException) as err:
                        logger.error(err)
                        return []

                    try:
                        links += [post_element.get_attribute('href') for post_element in elements]
                    except StaleElementReferenceException as err:
                        logger.error(err)
                        return []

                # Remove all duplicate links in the list and keep the list order
                links = sorted(set(links), key=lambda index: links.index(index))

                return links

            post_links += grab_links()

            # Remove any duplicates and return the list if maximum was reached
            post_links = sorted(set(post_links), key=lambda index: post_links.index(index))
            if len(post_links) >= self.__maximum_download:
                self.__browser.maximize_window()
                return post_links[:self.__maximum_download]

            # Scroll down to bottom
            self.__browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)

            # If instagram asks to show more posts, click it
            try:
                element = self.__browser.find_element_by_css_selector(constants.SHOW_MORE_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # No show more posts button found, do nothing
                pass
            else:
                element.click()

            try:
                self.__browser.find_element_by_css_selector(constants.SCROLL_LOAD_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # Reached the end, grab links for the last time, remove any duplicates and return the list
                post_links += grab_links()
                self.__browser.maximize_window()
                return sorted(set(post_links), key=lambda index: post_links.index(index))[:self.__maximum_download]
            else:
                # Change the browser height to prevent randomly being stuck while scrolling down
                height = self.__browser.get_window_size()['height']
                if increment_browser_height:
                    height += 25
                    increment_browser_height = False
                else:
                    height -= 25
                    increment_browser_height = True

                width = self.__browser.get_window_size()['width']
                self.__browser.set_window_size(width, height)

    def __scrape_top_tags(self, link, tag):
        """ Find the post links from the top tags """

        print('Retrieving post links from explore, please wait... ')

        self.__go_to_link(link)

        try:
            top_tags_box_element = self.__browser.find_element_by_xpath(constants.TOP_TAGS_XPATH)
        except (NoSuchElementException, StaleElementReferenceException):
            print(self.__c_fore.RED + 'No posts found.' + self.__c_style.RESET_ALL)
            return

        try:
            post_elements = top_tags_box_element.find_elements_by_css_selector(constants.POSTS_CSS + ' [href]')
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            return

        try:
            tag.post_links = [post_element.get_attribute('href') for post_element in post_elements]
        except StaleElementReferenceException as err:
            logger.error(err)
            return
        else:
            tag.post_links = tag.post_links[:self.__maximum_download]

            print(self.__c_fore.GREEN + str(len(tag.post_links)) + ' top post(s) will be downloaded: ' +
                  self.__c_style.RESET_ALL)
            progress_bar = ProgressBar(len(tag.post_links), show_count=True)
            for post_link in tag.post_links:
                if self.__prepare_scrape_page(post_link, tag.output_top_tag_path):
                    self.__database.insert_tag_post(post_link, tag.tagname, in_top=True)
                    progress_bar.update(1)
            progress_bar.close()

        if self.__post_save_success_count == len(tag.post_links):
            print('All posts downloaded.')
        else:
            print(
                self.__c_fore.RED + 'Not all posts have been saved. For more information check the log file.' +
                self.__c_style.RESET_ALL)

    def __scrape_recent_tags(self, link, tag):
        """ Find the post links from the recent tags """

        print('Retrieving post links from explore, please wait... ')

        self.__go_to_link(link)

        tag.post_links = self.__scroll_down_and_grab_post_links(link, constants.RECENT_TAGS_XPATH)

        if len(tag.post_links) < 1:
            print(self.__c_fore.RED + 'No posts found.' + self.__c_style.RESET_ALL)
            return

        print(self.__c_fore.GREEN + str(len(tag.post_links)) +
              ' recent post(s) will be downloaded: ' + self.__c_style.RESET_ALL)

        progress_bar = ProgressBar(len(tag.post_links), show_count=True)
        for post_link in tag.post_links:
            if self.__prepare_scrape_page(post_link, tag.output_recent_tag_path):
                self.__database.insert_tag_post(post_link, tag.tagname, in_recent=True)
                progress_bar.update(1)
        progress_bar.close()

        if self.__post_save_success_count == len(tag.post_links):
            print('All posts downloaded.')
        else:
            print(
                self.__c_fore.RED + 'Not all posts have been saved. For more information check the log file.' +
                self.__c_style.RESET_ALL)

    def __prepare_scrape_page(self, link, output_path, userid=None):
        """
        Loads the post page and decides whether to start scraping for a post with
        single content or multiple content
        """

        self.__go_to_link(link)

        # Check if page is available
        try:
            self.__browser.find_element_by_css_selector(constants.PAGE_NOT_AVAILABLE_PUBLIC_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # No "page isn't available" message found, do nothing
            pass
        else:
            logger.warning('Page not available at %s', link)
            return False
        try:
            self.__browser.find_element_by_css_selector(constants.PAGE_NOT_AVAILABLE_PRIVATE_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # No "page isn't available" message found, do nothing29;\hV65_l+yP4h=0lv*3@SH_
            pass
        else:
            logger.warning('Page not available at %s', link)
            return False

        # Try to load post link again if Instagram asks to login
        attempts = 5
        try:
            self.__browser.find_element_by_css_selector(constants.LOGIN_BOX_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # No login box found, do nothing
            pass
        else:
            logger.warning('Post link %s was redirected to login page.', link)
            for _ in range(attempts):
                if self.__browser.current_url != link:
                    self.__go_to_link(link)
                else:
                    break
            else:
                error_msg = 'Post link was redirected to login page ' + str(attempts) + ' times.'
                logger.error(error_msg)
                print('\n' + error_msg + '\nProgram stopped.')
                self.stop()

        # Scrape a multiple content post or single content post
        if self.__post_has_multiple_content(link):
            if self.__scrape_post_multiple_content(link, output_path):
                self.__database.insert_post(link, True, userid)
                return True
        elif not self.__post_has_multiple_content(link):
            if self.__scrape_post_single_content(link, output_path):
                self.__database.insert_post(link, False, userid)
                return True

        return False

    def __scrape_user_dp(self, user):
        """ Download the user display photo """

        self.__go_to_link(user.profile_link)
        display_picture_url = None

        try:
            element = self.__browser.find_element_by_css_selector(constants.DISPLAY_PIC_PUBLIC_CSS)
            display_picture_url = element.get_attribute('src')
        except (NoSuchElementException, StaleElementReferenceException):
            # No display pic found (public profile)
            pass

        try:
            element = self.__browser.find_element_by_css_selector(constants.DISPLAY_PIC_PRIVATE_CSS)
            display_picture_url = element.get_attribute('src')
        except (NoSuchElementException, StaleElementReferenceException):
            # No display pic found (private profile)
            pass

        if not save_image(display_picture_url, user.output_user_dp_path):
            logger.error('Could not save display picture for profile at %s', user.profile_link)
            print(self.__c_fore.RED + 'Could not save display picture.' + self.__c_style.RESET_ALL)

    def __post_has_multiple_content(self, link):
        """ Check if post has multiple content """

        self.__go_to_link(link)
        try:
            self.__browser.find_element_by_css_selector(constants.GROUP_INDICATORS_CSS)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            # Post has no multiple content, do nothing
            return False

    def __scrape_post_single_content(self, link, output_path):
        """ Find the src url of images or videos from a post with one content and save """

        # Get the published date of the post
        date_time = None
        try:
            element = self.__browser.find_element_by_css_selector(constants.POST_TIME_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
        else:
            date_time = element.get_attribute('datetime')

        # Get the image
        try:
            element = self.__browser.find_element_by_css_selector(constants.IMG_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # Is not an image, do nothing
            pass
        else:
            img_url = element.get_attribute('src')
            if save_image(img_url, output_path, date_time=date_time):
                self.__post_save_success_count += 1
                return True
            logger.error('Error downloading post: %s', link)
            return False

        # Get the video
        try:
            element = self.__browser.find_element_by_css_selector(constants.VID_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # Is not a video, do nothing
            pass
        else:
            vid_url = element.get_attribute('src')
            if save_video(vid_url, output_path, date_time=date_time):
                self.__post_save_success_count += 1
                return True
            logger.error('Error downloading post: %s', link)
            return False

        logger.error('Error downloading post: %s', link)
        return False

    def __scrape_post_multiple_content(self, link, output_path):
        """ Find the src url of images and videos from a post with multiple content and save """

        def click_next_control():
            """ Go to the next content in a post with multiple content """

            try:
                next_element = self.__browser.find_element_by_css_selector(constants.NEXT_CONTROL_CSS)
            except (NoSuchElementException, StaleElementReferenceException) as error:
                logger.error(error)
            else:
                next_element.click()
                time.sleep(1)

        content_success_count = 0

        # Get the published date of the post
        date_time = None
        try:
            element = self.__browser.find_element_by_css_selector(constants.POST_TIME_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
        else:
            date_time = element.get_attribute('datetime')

        # Get amount of content in the post
        try:
            elements = self.__browser.find_elements_by_css_selector(constants.INDICATOR)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            logger.error('Error downloading post: %s', link)
            return False
        else:
            post_content_count = len(elements)

        for i in range(post_content_count):
            li_element = None

            # Find the ul element that contains the contents
            try:
                ul_element = self.__browser.find_element_by_css_selector(constants.MULTIPLE_CONTENT_UL_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                return False

            # First displayed content is found at the first li inside ul
            if i == 0:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[0]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    return False

            # All displayed content that is not first or last is found at the second li inside ul
            elif 0 < i < post_content_count:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[1]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    return False

            # Last displayed content is found at the last li inside ul
            elif i == post_content_count - 1:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[-1]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    return False

            # Get the image src from the li element
            try:
                img_element = li_element.find_element_by_css_selector(
                    constants.IMG_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # Is not an image, do nothing
                pass
            else:
                img_url = img_element.get_attribute('src')
                if save_image(img_url, output_path, date_time=date_time, count=i + 1):
                    content_success_count += 1
                    if i < post_content_count - 1:
                        click_next_control()
                    continue
                logger.error('Error downloading image at post(' + str(i + 1) + '): %s', link)
                continue

            # Get the video src from the li element
            try:
                vid_element = li_element.find_element_by_css_selector(constants.VID_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # Is not a video, do nothing
                pass
            else:
                vid_url = vid_element.get_attribute('src')
                if save_video(vid_url, output_path, date_time=date_time, count=i + 1):
                    content_success_count += 1
                    if i < post_content_count - 1:
                        click_next_control()
                    continue
                logger.error('Error downloading video at post(' + str(i + 1) + '): %s', link)
                continue

            logger.error('No image or video downloaded at post(' + str(i + 1) + '): %s', link)

        if content_success_count == post_content_count:
            self.__post_save_success_count += 1
            return True

        logger.error('Error downloading post: %s', link)
        return False

    def __scrape_user_stories(self, user, stories_count):
        """ Find the src urls of images and videos from stories and save """

        self.__go_to_link(user.stories_link)

        try:
            tap_element = self.__browser.find_element_by_css_selector(constants.STORIES_TAP_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            print('Could not download stories, for more information check the log.')
        else:
            tap_element.click()
            time.sleep(1)

        success = 0
        progress_bar = ProgressBar(stories_count, show_count=True)
        for i in range(stories_count):
            next_story_button = self.__browser.find_element_by_css_selector(constants.STORIES_NEXT_CSS)

            # Check if the story is a video and download it
            try:
                vid_elements = self.__browser.find_element_by_css_selector(constants.STORIES_VID_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # Is not a video, do nothing
                pass
            else:
                vid_elements_src = vid_elements.find_elements_by_tag_name('source')
                vid_url = vid_elements_src[0].get_attribute('src')
                if save_video(vid_url, user.output_user_stories_path):
                    success += 1
                    progress_bar.update(1)

                # Go to the next story
                if i < stories_count - 1:
                    next_story_button.click()
                    time.sleep(1)
                continue

            # Check if the story is an image and download it
            try:
                img_element = self.__browser.find_element_by_css_selector(
                    'img[class="' + constants.STORIES_IMG_CSS[1:] + '"]')
            except (NoSuchElementException, StaleElementReferenceException):
                # Is not an image, do nothing
                pass
            else:
                img_url = img_element.get_attribute('src')
                if save_image(img_url, user.output_user_stories_path):
                    success += 1
                    progress_bar.update(1)

                # Go to the next story
                if i < stories_count - 1:
                    next_story_button.click()
                    time.sleep(1)
                continue

            logger.error('A story could not be downloaded from %s', user.username)

        progress_bar.close()

        if success == stories_count:
            print('All stories downloaded.')
        else:
            print('Not all stories have been downloaded')

    def __count_user_stories(self, user):
        """ Count amount of stories """

        self.__go_to_link(user.stories_link)
        time.sleep(2)
        try:
            stories_bar = self.__browser.find_elements_by_css_selector(constants.STORIES_BAR_CSS)
            return len(stories_bar)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        return 0

    def __is_account_private(self, user):
        """ Check if account is private """

        self.__go_to_link(user.profile_link)
        try:
            self.__browser.find_element_by_css_selector(constants.USER_PRIVATE_CSS)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def __profile_has_posts(self, user):
        """ Check if there are posts in the profile """

        self.__go_to_link(user.profile_link)
        try:
            self.__browser.find_element_by_css_selector(constants.POSTS_CSS)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def __login(self, login_password):
        """ Login user with credentials """

        self.__go_to_link(constants.INSTAGRAM_URL)
        time.sleep(2)

        # Get the credential element
        try:
            credential_elements = self.__browser.find_elements_by_css_selector(constants.CREDENTIALS_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            return False

        # Click username box and fill
        try:
            username_element = credential_elements[0]
        except ElementClickInterceptedException as err:
            logger.error(err)
            return False
        else:
            username_element.click()
            username_element.send_keys(self.__login_username)

        # Click password box and fill
        try:
            password_element = credential_elements[1]
        except ElementClickInterceptedException as err:
            logger.error(err)
            return False
        else:
            password_element.click()
            password_element.send_keys(login_password)

        # Click login button
        try:
            button_element = self.__browser.find_element_by_css_selector(constants.LOGIN_BUTTON_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            return False
        else:
            button_element.click()
            time.sleep(4)

        # Enter security code if asked for
        try:
            security_input_box = self.__browser.find_element_by_css_selector(constants.SECURITY_INPUT_BOX_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        else:
            security_input_box.click()
            time.sleep(2)
            try:
                security_code = getpass.getpass(prompt='Enter security code: ')
                security_input_box.send_keys(security_code)
                security_button_element = self.__browser.find_element_by_css_selector(constants.SECURITY_BOX_BUTTON)
            except (NoSuchElementException, StaleElementReferenceException) as err:
                logger.info(err)
                return False
            else:
                security_button_element.click()
                time.sleep(4)

        # Click no if asked to save login info
        try:
            not_save_login_button = self.__browser.find_element_by_css_selector(
                constants.NOT_SAVE_LOGIN_INFO_BUTTON_CSS)
        except(NoSuchElementException, StaleElementReferenceException):
            # User was not asked to save login info, do nothing
            pass
        else:
            not_save_login_button.click()
            time.sleep(2)

        # Check for failed login message
        try:
            self.__browser.find_element_by_css_selector(constants.FAILED_LOGIN_MESSAGE_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # No failed login message found, do nothing
            pass
        else:
            return False

        # Check if Instagram shows popup asking to turn on notifications
        try:
            no_notifications_element = self.__browser.find_element_by_css_selector(
                constants.NO_NOTIFICATIONS_BUTTON_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            # No popup found, do nothing
            pass
        else:
            no_notifications_element.click()

        return True

    def __logout(self):
        """ Logout user """

        self.__go_to_link(constants.INSTAGRAM_URL + self.__login_username)

        # Click settings
        try:
            settings_button_element = self.__browser.find_element_by_css_selector(constants.SETTINGS_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            return False
        else:
            settings_button_element.click()
            time.sleep(2)

        # Get settings buttons elements
        try:
            settings_list_elements = self.__browser.find_elements_by_css_selector(constants.SETTINGS_BUTTONS_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            return False

        # Click logout button
        try:
            logout_button = settings_list_elements[8]
            logout_button.click()
        except ElementClickInterceptedException as err:
            logger.error(err)
            return False
        else:
            time.sleep(2)
            self.__is_logged_in = False
            return True
