import logging
import json
import time

from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError

from .. import constants
from .. import actions

logger = logging.getLogger('__name__')


class GetVidSrcUrl(actions.Action):
    def __init__(self, scraper, post_id, is_multiple, post_index=0):
        super().__init__(scraper)
        self.__post_id = post_id
        self.__is_multiple = is_multiple
        self.__post_index = post_index

    def do(self):
        """ Get the video source url """

        # Open new tab and load the link
        link = constants.INSTAGRAM_POST_INFO.format(self.__post_id)
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
            post_info = json.loads(soup.text)
            if self.__is_multiple:
                vid_url = post_info['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'][
                    self.__post_index]['node']['video_url']
                return vid_url
            else:
                vid_url = post_info['graphql']['shortcode_media']['video_url']
                return vid_url
        except (JSONDecodeError, KeyError) as err:
            logger.error('Unable to get video source url: %s' % str(err))

    def on_fail(self):
        pass
