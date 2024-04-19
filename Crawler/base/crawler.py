from abc import ABC, abstractmethod
import aiohttp
import asyncio
import logging


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

    logging.basicConfig(level=logging.DEBUG)
    __logger = logging.getLogger(__name__)

    @property
    @abstractmethod
    def _base_url(self) -> str:
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

    async def _fetch_data(
        self, session: aiohttp.ClientSession, url: str, method: str = "GET", **kwargs
    ):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with getattr(session, method.lower())(url, **kwargs) as response:
                    if response.status == 200:
                        if "json" in response.headers.get("Content-Type", ""):
                            return await response.json()
                        else:
                            return await response.text()
                    self.__logger.error(
                        f"Request failed with status code: {response.status}"
                    )
                    retry_count += 1
                    await asyncio.sleep(1)  # 1초 대기 후 재시도
            except BaseException as error:
                self.__logger.error(f"URL Response Failed: {str(error)}")
                retry_count += 1
                await asyncio.sleep(1)  # 1초 대기 후 재시도

        raise Exception("Max retries exceed")

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

        max_retries = 3
        retry_count = 0
        timeout = aiohttp.ClientTimeout(total=10)  # 10초 시간 초과 설정

        while retry_count < max_retries:
            try:
                async with session.get(image_url, timeout=timeout) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type")
                        if content_type and content_type.startswith("image/"):
                            return True
                    return False
            except (
                aiohttp.ClientError,
                asyncio.exceptions.TimeoutError,
                asyncio.exceptions.CancelledError,
            ) as e:
                self.__logger.error(f"Error checking image URL: {image_url}, {str(e)}")
                retry_count += 1
                await asyncio.sleep(1)  # 1초 대기 후 재시도
        return False
