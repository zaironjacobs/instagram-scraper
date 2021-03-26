import logging
import json
import time

from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError

from .. import constants
from .. import actions

logger = logging.getLogger('__name__')


class GetUserId(actions.Action):
    def __init__(self, scraper, username):
        super().__init__(scraper)
        self.__username = username

    def do(self):
        """ Get the id of a username """

        # Open new tab and load the link
        link = constants.INSTAGRAM_USER_INFO_URL_DEFAULT.format(self.__username)
        self._web_driver.execute_script("window.open('" + link + "','_blank');")
        first_tab_handle = self._web_driver.current_window_handle

        # Switch to the new tab
        self._web_driver.switch_to.window(self._web_driver.window_handles[1])
        time.sleep(2)

        # Get data
        result = self._scraper.web_driver.page_source
        soup = BeautifulSoup(result, 'html.parser')

        # Close the the new tab
        self._web_driver.close()
        self._web_driver.switch_to.window(first_tab_handle)
        time.sleep(2)

        try:
            data = json.loads(soup.text)
            return data['graphql']['user']['id']
        except (JSONDecodeError, KeyError) as err:
            logger.error('could not retrieve user id: %s' % str(err))

    def on_fail(self):
        pass
