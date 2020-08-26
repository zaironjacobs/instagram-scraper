import os
import sys
import zipfile
import argparse
import platform
import logging
from signal import signal, SIGINT
from urllib.error import HTTPError

import wget

from instagram_scraper import constants
from instagram_scraper.scraper import Scraper
from instagram_scraper.user import User
from instagram_scraper.tag import Tag
from instagram_scraper.database import Database
from instagram_scraper import req_userinfo
from instagram_scraper.version import __version__
from instagram_scraper import helper

logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)
# logger_file_handler = logging.FileHandler(os.path.expanduser(os.path.join('~', '.igscraper.log')))
logger_file_handler = logging.FileHandler('igscraper.log')
logger_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logger_file_handler.setFormatter(logger_formatter)
logger.addHandler(logger_file_handler)


def main():
    def signal_handler(signal_received, frame):
        """ Handles clean Ctrl+C exit """

        sys.stdout.write('\n')
        sys.exit(0)

    signal(SIGINT, signal_handler)
    App()


class App:

    def __init__(self):
        self.__no_db_found_str = 'No database found.'
        self.__must_provide_tag_str = 'Provide at least one tag.'
        self.__download_completed_str = 'Download completed.'

        parser = argparse.ArgumentParser()
        parser.add_argument('users', help='instagram users to scrape', nargs='*')
        parser.add_argument('--login-username', '--login_username', type=str, metavar='',
                            help='instagram login username.')
        parser.add_argument('--update-users', '--update_users', help='check all scraped users for new posts',
                            action='store_true')
        parser.add_argument('--top-tags', '--top_tags', help='top tags to scrape', nargs='*')
        parser.add_argument('--recent-tags', '--recent_tags', help='recent tags to scrape', nargs='*')
        parser.add_argument('--max', metavar='', help='maximum number of posts to scrape')
        parser.add_argument('--headful', help='display the browser UI', action='store_true')
        parser.add_argument('--set-driver', '--set_driver', help='choose a webdriver', action='store_true')
        parser.add_argument('--list-users', '--list_users', help='list all scraped users', action='store_true')
        parser.add_argument('--list-tags', '--list_tags', help='list all scraped tags', action='store_true')
        parser.add_argument('--remove-users', '--remove_users', nargs='+', metavar='',
                            help='remove username(s)')
        parser.add_argument('--remove-users-n', '--remove_users_n', nargs='+', metavar='',
                            help='remove user(s) by number')
        parser.add_argument('--remove-all-users', '--remove_all_users', help='remove all users',
                            action='store_true')
        parser.add_argument('--remove-tags', '--remove_tags', nargs='+', metavar='', help='remove tag(s) by tagname')
        parser.add_argument('--remove-tags-n', '--remove_tags_n', nargs='+', metavar='',
                            help='remove tag(s) by tagname')
        parser.add_argument('--remove-all-tags', '--remove_all_tags', help='remove all tags', action='store_true')
        parser.add_argument('--version', help='program version', action='store_true')
        args = parser.parse_args()

        if args.version:
            print('v' + __version__)
            sys.exit(0)

        if args.list_users:
            if os.path.isfile(constants.LOCAL_DB):
                self.__list_all_users()
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.list_tags:
            if os.path.isfile(constants.LOCAL_DB):
                self.__list_all_tags()
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.remove_users:
            if os.path.isfile(constants.LOCAL_DB):
                self.__remove_users_by_username(args.remove_users)
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.remove_tags:
            if os.path.isfile(constants.LOCAL_DB):
                self.__remove_tags_by_tagname(args.remove_tags)
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.remove_tags_n:
            if os.path.isfile(constants.LOCAL_DB):
                self.__remove_tags_by_number(args.remove_tags_n)
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.remove_users_n:
            if os.path.isfile(constants.LOCAL_DB):
                self.__remove_users_by_number(args.remove_users_n)
                sys.exit(0)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.remove_all_users:
            self.__remove_all_users()
            sys.exit(0)

        if args.remove_all_tags:
            self.__remove_all_tags()
            sys.exit(0)

        self.__maximum_download = 1000000000
        if args.max:
            try:
                self.__maximum_download = int(args.max)
                if self.__maximum_download < 1:
                    print('--max has to be 1 or greater.')
                    sys.exit(0)
            except (ValueError, TypeError):
                print('--max has to be a number')
                sys.exit(0)

        self.__headful = args.headful

        top_tags = []
        if args.top_tags is not None:
            if len(args.top_tags) > 0:
                top_tags = self.__create_tag_objects(args.top_tags)
            else:
                print(self.__must_provide_tag_str)
                sys.exit(0)

        recent_tags = []
        if args.recent_tags is not None:
            if args.max is None:
                print('Provide a maximum amount to download as well with --max')
                sys.exit(0)
            if len(args.recent_tags) > 0:
                recent_tags = self.__create_tag_objects(args.recent_tags)
            else:
                print(self.__must_provide_tag_str)
                sys.exit(0)

        database = Database()
        database.create_tables()

        self.webdriver_interface = None
        current_webdriver_name = self.__get_current_webdriver_name()
        if not current_webdriver_name:
            self.__choose_webdriver()
        elif current_webdriver_name == constants.CHROMEDRIVER:
            self.webdriver_interface = constants.CHROMEDRIVER

        print('Starting...')

        users = []
        if len(args.users) > 0:
            usernames_to_scrape = sorted(set(args.users), key=lambda index: args.users.index(index))
            users = self.__create_user_objects(usernames_to_scrape)
        elif args.update_users:
            if os.path.isfile(constants.LOCAL_DB):
                usernames_to_scrape = self.__get_all_usernames()
                if len(usernames_to_scrape) == 0:
                    print('No users found in the database.')
                    sys.exit(0)
                users = self.__create_user_objects(usernames_to_scrape)
            else:
                print(self.__no_db_found_str)
                sys.exit(0)

        if args.set_driver:
            self.__choose_webdriver()
            sys.exit(0)

        if len(users) == 0 and len(top_tags) == 0 and len(recent_tags) == 0:
            print('Provide at least one username or tag to scrape.')
            sys.exit(0)

        scraper = Scraper(database, self.webdriver_interface, self.__headful, self.__maximum_download,
                          args.login_username)

        if len(users) > 0:
            scraper.init_scrape_users(users)

        if len(top_tags) > 0:
            scraper.init_scrape_tags(top_tags, constants.TAG_TERM_TOP)

        if len(recent_tags) > 0:
            scraper.init_scrape_tags(recent_tags, constants.TAG_TERM_RECENT)

        scraper.stop()

    def __create_user_objects(self, usernames_to_scrape):
        """ Create user objects """

        users = []
        for input_username in usernames_to_scrape:
            input_username = input_username.lower()
            input_username = self.__check_for_new_username(input_username)
            user = User(input_username)
            users.append(user)
        return users

    def __create_tag_objects(self, tagnames_to_scrape):
        """ Create tag objects """

        tags = []
        for input_tag in tagnames_to_scrape:
            input_tag = input_tag.lower()
            tag = Tag(input_tag)
            tags.append(tag)
        return tags

    def __get_all_usernames(self):
        """ Retrieve all usernames from database """

        database = Database()
        usernames = []
        db_usernames = database.retrieve_all_usernames()
        if len(db_usernames) > 0:
            for user in db_usernames:
                usernames.append(user)
        database.close_connection()
        return usernames

    def __get_all_tagnames(self):
        """ Retrieve all tags from database """

        database = Database()
        tags = []
        db_tags = database.retrieve_all_tags()
        if len(db_tags) > 0:
            for tag in db_tags:
                tags.append(tag)

        database.close_connection()
        return tags

    def __check_for_new_username(self, input_username):
        """ If user has a new username, then update it in the database and rename the user dir """

        database = Database()
        user_id = database.get_id_by_username(input_username)
        if user_id:
            ig_username = req_userinfo.get_username_by_id(user_id)
            if ig_username:
                if input_username != ig_username:
                    database.rename_user(user_id, ig_username)
                    helper.rename_dir(input_username, ig_username)
                    return ig_username
        database.close_connection()
        return input_username

    def __list_all_users(self):
        """ List all users in the database """

        database = Database()
        usernames_dict = self.__get_usernames_dict()
        if len(usernames_dict) > 0:
            first_str = 'User'
            second_str = 'Posts scraped'
            descriptor = '{:<40} {}'
            print('')
            print(descriptor.format(first_str, second_str))
            print(descriptor.format(len(first_str) * '-', len(second_str) * '-'))
            for number, username in usernames_dict.items():
                space_str = ' ' if len(str(number)) > 1 else '  '
                first = '[' + space_str + str(number) + '] ' + username
                second = str(database.get_user_post_count(username))
                print(descriptor.format(first, second))
        else:
            print('No users found in the database.')
        database.close_connection()

    def __list_all_tags(self):
        """ List all tags in the database """

        database = Database()
        tags_dict = self.__get_tagnames_dict()
        if len(tags_dict) > 0:
            first_str = 'Tag'
            second_str = 'Top posts scraped'
            third_str = 'Recent posts scraped'
            descriptor = '{:<40} {:<20} {}'
            print('')
            print(descriptor.format(first_str, second_str, third_str))
            print(descriptor.format(len(first_str) * '-', len(second_str) * '-',
                                    len(third_str) * '-'))
            for number, tag in tags_dict.items():
                space_str = ' ' if len(str(number)) > 1 else '  '
                first = '[' + space_str + str(number) + '] ' + tag
                second = str(database.get_top_tag_post_count(tag))
                third = str(database.get_recent_tag_post_count(tag))
                print(descriptor.format(first, second, third))
        else:
            print('No tags found in the database.')
        database.close_connection()

    def __remove_users_by_username(self, input_usernames):
        """ Remove requested user(s) from the database and their output directory """

        database = Database()
        input_usernames = sorted(set(input_usernames), key=lambda index: input_usernames.index(index))
        usernames = []
        for username in input_usernames:
            if database.user_exists(username):
                usernames.append(username)

        if len(usernames) < 1:
            print('User not found.')
            return

        usernames_str = ' '.join([str(username) for username in usernames])
        answer = helper.yes_or_no('Removing:\n ' + usernames_str + '\nProceed?')

        if answer:
            for username in input_usernames:
                database.remove_user(username)
                try:
                    helper.remove_dir(constants.USERS_DIR + '/' + username)
                except OSError as err:
                    logger.error(err)
        database.close_connection()

    def __remove_tags_by_tagname(self, input_tags):
        """ Remove requested tags(s) from the database and their output directory """

        database = Database()
        input_tags = sorted(set(input_tags), key=lambda index: input_tags.index(index))
        tags = []
        for tag in input_tags:
            if database.tag_exists(tag):
                tags.append(tag)

        if len(tags) < 1:
            print('Tag not found.')
            return

        tags_str = ' '.join([str(tag) for tag in tags])
        answer = helper.yes_or_no('Removing:\n ' + tags_str + '\nProceed?')

        if answer:
            for tag in input_tags:
                database.remove_tag(tag)
                try:
                    helper.remove_dir(constants.TAGS_DIR + '/' + tag)
                except OSError as err:
                    logger.error(err)
        database.close_connection()

    def __remove_users_by_number(self, input_numbers):
        """ Remove requested user(s) from the database and their output directory """

        input_numbers = sorted(set(input_numbers), key=lambda index: input_numbers.index(index))
        try:
            input_numbers = list(map(int, input_numbers))
        except ValueError as err:
            logger.error(err)
            print('Only numbers allowed.')
            sys.exit(0)

        database = Database()
        usernames_dict = self.__get_usernames_dict()
        usernames = [v for k, v in usernames_dict.items() if k in input_numbers]

        if len(usernames) < 1:
            print('User not found.')
            return

        usernames_str = ' '.join([str(username) for username in usernames])
        answer = helper.yes_or_no('Removing:\n ' + usernames_str + '\nProceed?')

        if answer:
            for username in usernames:
                if database.user_exists(username):
                    database.remove_user(username)
                try:
                    helper.remove_dir(constants.USERS_DIR + '/' + username)
                except OSError as err:
                    logger.error(err)
        database.close_connection()

    def __remove_tags_by_number(self, input_numbers):
        """ Remove requested tag(s) from the database and their output directory """

        input_numbers = sorted(set(input_numbers), key=lambda index: input_numbers.index(index))
        try:
            input_numbers = list(map(int, input_numbers))
        except ValueError as err:
            logger.error(err)
            print('Only numbers allowed.')
            sys.exit(0)

        database = Database()
        tags_dict = self.__get_tagnames_dict()
        tags = [v for k, v in tags_dict.items() if k in input_numbers]

        if len(tags) < 1:
            print('Tag not found.')
            return

        tags_str = ' '.join([str(tag) for tag in tags])
        answer = helper.yes_or_no('Removing:\n ' + tags_str + '\nProceed?')

        if answer:
            for tag in tags:
                if database.tag_exists(tag):
                    database.remove_tag(tag)
                try:
                    helper.remove_dir(constants.TAGS_DIR + '/' + tag)
                except OSError as err:
                    logger.error(err)

        database.close_connection()

    def __remove_all_users(self):
        """ Remove all users from the database and all user output directories """

        answer = helper.yes_or_no('Are you sure you want to remove all users?')
        if answer:
            if os.path.isfile(constants.LOCAL_DB):
                database = Database()
                usernames = database.retrieve_all_usernames()

                for username in usernames:
                    helper.remove_dir(constants.USERS_DIR + '/' + username)

                if len(usernames) > 0:
                    database.remove_all_users()
                database.close_connection()

    def __remove_all_tags(self):
        """ Remove all tags from the database and all tag output directories """

        answer = helper.yes_or_no('Are you sure you want to remove all tags?')
        if answer:
            if os.path.isfile(constants.LOCAL_DB):
                database = Database()
                tagnames = database.retrieve_all_tags()

                for tagname in tagnames:
                    helper.remove_dir(constants.TAGS_DIR + '/' + tagname)

                if len(tagnames) > 0:
                    database.remove_all_tags()
                database.close_connection()

    def __get_usernames_dict(self):
        """ Returns a dictionary with usernames, key starts at 1 """

        usernames_list = self.__get_all_usernames()
        usernames_dict = {v + 1: k for v, k in enumerate(usernames_list)}
        return usernames_dict

    def __get_tagnames_dict(self):
        """ Returns a dictionary with tags, key starts at 1 """

        tagnames_list = self.__get_all_tagnames()
        tags_dict = {v + 1: k for v, k in enumerate(tagnames_list)}
        return tags_dict

    def __get_current_webdriver_name(self):
        """ Get the name of the current webdriver to use """

        database = Database()
        webdriver_name = database.get_webdriver_name()
        database.close_connection()
        return webdriver_name

    def __choose_webdriver(self):
        """ Choose a webdriver to run the program """

        answer = helper.choose_options('Choose a web driver', constants.WEBDRIVERS)
        if answer == constants.CHROMEDRIVER:
            self.__download_chromedriver()
            self.__save_webdriver_name(constants.CHROMEDRIVER)
            self.webdriver_interface = constants.CHROMEDRIVER

    def __save_webdriver_name(self, webdriver_name):
        """ Save webdriver name in database """

        database = Database()
        database.set_webdriver_name(webdriver_name)
        database.close_connection()

    def __download_chromedriver(self):
        """ Download chromedriver if not found """

        download_completed = False

        for root, dirs, files in os.walk(constants.WEBDRIVERS_DIR):
            for file in files:
                if file[:len(constants.CHROMEDRIVER)] == constants.CHROMEDRIVER:
                    return

        helper.create_dir(constants.WEBDRIVERS_DIR)

        answer = helper.yes_or_no('Would you like to download chromedriver now?')
        if answer:
            driver_file_name = 'driver'
            version = constants.CHROMEDRIVER_VERSION

            if platform.system() == 'Linux':
                print('Downloading chromedriver-' + version + ': ')
                try:
                    wget.download(constants.CHROMEDRIVER_LINUX_URL,
                                  constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip')
                except HTTPError as err:
                    logger.error(err)
                    print('Download error.')
                    sys.exit(0)

                with zipfile.ZipFile(constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip', 'r') as zip_ref:
                    zip_ref.extractall(constants.WEBDRIVERS_DIR)
                    os.chmod(constants.WEBDRIVERS_DIR + '/' + constants.CHROMEDRIVER, 0o755)
                download_completed = True

            elif platform.system() == 'Windows':
                print('Downloading chromedriver-' + version + ': ')
                try:
                    wget.download(constants.CHROMEDRIVER_WINDOWS_URL,
                                  constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip')
                except HTTPError as err:
                    logger.error(err)
                    print('Download error.')
                    sys.exit(0)

                with zipfile.ZipFile(constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip', 'r') as zip_ref:
                    zip_ref.extractall(constants.WEBDRIVERS_DIR)
                    os.chmod(constants.WEBDRIVERS_DIR + '/' + constants.CHROMEDRIVER + '.exe', 0o755)
                download_completed = True

            elif platform.system() == 'Darwin':
                print('Downloading chromedriver-' + version + ': ')
                try:
                    wget.download(constants.CHROMEDRIVER_MACOS_URL,
                                  constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip')
                except HTTPError as err:
                    logger.error(err)
                    print('Download error.')
                    sys.exit(0)

                with zipfile.ZipFile(constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip', 'r') as zip_ref:
                    zip_ref.extractall(constants.WEBDRIVERS_DIR)
                    os.chmod(constants.WEBDRIVERS_DIR + '/' + constants.CHROMEDRIVER, 0o755)
                download_completed = True

        else:
            print('Manually download chromedriver ' + constants.CHROMEDRIVER_VERSION + ' and place the file in ' +
                  'working-directory/webdriver/chromedriver/')
            sys.exit(0)

        if download_completed:
            helper.remove_file(constants.WEBDRIVERS_DIR + '/' + driver_file_name + '.zip')
            print('\n' + self.__download_completed_str + '\n')


if __name__ == "__main__":
    main()
