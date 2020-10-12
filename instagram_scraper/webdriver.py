import os
import sys
import platform
import logging

from get_chromedriver import GetChromeDriver
from get_chromedriver.exceptions import GetChromeDriverError

from instagram_scraper import constants
from instagram_scraper import helper

logger = logging.getLogger('__name__')


def download_chromedriver():
    """ Download chromedriver if not found """

    download_error = 'download error'
    downloading_chromedriver = 'downloading ChromeDriver'

    if platform.system() == 'Linux':
        get_driver = GetChromeDriver('linux')
        print(downloading_chromedriver + ' ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
            os.chmod(constants.WEBDRIVER_DIR + '/' + constants.CHROMEDRIVER, 0o755)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)

    elif platform.system() == 'Windows':
        get_driver = GetChromeDriver('win')
        print(downloading_chromedriver + ' ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)

    elif platform.system() == 'Darwin':
        get_driver = GetChromeDriver('mac')
        print(downloading_chromedriver + ' ' + get_driver.latest_stable_release_version() + '...')
        try:
            get_driver.download_latest_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)


def chromedriver_present():
    helper.rename_dir('webdrivers', constants.WEBDRIVER_DIR)
    for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
        for file in files:
            if file[:len(constants.CHROMEDRIVER)] == constants.CHROMEDRIVER:
                return True
    return False
