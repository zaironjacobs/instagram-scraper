import os
import shutil
import pytest
import subprocess
import platform

from instagram_scraper import constants
from app_info import __app_version__
from app_info import __app_name__

# Change to the current test directory
os.chdir(os.path.dirname(__file__))


class TestApp:

    #########################
    # WEBDRIVER FILE EXISTS #
    #########################
    def test_webdriver_file(self):
        process = subprocess.Popen([__app_name__, 'instagram', '--max', '1'],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.communicate('yes'.encode())[0].rstrip()

        if platform.system() == 'Windows':
            file_path = 'webdriver/chromedriver.exe'
        else:
            file_path = 'webdriver/chromedriver'

        result = os.path.isfile(file_path)
        assert result

    ###############################
    # USER DISPLAY PICTURE EXISTS #
    ###############################
    def test_user_display_file(self):
        process = subprocess.Popen([__app_name__, 'instagram', '--max', '1'],
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
        process = subprocess.Popen([__app_name__, 'instagram', '--max', amount],
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
        process = subprocess.Popen([__app_name__, '--recent-tags', 'instagram', '--max', amount],
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
        process = subprocess.Popen([__app_name__, '--top-tags', 'instagram', '--max', amount],
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
        process = subprocess.Popen([__app_name__, '--version'], stdout=subprocess.PIPE)
        actual = process.stdout.readline().rstrip().decode('utf-8')
        assert 'v' + __app_version__ == str(actual)

    ###########
    # CLEANUP #
    ###########
    @pytest.fixture(scope='session', autouse=True)
    def cleanup(self):
        yield
        try:
            shutil.rmtree(constants.USERS_DIR)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(constants.TAGS_DIR)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(constants.WEBDRIVER_DIR)
        except FileNotFoundError:
            pass
        try:
            os.remove(constants.LOCAL_DB)
        except FileNotFoundError:
            pass
        try:
            os.remove(constants.LOG_FILE)
        except FileNotFoundError:
            pass
