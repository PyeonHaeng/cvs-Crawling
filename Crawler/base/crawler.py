from abc import ABC, abstractmethod


class Crawler(ABC):
    @property
    @abstractmethod
    def _url(self) -> str:
        pass

    @abstractmethod
    def execute(self):
        pass
