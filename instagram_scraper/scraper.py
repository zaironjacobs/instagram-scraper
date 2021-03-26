import os
import sys
import getpass
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import SessionNotCreatedException

import colorama

from .database import Database
from . import constants
from .progress_bar import ProgressBar
from . import helper
from . import get_data
from . import actions

logger = logging.getLogger('__name__')


class Scraper:

    def __init__(self, headful, download_stories, max_download, login_username):
        self.__c_fore = colorama.Fore
        self.__c_style = colorama.Style
        colorama.init()

        self.__database = Database()
        self.__database.create_tables()

        self.__headful = headful
        self.__download_stories = download_stories
        self.__max_download = max_download
        self.__login_username = login_username

        self.__is_logged_in = False
        self.__cookies_accepted = False

        self.__web_driver = self.__start_web_driver()

        if self.__login_username:
            self.__init_login()

        if self.__max_download == 0:
            print(self.__c_fore.RED
                  + 'add the argument \'--max 3\' to specify a maximum amount of posts to scrape'
                  + self.__c_style.RESET_ALL)
            self.stop()

        if not self.__is_logged_in and self.__download_stories:
            print(self.__c_fore.RED + 'you need to be logged in to scrape stories' + self.__c_style.RESET_ALL)
            self.stop()

    def __start_web_driver(self):
        """ Start the web driver """

        driver_options = ChromeOptions()
        driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver_options.add_argument('--mute-audio')
        driver_options.add_argument('--user-agent=Mozilla/5.0 Chrome/74.0.3729.169 Safari/537.36')
        driver_options.headless = not self.__headful

        try:
            driver = webdriver.Chrome(service_log_path=os.devnull, options=driver_options)
        except SessionNotCreatedException as err:
            logger.error(err)
            print('could not start session')
            self.stop()
        except WebDriverException as err:
            logger.error('Launch Google Chrome error: %s' % err)
            print('could not launch Google Chrome: ')
            print('make sure Google Chrome is installed on your machine')
            self.stop()
        else:
            driver.maximize_window()
            driver.set_page_load_timeout(600)

            return driver

    def __check_if_ip_is_restricted(self):
        """
        Check if the official Instagram profile can be seen.
        If not, then Instagram has temporarily restricted the ip address.
        """

        if get_data.get_id_by_username_from_ig('instagram') is None:
            print(self.__c_fore.RED +
                  'unable to load profiles at this time (IP temporarily restricted by Instagram)' + '\n' +
                  'try to login with a DUMMY account to scrape' +
                  self.__c_style.RESET_ALL)
            self.stop()

    def __init_login(self):
        """ Login """

        if self.__login_username and not self.__is_logged_in:
            sys.stdout.write('\n')
            print('login with a DUMMY account, never use your personal account')
            login_password = getpass.getpass(prompt='enter your password: ')
            actions.Login(self, self.__login_username, login_password).do()
            print('login success')

    def __init_scrape_stories(self, user):
        """ Start function for scraping stories """

        print('counting stories, please wait...')
        stories_amount = actions.CountStories(self, user).do()

        if stories_amount > 0:
            print(self.__c_fore.GREEN
                  + str(stories_amount) + ' image(s)/video(s) will be downloaded from stories: '
                  + self.__c_style.RESET_ALL)
            actions.ScrapeStories(self, user, stories_amount).do()
        else:
            print('no stories found')

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

            # Retrieve the id using actions
            if self.__is_logged_in:
                userid = actions.GetUserId(self, user.username).do()
            # Retrieve the id using requests
            else:
                userid = get_data.get_id_by_username_from_ig(user.username)

            # Continue to next user if id not found
            if userid is None:
                print(self.__c_fore.RED + 'could not load user profile' + self.__c_style.RESET_ALL)
                import time
                time.sleep(1000)
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
            self.__web_driver.quit()
        except AttributeError as err:
            logger.error('Quit driver error: %s' % err)

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
    def login_username(self):
        return self.__login_username

    @property
    def database(self):
        return self.__database

    @property
    def max_download(self):
        return self.__max_download
