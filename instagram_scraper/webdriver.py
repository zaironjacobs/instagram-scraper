import os
import sys
import platform
import logging
from urllib.error import HTTPError

from instagram_scraper import constants

from get_chromedriver import GetChromeDriver

logger = logging.getLogger('__name__')


def download_chromedriver():
    """ Download chromedriver if not found """

    download_completed = False

    if platform.system() == 'Linux':
        get_driver = GetChromeDriver('linux')
        print('Downloading ChromeDriver ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
            os.chmod(constants.WEBDRIVER_DIR + '/' + constants.CHROMEDRIVER, 0o755)
        except HTTPError as err:
            logger.error(err)
            print('Download error.')
            sys.exit(0)
        download_completed = True

    elif platform.system() == 'Windows':
        get_driver = GetChromeDriver('win')
        print('Downloading ChromeDriver ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except HTTPError as err:
            logger.error(err)
            print('Download error.')
            sys.exit(0)
        download_completed = True

    elif platform.system() == 'Darwin':
        get_driver = GetChromeDriver('mac')
        print('Downloading ChromeDriver ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except HTTPError as err:
            logger.error(err)
            print('Download error.')
            sys.exit(0)
        download_completed = True

    if download_completed:
        print('Download completed.')
        sys.stdout.write('\n')


def chromedriver_present():
    __rename_folder()
    for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
        for file in files:
            if file[:len(constants.CHROMEDRIVER)] == constants.CHROMEDRIVER:
                return True
    return False


def __rename_folder():
    """ Name change """

    old_dir_name = 'webdrivers'
    if os.path.exists(old_dir_name):
        os.rename(old_dir_name, constants.WEBDRIVER_DIR)
