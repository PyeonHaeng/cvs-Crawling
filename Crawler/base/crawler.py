from selenium import webdriver
from abc import ABC, abstractmethod
import platform
import os


class Crawler(ABC):
    def __init__(self):
        self._driver = self.initialize_driver()

    def initialize_driver(self):
        operating_system = platform.system()
        chromedriver_path = os.path.join(os.path.dirname(__file__), "chromedriver")

        if operating_system == "Darwin":  # M1 MacBook
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless")
            return webdriver.Chrome(options=options)
        elif operating_system == "Windows":  # Windows
            chromedriver_path += ".exe"
            return webdriver.Chrome(executble_path=chromedriver_path)
        else:
            raise Exception(f"Unsupported operating system: {operating_system}")

    def __del__(self):
        self._driver.quit()

    @abstractmethod
    def execute(self):
        pass
