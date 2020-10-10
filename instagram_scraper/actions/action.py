from abc import ABCMeta, abstractmethod


class Action:
    __metaclass__ = ABCMeta

    def __init__(self, scraper):
        self._scraper = scraper
        self._web_driver = scraper.web_driver

    @abstractmethod
    def do(self): raise NotImplementedError

    @abstractmethod
    def on_fail(self): raise NotImplementedError
