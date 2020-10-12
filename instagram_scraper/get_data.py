import logging
import json

from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup

from instagram_scraper import Database
from instagram_scraper import constants

logger = logging.getLogger('__name__')


def get_all_usernames():
    """ Retrieve all usernames from database """

    database = Database()
    usernames = []
    db_usernames = database.retrieve_all_usernames()
    if len(db_usernames) > 0:
        for user in db_usernames:
            usernames.append(user)
    database.close_connection()
    return usernames


def get_all_tagnames():
    """ Retrieve all tags from database """

    database = Database()
    tags = []
    db_tags = database.retrieve_all_tags()
    if len(db_tags) > 0:
        for tag in db_tags:
            tags.append(tag)

    database.close_connection()
    return tags


def get_usernames_dict():
    """ Returns a dictionary with usernames, key starts at 1 """

    usernames_list = get_all_usernames()
    usernames_dict = {v + 1: k for v, k in enumerate(usernames_list)}
    return usernames_dict


def get_tagnames_dict():
    """ Returns a dictionary with tags, key starts at 1 """

    tagnames_list = get_all_tagnames()
    tags_dict = {v + 1: k for v, k in enumerate(tagnames_list)}
    return tags_dict


def get_id_by_username_from_db(username):
    database = Database()
    user_id = database.get_id_by_username(username)
    database.close_connection()
    return user_id


def get_id_by_username_from_ig(username):
    session = __retry_session(retries=5,
                              backoff_factor=0.1,
                              status_forcelist=[429, 500, 502, 503, 504],
                              method_whitelist=['GET'])
    result = session.get(constants.INSTAGRAM_USER_INFO_URL_DEFAULT.format(username))
    soup = BeautifulSoup(result.content, 'html.parser')

    try:
        data = json.loads(soup.text)
        return data['graphql']['user']['id']
    except (JSONDecodeError, KeyError) as err:
        logger.error('could not retrieve user id: %s', str(err))


def get_user_post_count(username):
    database = Database()
    post_count = database.get_user_post_count(username)
    database.close_connection()
    return post_count


def get_top_tag_post_count(tag):
    database = Database()
    post_count = database.get_top_tag_post_count(tag)
    database.close_connection()
    return post_count


def get_recent_tag_post_count(tag):
    database = Database()
    post_count = database.get_recent_tag_post_count(tag)
    database.close_connection()
    return post_count


def get_username_by_id(user_id):
    """ Return the username id """

    headers = {
        'user-agent': 'Instagram 155.0.0.37.107'
    }

    try:
        session = __retry_session(retries=5,
                                  backoff_factor=0.1,
                                  status_forcelist=[429, 500, 502, 503, 504],
                                  method_whitelist=['GET'])
        result = session.get(constants.INSTAGRAM_USER_INFO_URL_MOBILE.format(user_id), headers=headers)

    except (HTTPError, ConnectionError, Timeout, RequestException) as err:
        logger.error(err)

    else:

        if result.status_code == 200:

            try:
                user_info = result.json()
            except JSONDecodeError as err:
                logger.error('JSONDecodeError: %s', str(err))
            else:

                try:
                    username = user_info['user']['username']
                except KeyError as err:
                    logger.error(err)
                    logger.error('Unable to fetch username')
                else:
                    return username


def __retry_session(retries, backoff_factor, status_forcelist, method_whitelist):
    """ Retry session """

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist)

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
