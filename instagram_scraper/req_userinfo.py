import os
import sys
import logging

from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from simplejson.errors import JSONDecodeError

logger = logging.getLogger('__name__')


def get_username_by_id(user_id):
    url = 'https://i.instagram.com/api/v1/users/{}/info/'

    headers = {
        'user-agent': 'Instagram 136.0.0.34.124'
    }

    try:
        session = __retry_session(retries=3,
                                  backoff_factor=0.1,
                                  status_forcelist=[429, 500, 502, 503, 504],
                                  method_whitelist=['GET'])
        res = session.get(url.format(user_id), timeout=15, headers=headers)
    except (HTTPError, ConnectionError, Timeout, RequestException) as err:
        logger.error(err)
    else:
        if res.status_code == 200:
            try:
                user_info = res.json()
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
    return None


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
