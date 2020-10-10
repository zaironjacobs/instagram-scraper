import sys
import os
import logging

from instagram_scraper import helper
from instagram_scraper import Database
from instagram_scraper import constants

logger = logging.getLogger('__name__')


def remove_users_by_username(input_usernames):
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


def remove_tags_by_tagname(input_tags):
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


def remove_users_by_number(usernames_dict, input_numbers):
    """ Remove requested user(s) from the database and their output directory """

    input_numbers = sorted(set(input_numbers), key=lambda index: input_numbers.index(index))
    try:
        input_numbers = list(map(int, input_numbers))
    except ValueError as err:
        logger.error(err)
        print('Only numbers allowed.')
        sys.exit(0)

    database = Database()
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


def remove_tags_by_number(tags_dict, input_numbers):
    """ Remove requested tag(s) from the database and their output directory """

    input_numbers = sorted(set(input_numbers), key=lambda index: input_numbers.index(index))
    try:
        input_numbers = list(map(int, input_numbers))
    except ValueError as err:
        logger.error(err)
        print('Only numbers allowed.')
        sys.exit(0)

    database = Database()
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


def remove_all_users():
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


def remove_all_tags():
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
