from selenium import webdriver
from abc import ABC, abstractmethod


class Crawler:
    def __init__(self):
        self._driver = webdriver.Chrome("./chromedriver")
        self._driver.implicitly_wait(3)

    def __del__(self):
        self._driver.quit()

    @abstractmethod
    def execute(self):
        pass
