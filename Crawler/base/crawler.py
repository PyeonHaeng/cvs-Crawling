from abc import ABC, abstractmethod
import aiohttp


class Crawler(ABC):
    """
    크롤러의 추상 기본 클래스입니다.

    이 클래스는 크롤링 작업을 위한 기본 구조와 유틸리티 메서드를 제공합니다.
    서브클래스에서는 `_url` 속성과 `execute` 메서드를 구현해야 합니다.

    Attributes:
        _url (str): 크롤링할 대상 URL을 나타내는 추상 속성입니다.

    Methods:
        execute(): 크롤링 작업을 수행하는 추상 메서드입니다.
        _is_valid_image(session, image_url): 주어진 이미지 URL이 유효한 이미지인지 확인하는 비동기 유틸리티 메서드입니다.
    """

    @property
    @abstractmethod
    def _url(self) -> str:
        """
        크롤링할 대상 URL을 나타내는 추상 속성입니다.

        서브클래스에서 이 속성을 구현하여 크롤링할 URL을 지정해야 합니다.

        Returns:
            str: 크롤링할 대상 URL.
        """
        pass

    @abstractmethod
    def execute(self):
        """
        크롤링 작업을 수행하는 추상 메서드입니다.

        서브클래스에서 이 메서드를 구현하여 실제 크롤링 작업을 수행해야 합니다.
        """
        pass

    async def _is_valid_image(
        self, session: aiohttp.ClientSession, image_url: str
    ) -> bool:
        """
        주어진 이미지 URL이 유효한 이미지인지 확인하는 비동기 유틸리티 메서드입니다.

        Parameters:
            session (aiohttp.ClientSession): aiohttp 클라이언트 세션 객체.
            image_url (str): 확인할 이미지 URL.

        Returns:
            bool: 이미지 URL이 유효한 경우 True, 그렇지 않은 경우 False.
        """
        try:
            async with session.get(image_url) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type")
                    if content_type and content_type.startswith("image/"):
                        return True
        except aiohttp.ClientError:
            pass
        return False
