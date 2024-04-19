import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging

if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType


class SevenElevenCrawler(Crawler):
    logging.basicConfig(level=logging.INFO)
    __logger = logging.getLogger(__name__)
    _base_url = "https://www.7-eleven.co.kr/product/listMoreAjax.asp"
    __promotion_conditions = [1, 2]  # 1+1, 2+1

    async def __parse_data(
        self, session: aiohttp.ClientSession, html: str
    ) -> list[EventItem]:
        soup = BeautifulSoup(html, "html.parser")
        event_items = []
        for li in soup.select("li"):
            promotion_type = None
            badge = li.select_one(".tag_list_01 li")
            if badge is None:
                continue

            badge_text = badge.get_text(strip=True)
            if badge_text == "1+1":
                promotion_type = PromotionType.buy_one_get_one_free
            elif badge_text == "2+1":
                promotion_type = PromotionType.buy_two_get_one_free

            if promotion_type is None:
                continue

            image_url = (
                "https://www.7-eleven.co.kr" + li.select_one(".pic_product img")["src"]
            )
            if not await self._is_valid_image(session, image_url):
                image_url = None

            name = li.select_one(".tit_product").get_text(strip=True)
            price_element = li.select(".price_list span:not(.hide)")
            if len(price_element) > 1:
                price = int(price_element[1].get_text(strip=True).replace(",", ""))
            elif len(price_element) == 1:
                price = int(price_element[0].get_text(strip=True).replace(",", ""))
            else:
                raise ValueError

            event_item = EventItem(
                promotion_type=promotion_type,
                event_name=name,
                price=price,
                name=name,
                image_url=image_url,
            )
            event_items.append(event_item)

        return event_items

    async def execute(self) -> list[EventItem]:
        data_array = []

        async with aiohttp.ClientSession() as session:
            for promotion_condition in self.__promotion_conditions:
                page_num = 1
                while True:
                    data = {
                        "intCurrPage": page_num,
                        "intPageSize": 20,
                        "pTab": promotion_condition,
                    }
                    html = await self._fetch_data(
                        session, self._base_url, "POST", data=data
                    )
                    event_items = await self.__parse_data(session, html)

                    if not event_items:
                        self.__logger.debug("Finished parsing the data to the end")
                        break
                    data_array.extend(event_items)

                    page_num += 1

        self.__logger.info(f"Total data count: {len(data_array)}")
        return data_array


async def main():
    crawler = SevenElevenCrawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
