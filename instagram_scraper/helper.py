import os
import shutil
import logging
import datetime
import re

from . import constants

logger = logging.getLogger('__name__')


def yes_or_no(question):
    """ Returns True for yes or False for no """

    yes_answer = ['y', 'yes']
    no_answer = ['n', 'no']
    while True:
        user_input = input(question + ' [Y/n] ').lower()
        if user_input in yes_answer:
            return True
        elif user_input in no_answer:
            return False
        else:
            print('Answer with yes or no.')


def choose_options(question, options):
    """ Returns the chosen option """

    options_dict = {}
    for i, option in enumerate(options):
        number = str(i + 1)
        options_dict.update({number: option})
        print('[ ' + number + '] ' + option)

    options_dict = dict((k, v.lower()) for k, v in options_dict.items())
    while True:
        user_input = input(question + ': ').lower()
        if user_input in options_dict.keys():
            return options_dict.get(user_input)
        if user_input in options_dict.values():
            return user_input
        else:
            print('Invalid answer, choose one value from the options.')


def create_dir(directory):
    """ Create a directory
    """

    try:
        os.makedirs(directory)
    except FileExistsError:
        return True
    except OSError as err:
        logger.error(err)
        return False
    else:
        return True


def remove_dir(directory):
    """ Remove a directory """

    try:
        if os.path.isdir(directory):
            shutil.rmtree(directory)
    except OSError as err:
        logger.error(err)
        return False
    else:
        return True


def remove_file(file):
    """ Remove a file """

    try:
        if os.path.isfile(file):
            os.remove(file)
    except OSError as err:
        logger.error(err)
        return False
    else:
        return True


def rename_dir(old_directory_name, new_directory_name):
    """ Rename a directory """

    try:
        os.rename(old_directory_name, new_directory_name)
    except OSError as err:
        logger.error(err)
        return False
    else:
        return True


def rename_user_dir(old_directory_name, new_directory_name):
    """ Rename user directory """

    try:
        os.rename(constants.USERS_DIR + '/' + old_directory_name, constants.USERS_DIR + '/' + new_directory_name)
    except OSError as err:
        logger.error(err)
        return False
    else:
        return True


def get_datetime_str(date_time):
    """ Create a date-time string """

    date = datetime.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    date_format = "%Y_%m_%d_%H_%M_%S"
    return date.strftime(date_format)


def extract_post_id_from_url(url):
    """ Return the post id """

    post_id = re.search('/p/(.+)', url)
    if post_id:
        if post_id.group(1)[-1] == '/':
            return post_id.group(1)[:-1]
        return post_id.group(1)

    logger.error('Could not extract the post id')
    return ''
