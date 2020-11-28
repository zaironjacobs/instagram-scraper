import logging
import json

from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError

from .. import constants
from .. import actions

logger = logging.getLogger('__name__')


class GetId(actions.Action):
    def __init__(self, scraper, username):
        super().__init__(scraper)
        self.__username = username

    def do(self):
        """ Get the id of a username """

        link = constants.INSTAGRAM_USER_INFO_URL_DEFAULT.format(self.__username)
        actions.GoToLink(self._scraper, link).do()
        result = self._scraper.web_driver.page_source
        soup = BeautifulSoup(result, 'html.parser')
        try:
            data = json.loads(soup.text)
            return data['graphql']['user']['id']
        except (JSONDecodeError, KeyError) as err:
            logger.error('could not retrieve user id: %s', str(err))

    def on_fail(self):
        pass
