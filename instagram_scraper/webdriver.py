import os
import sys
import platform
import logging

from get_chrome_driver import GetChromeDriver
from get_chrome_driver.exceptions import GetChromeDriverError

from . import constants
from . import helper

logger = logging.getLogger('__name__')


def download_chromedriver():
    """ Download chromedriver if not found """

    download_error = 'download error'
    downloading_chromedriver = 'downloading ChromeDriver'

    if platform.system() == 'Linux':
        get_driver = GetChromeDriver('linux')
        print(downloading_chromedriver + ' ' + get_driver.stable_release_version() + '...')
        try:
            get_driver.download_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
            os.chmod(constants.WEBDRIVER_DIR + '/' + constants.CHROMEDRIVER, 0o755)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)

    elif platform.system() == 'Windows':
        get_driver = GetChromeDriver('win')
        print(downloading_chromedriver + ' ' + get_driver.stable_release_version() + '...')
        try:
            get_driver.download_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)

    elif platform.system() == 'Darwin':
        get_driver = GetChromeDriver('mac')
        print(downloading_chromedriver + ' ' + get_driver.stable_release_version() + '...')
        try:
            get_driver.download_stable_release(output_path=constants.WEBDRIVER_DIR, extract=True)
        except GetChromeDriverError as err:
            logger.error(err)
            print(download_error)
            sys.exit(0)


def chromedriver_present():
    try:
        helper.rename_dir('webdrivers', constants.WEBDRIVER_DIR)
    except OSError:
        pass
    for root, dirs, files in os.walk(constants.WEBDRIVER_DIR):
        for file in files:
            if file[:len(constants.CHROMEDRIVER)] == constants.CHROMEDRIVER:
                return True
    return False
