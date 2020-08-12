import os
import sys
import re
import logging
import datetime

from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError

REQUESTS_TIMEOUT = 60
SESSION_RETRY = 2

logger = logging.getLogger('__name__')


def __retry_session(total):
    """ Retry session for requests """

    retry = Retry(
        total=total,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def save_image(img_url, output_user_posts_path, date_time=None, count=''):
    """ Save the Instagram image from url """

    try:
        session = __retry_session(total=SESSION_RETRY)
        res = session.get(url=img_url, timeout=REQUESTS_TIMEOUT)
    except HTTPError as err:
        logger.error(err)
    except ConnectionError as err:
        logger.error(err)
    except Timeout as err:
        logger.error(err)
    except RequestException as err:
        logger.error(err)
    else:
        file_extension = '.jpg'

        count = str(count)
        if count != '':
            count = '-' + count

        if date_time is not None:
            file_name = __get_datetime_str(date_time) + count + '__' + \
                        __get_img_file_name(img_url, res)
        else:
            file_name = __get_img_file_name(img_url, res) + count

        file_name += file_extension

        try:
            with open(output_user_posts_path + '/' + file_name, 'wb') as img_file:
                img_file.write(res.content)
            return True
        except EnvironmentError as err:
            logger.error(err)

    return False


def save_video(vid_url, output_user_posts_path, date_time=None, count=''):
    """ Save the Instagram video from url """

    try:
        session = __retry_session(total=SESSION_RETRY)
        res = session.get(url=vid_url, timeout=REQUESTS_TIMEOUT)
    except HTTPError as err:
        logger.error(err)
    except ConnectionError as err:
        logger.error(err)
    except Timeout as err:
        logger.error(err)
    except RequestException as err:
        logger.error(err)
    else:
        file_extension = '.mp4'

        count = str(count)
        if count != '':
            count = '-' + count

        if date_time is not None:
            file_name = __get_datetime_str(date_time) + count + '__' + \
                        __get_vid_file_name(vid_url, res)
        else:
            file_name = __get_vid_file_name(vid_url, res) + count

        file_name += file_extension

        try:
            with open(output_user_posts_path + '/' + file_name, 'wb') as vid_file:
                vid_file.write(res.content)
            return True
        except EnvironmentError as err:
            logger.error(err)

    return False


def __get_img_file_name(img_url, req):
    """ Get the image file name """

    if "Content-Disposition" in req.headers.keys():
        file_name = re.findall("filename=(.+)", req.headers["Content-Disposition"])[0]
    else:
        file_name = img_url.split("/")[-1]
    return file_name[:file_name.find('.jpg')].strip()


def __get_vid_file_name(vid_url, req):
    """ Get the video file name """

    if "Content-Disposition" in req.headers.keys():
        file_name = re.findall("filename=(.+)", req.headers["Content-Disposition"])[0]
    else:
        file_name = vid_url.split("/")[-1]
    return file_name[:file_name.find('.mp4')].strip()


def __get_datetime_str(date_time):
    """ Create a date/time string """

    date = datetime.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    date_format = "%Y_%m_%d_%H_%M_%S"
    return date.strftime(date_format)
