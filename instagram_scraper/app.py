import os
import sys
import argparse
import logging
from signal import signal, SIGINT

import colorama

from . import constants
from .scraper import Scraper
from .models.user import User
from .models.tag import Tag
from . import __version__
from . import helper
from . import webdriver
from . import remove_data
from . import update_data
from . import get_data
from . import arguments


def main():
    # noinspection PyUnusedLocal
    def signal_handler(signal_received, frame):
        """ Handles clean Ctrl+C exit """

        sys.stdout.write('\n')
        sys.exit(0)

    signal(SIGINT, signal_handler)
    App()


class App:

    def __init__(self):
        self.__init_logging()

        self.__c_fore = colorama.Fore
        self.__c_style = colorama.Style
        colorama.init()

        self.__message_no_db_found = 'no database found'
        self.__message_must_provide_tag = 'provide at least one tag'
        self.__msg_error_unrecognized_argument = (
                self.__c_fore.RED + 'error: unrecognized argument(s) detected' + self.__c_style.RESET_ALL
                + '\n' + 'tip: use --help to see all available arguments')

        self.__parser = argparse.ArgumentParser(add_help=False)
        self.__parser.add_argument('users', nargs='*')
        for i, arg in enumerate(arguments.args_options):
            self.__parser.add_argument(arguments.args_options[i][0], nargs='*')
        self.__args, self.__unknown = self.__parser.parse_known_args()

        if self.__unknown:
            print(self.__msg_error_unrecognized_argument)
            sys.exit(0)

        ###################
        # DEFAULT NO ARGS #
        ###################
        if len(sys.argv) == 1:
            arguments.print_help()
            sys.exit(0)

        ########
        # HELP #
        ########
        self.__arg_help = self.__args.help
        if self.__arg_passed(self.__arg_help):
            arguments.print_help()
            sys.exit(0)

        ########
        # LOG #
        ########
        self.__arg_log = self.__args.log
        if self.__arg_passed(self.__arg_log):
            open(constants.LOG_FILE, 'a').close()

        ###########
        # VERSION #
        ###########
        self.__arg_version = self.__args.version
        if self.__arg_passed(self.__arg_version):
            print('v' + __version__)
            sys.exit(0)

        ##############
        # LIST USERS #
        ##############
        self.__arg_list_users = self.__args.list_users
        if self.__arg_passed(self.__arg_list_users):
            if self.__is_db_present():
                self.__list_all_users()
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        #############
        # LIST TAGS #
        #############
        self.__arg_list_tags = self.__args.list_tags
        if self.__arg_passed(self.__arg_list_tags):
            if self.__is_db_present():
                self.__list_all_tags()
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        ################
        # REMOVE USERS #
        ################
        self.__arg_remove_users = self.__args.remove_users
        if self.__arg_passed(self.__arg_remove_users):
            if self.__is_db_present():
                remove_data.remove_users_by_username(self.__args.remove_users)
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        ###############
        # REMOVE TAGS #
        ###############
        self.__arg_remove_tags = self.__args.remove_tags
        if self.__arg_passed(self.__arg_remove_tags):
            if self.__is_db_present():
                remove_data.remove_tags_by_tagname(self.__arg_remove_tags)
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        #########################
        # REMOVE TAGS BY NUMBER #
        #########################
        self.__arg_remove_tags_n = self.__args.remove_tags_n
        if self.__arg_passed(self.__arg_remove_tags_n):
            if self.__is_db_present():
                remove_data.remove_tags_by_number(get_data.get_tagnames_dict(), self.__arg_remove_tags_n)
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        ##########################
        # REMOVE USERS BY NUMBER #
        ##########################
        self.__arg_remove_users_n = self.__args.remove_users_n
        if self.__arg_passed(self.__arg_remove_users_n):
            if self.__is_db_present():
                remove_data.remove_users_by_number(get_data.get_usernames_dict(), self.__arg_remove_users_n)
                sys.exit(0)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        ####################
        # REMOVE ALL USERS #
        ####################
        self.__arg_remove_all_users = self.__args.remove_all_users
        if self.__arg_passed(self.__arg_remove_all_users):
            remove_data.remove_all_users()
            sys.exit(0)

        ###################
        # REMOVE ALL TAGS #
        ###################
        self.__arg_remove_all_tags = self.__args.remove_all_tags
        if self.__arg_passed(self.__arg_remove_all_tags):
            remove_data.remove_all_tags()
            sys.exit(0)

        #######
        # MAX #
        #######
        self.__arg_max = self.__args.max
        if self.__arg_passed(self.__arg_max):
            try:
                if int(self.__arg_max[0]) < 1:
                    print('--max has to be 1 or greater')
                    sys.exit(0)
                max_download = int(self.__arg_max[0])
            except (ValueError, TypeError, IndexError):
                print('--max value has to be a number')
                sys.exit(0)
        else:
            max_download = 1000000000

        ###########
        # HEADFUL #
        ###########
        self.__arg_headful = self.__args.headful
        if self.__arg_passed(self.__arg_headful):
            headful = True
        else:
            headful = False

        ############
        # TOP TAGS #
        ############
        self.__top_tags = []
        self.__arg_top_tags = self.__args.top_tags
        if self.__arg_passed(self.__arg_top_tags):
            if len(self.__arg_top_tags) > 0:
                self.__top_tags = self.__create_tag_objects(self.__arg_top_tags)
            else:
                print(self.__message_must_provide_tag)
                sys.exit(0)

        ###############
        # RECENT TAGS #
        ###############
        self.__recent_tags = []
        self.__arg_recent_tags = self.__args.recent_tags
        if self.__arg_passed(self.__arg_recent_tags):
            if len(self.__arg_recent_tags) > 0:
                self.__recent_tags = self.__create_tag_objects(self.__arg_recent_tags)
            else:
                print(self.__message_must_provide_tag)
                sys.exit(0)

        if not webdriver.chromedriver_present():
            if helper.yes_or_no('would you like to download chromedriver now?'):
                webdriver.download_chromedriver()
                print('download completed')
                sys.stdout.write('\n')
            else:
                print('manually download the correct chromedriver for your current installed'
                      + ' chrome web browser and place the file in working-directory/'
                      + constants.WEBDRIVER_DIR)
                sys.exit(0)

        print('starting...')

        #########
        # USERS #
        #########
        self.__users = []
        self.__arg_users = self.__args.users
        if self.__arg_passed(self.__arg_users):
            if len(self.__arg_users) > 0:
                usernames_to_scrape = sorted(set(self.__arg_users), key=lambda index: self.__arg_users.index(index))
                self.__users = self.__create_user_objects(usernames_to_scrape)

        ################
        # UPDATE USERS #
        ################
        self.__arg_update_users = self.__args.update_users
        if self.__arg_passed(self.__arg_update_users):
            if self.__is_db_present():
                usernames_to_scrape = get_data.get_all_usernames()
                if len(usernames_to_scrape) == 0:
                    print('database has no users to update.')
                    sys.exit(0)
                self.__users = self.__create_user_objects(usernames_to_scrape)
            else:
                print(self.__message_no_db_found)
                sys.exit(0)

        ##################
        # LOGIN USERNAME #
        ##################
        self.__arg_login_username = self.__args.login_username
        if self.__arg_passed(self.__arg_login_username):
            login_username = self.__arg_login_username[0]
        else:
            login_username = None

        if len(self.__users) == 0 and len(self.__top_tags) == 0 and len(self.__recent_tags) == 0:
            print('provide at least one username or tag to scrape.')
            sys.exit(0)

        self.__scraper = Scraper(headful, max_download, login_username)

        if len(self.__users) > 0:
            self.__scraper.init_scrape_users(self.__users)
        if len(self.__top_tags) > 0:
            self.__scraper.init_scrape_tags(self.__top_tags, constants.TAG_TYPE_TOP)
        if len(self.__recent_tags) > 0:
            self.__scraper.init_scrape_tags(self.__recent_tags, constants.TAG_TYPE_RECENT)

        self.__scraper.stop()

    def __arg_passed(self, arg):
        if isinstance(arg, list):
            return True
        return False

    def __init_logging(self):
        """ Initialize logging if igscraper.log is present """

        logger = logging.getLogger('__name__')
        if os.path.exists(constants.LOG_FILE):
            logger.setLevel(logging.DEBUG)
            logger_file_handler = logging.FileHandler(constants.LOG_FILE)
            logger_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            logger_file_handler.setFormatter(logger_formatter)
            logger.addHandler(logger_file_handler)
        else:
            logger.disabled = True

    def __is_db_present(self):
        if os.path.isfile(constants.LOCAL_DB):
            return True
        return False

    def __create_user_objects(self, usernames_to_scrape):
        """ Create user objects """

        users = []
        for input_username in usernames_to_scrape:
            input_username = input_username.lower()
            input_username = self.__check_if_username_has_changed(input_username)
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

    def __check_if_username_has_changed(self, input_username):
        """ If user has a new username, update it in the database and rename the user dir """

        user_id = get_data.get_id_by_username_from_db(input_username)
        if user_id:
            username = get_data.get_username_by_id(user_id)
            if username:
                if input_username != username:
                    update_data.rename_user(user_id, username)
                    helper.rename_user_dir(input_username, username)
                    return username
        return input_username

    def __list_all_users(self):
        """ List all users in the database """

        usernames_dict = get_data.get_usernames_dict()
        if len(usernames_dict) > 0:
            first_str = 'user'
            second_str = 'posts scraped'
            descriptor = '{:<40} {}'
            print('')
            print(descriptor.format(first_str, second_str))
            print(descriptor.format(len(first_str) * '-', len(second_str) * '-'))
            for number, username in usernames_dict.items():
                space_str = ' ' if len(str(number)) > 1 else '  '
                first = '[' + space_str + str(number) + '] ' + username
                second = str(get_data.get_user_post_count(username))
                print(descriptor.format(first, second))
        else:
            print('no users found in the database')

    def __list_all_tags(self):
        """ List all tags in the database """

        tags_dict = get_data.get_tagnames_dict()
        if len(tags_dict) > 0:
            first_str = 'tag'
            second_str = 'top posts scraped'
            third_str = 'recent posts scraped'
            descriptor = '{:<40} {:<20} {}'
            print('')
            print(descriptor.format(first_str, second_str, third_str))
            print(descriptor.format(len(first_str) * '-', len(second_str) * '-',
                                    len(third_str) * '-'))
            for number, tag in tags_dict.items():
                space_str = ' ' if len(str(number)) > 1 else '  '
                first = '[' + space_str + str(number) + '] ' + tag
                second = str(get_data.get_top_tag_post_count(tag))
                third = str(get_data.get_recent_tag_post_count(tag))
                print(descriptor.format(first, second, third))
        else:
            print('no tags found in the database')

