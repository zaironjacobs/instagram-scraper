import os
import sys
import getpass
import logging
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import SessionNotCreatedException

import colorama

from instagram_scraper.database import Database
from instagram_scraper import constants
from instagram_scraper.progress_bar import ProgressBar
from instagram_scraper import helper
from instagram_scraper import get_data
from instagram_scraper import actions

logger = logging.getLogger('__name__')


class Scraper:

    def __init__(self, headful, max_download, login_username):
        self.__c_fore = colorama.Fore
        self.__c_style = colorama.Style
        colorama.init()

        self.__database = Database()
        self.__database.create_tables()

        self.__headful = headful
        self.__max_download = max_download
        self.__login_username = login_username

        self.__is_logged_in = False
        self.__download_stories = False
        self.__cookies_accepted = False

        self.__web_driver = self.__start_web_driver()

        self.__init_login()

    def __start_web_driver(self):
        """ Start the web driver """

        driver_options = ChromeOptions()
        driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver_options.headless = not self.__headful

        webdriver_path = None
        if platform.system() == 'Windows':
            for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
                for file in files:
                    if file.lower() == constants.CHROMEDRIVER.lower() + '.exe':
                        webdriver_path = constants.WEBDRIVER_DIR + '/' + file
                        break
        elif platform.system() == 'Linux':
            for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
                for file in files:
                    if file.lower() == constants.CHROMEDRIVER.lower():
                        webdriver_path = constants.WEBDRIVER_DIR + '/' + file
                        break
        elif platform.system() == 'Darwin':
            for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
                for file in files:
                    if file.lower() == constants.CHROMEDRIVER.lower():
                        webdriver_path = constants.WEBDRIVER_DIR + '/' + file
                        break
        else:
            print(self.__c_fore.RED + 'webdriver for google chrome not found' + self.__c_style.RESET_ALL)
            self.stop()

        try:
            driver = webdriver.Chrome(
                executable_path=webdriver_path,
                service_log_path=os.devnull, options=driver_options)
        except SessionNotCreatedException as err:
            logger.error(err)
            print('could not start session, make sure you have the latest Chrome version installed')
            self.stop()
        except WebDriverException as err:
            logger.error(err)
            print('could not launch Google Chrome: ')
            print('make sure Google Chrome is installed on your machine and is up to date')
            self.stop()
        else:
            if self.__headful:
                driver.maximize_window()
            else:
                driver.set_window_size(1366, 768)
            driver.set_page_load_timeout(1800000)

            return driver

    def __check_if_ip_is_restricted(self):
        """
        Check if the official Instagram profile can be seen.
        If not, then Instagram has temporarily restricted the ip address (login required to view profiles).
        """

        if get_data.get_id_by_username_from_ig('instagram') is None:
            print(self.__c_fore.RED +
                  'unable to load profiles at this time (IP temporarily restricted by Instagram)' +
                  self.__c_style.RESET_ALL)
            print(self.__c_fore.RED + 'try logging in' + self.__c_style.RESET_ALL)
            self.stop()

    def __init_login(self):
        """ Login """

        if self.__login_username:
            sys.stdout.write('\n')
            login_password = getpass.getpass(prompt='enter your password: ')
            actions.Login(self, self.__login_username, login_password).do()
            print('login success')
            answer = helper.yes_or_no('download images and videos from stories?')
            if answer:
                self.__download_stories = True

    def __init_scrape_stories(self, user):

        print('counting stories, please wait...')
        stories_amount = actions.CountStories(self, user).do()

        if stories_amount > 0:
            print(self.__c_fore.GREEN
                  + str(stories_amount) + ' image(s)/video(s) will be downloaded from stories: '
                  + self.__c_style.RESET_ALL)
            actions.ScrapeStories(self, user, stories_amount).do()

    def __filter_post_links(self, user):
        """
        Check if the post link is already in the database (if post link was added by scraping a profile).
        If yes then skip it.
        """

        filtered_post_links = []
        for link in user.post_links:
            if not self.__database.user_post_link_exists(user.username, link):
                filtered_post_links.append(link)
        return filtered_post_links

    def init_scrape_users(self, users):
        """ Start function for scraping users """

        helper.create_dir(constants.USERS_DIR)

        for x, user in enumerate(users):

            if not self.__is_logged_in:
                self.__check_if_ip_is_restricted()

            sys.stdout.write('\n')
            print('\033[1m' + 'username: ' + user.username + '\033[0;0m')

            user.create_user_output_directories()

            userid = get_data.get_id_by_username_from_ig(user.username)
            if userid is None:
                print(self.__c_fore.RED + 'username not found' + self.__c_style.RESET_ALL)
                continue

            actions.ScrapeDisplay(self, user).do()

            if not self.__database.user_exists(user.username):
                self.__database.insert_userid_and_username(userid, user.username)

            if self.__is_logged_in and self.__download_stories:
                self.__init_scrape_stories(user)

            if actions.CheckIfAccountIsPrivate(self, user).do():
                print(self.__c_fore.RED + 'account is private' + self.__c_style.RESET_ALL)
                continue

            if not actions.CheckIfProfileHasPosts(self, user).do():
                print(self.__c_fore.RED + 'no posts found' + self.__c_style.RESET_ALL)
                continue

            print('retrieving post links from profile, please wait... ')

            user.post_links = actions.GrabPostLinks(self, user.profile_link).do()
            user.post_links = self.__filter_post_links(user)

            if len(user.post_links) <= 0:
                print('no new posts to download')
            else:
                print(self.__c_fore.GREEN + str(len(user.post_links)) +
                      ' post(s) will be downloaded: ' + self.__c_style.RESET_ALL)

                progress_bar = ProgressBar(len(user.post_links), show_count=True)
                for link in user.post_links:
                    actions.InitScrape(self, link, user.output_user_posts_path, userid).do()
                    progress_bar.update(1)
                progress_bar.close()

    def init_scrape_tags(self, tags, tag_type):
        """ Start function for scraping tags """

        helper.create_dir(constants.TAGS_DIR)

        for tag in tags:

            if not self.__is_logged_in:
                self.__check_if_ip_is_restricted()

            sys.stdout.write('\n')
            print('\033[1m' + 'tag: #' + tag.tagname + '\033[0;0m')

            tag.create_tag_output_directories()

            link = constants.INSTAGRAM_EXPLORE_URL.format(tag.tagname)
            self.__database.insert_tag(tag.tagname)

            if tag_type == constants.TAG_TYPE_TOP:
                actions.ScrapeTopTags(self, link, tag).do()
            elif tag_type == constants.TAG_TYPE_RECENT:
                actions.ScrapeRecentTags(self, link, tag).do()

    def stop(self):
        """ Stop the program """

        if self.__is_logged_in:
            actions.Logout(self, self.__login_username).do()

        try:
            self.web_driver.quit()
        except AttributeError as err:
            logger.error(err)

        self.__database.close_connection()
        sys.exit(0)

    @property
    def is_logged_in(self):
        return self.__is_logged_in

    @is_logged_in.setter
    def is_logged_in(self, is_logged_in):
        self.__is_logged_in = is_logged_in

    @property
    def cookies_accepted(self):
        return self.__cookies_accepted

    @cookies_accepted.setter
    def cookies_accepted(self, accepted):
        self.__cookies_accepted = accepted

    @property
    def web_driver(self):
        return self.__web_driver

    @property
    def database(self):
        return self.__database

    @property
    def max_download(self):
        return self.__max_download
