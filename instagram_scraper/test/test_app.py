import os
import shutil
import time
import pytest
import subprocess
import platform

from get_chrome_driver import GetChromeDriver

from .. import __version__
from .. import constants

name = 'igscraper'


class TestApp:

    #########################
    # WEBDRIVER FILE EXISTS #
    #########################
    def test_webdriver_file(self):
        get_driver = GetChromeDriver()
        release = get_driver.matching_version()

        process = subprocess.Popen([name, 'instagram', '--max', '1'],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        if platform.system() == 'Windows':
            file_path = constants.CHROMEDRIVER + '/' + release + '/' + 'bin' + '/' + constants.CHROMEDRIVER + '.exe'
        else:
            file_path = constants.CHROMEDRIVER + '/' + release + '/' + 'bin' + '/' + constants.CHROMEDRIVER

        result = os.path.isfile(file_path)
        assert result

    ###############################
    # USER DISPLAY PICTURE EXISTS #
    ###############################
    def test_user_display_file(self):
        process = subprocess.Popen([name, 'instagram', '--max', '1'],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        jpg_exists = False
        for file_name in os.listdir('users/instagram/display_photo'):
            if file_name.endswith('.jpg'):
                jpg_exists = True

        result = jpg_exists
        assert result

    #####################################
    # USER IMAGE/VIDEO POST FILE EXISTS #
    #####################################
    def test_user_posts_file(self):
        amount = '5'
        process = subprocess.Popen([name, 'instagram', '--max', amount],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        count = 0
        for file_name in os.listdir('users/instagram/posts'):
            if file_name.endswith('.jpg'):
                count += 1
            if file_name.endswith('.mp4'):
                count += 1

        result = count >= int(amount)
        assert result

    #######################################
    # RECENT TAG IMAGE/VIDEO FILE EXISTS #
    #######################################
    def test_recent_tags_file(self):
        amount = '5'
        process = subprocess.Popen([name, '--recent-tags', 'instagram', '--max', amount],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        count = 0
        for file_name in os.listdir('tags/instagram/recent'):
            if file_name.endswith('.jpg'):
                count += 1
            if file_name.endswith('.mp4'):
                count += 1

        result = count >= int(amount)
        assert result

    #######################################
    # TOP TAG IMAGE/VIDEO FILE EXISTS #
    #######################################
    def test_top_tags_file(self):
        amount = '5'
        process = subprocess.Popen([name, '--top-tags', 'instagram', '--max', amount],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        count = 0
        for file_name in os.listdir('tags/instagram/recent'):
            if file_name.endswith('.jpg'):
                count += 1
            if file_name.endswith('.mp4'):
                count += 1

        result = count >= int(amount)
        assert result

    ###########
    # VERSION #
    ###########
    def test_version(self):
        process = subprocess.Popen([name, '--version'], stdout=subprocess.PIPE)
        actual = process.stdout.readline().rstrip().decode('utf-8')
        assert 'v' + __version__ == str(actual)

    ###########
    # CLEANUP #
    ###########
    @pytest.fixture(scope='session', autouse=True)
    def cleanup(self):
        # Before all tests
        temp_dir = os.path.dirname(__file__) + '/' + 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        os.chdir(temp_dir)

        # After all tests
        yield
        time.sleep(3)
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(temp_dir)
