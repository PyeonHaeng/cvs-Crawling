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


class Emart24Crawler(Crawler):
    logging.basicConfig(level=logging.INFO)
    __logger = logging.getLogger(__name__)
    _base_url = "https://emart24.co.kr/goods/event"
    __category_seqs = [1, 2]  # 1+1, 2+1 각각 가져오기

    async def __parse_data(
        self, session: aiohttp.ClientSession, html
    ) -> list[EventItem]:
        soup = BeautifulSoup(html, "html.parser")
        event_items = []
        for div in soup.select("div.itemWrap"):
            image_url = div.select_one(".itemImg img")["src"]
            if not await self._is_valid_image(session, image_url):
                image_url = None
            name = div.select_one(".itemtitle p a").get_text(strip=True)
            price = int(
                div.select_one(".price")
                .get_text(strip=True)
                .replace(",", "")
                .replace("원", "")
            )
            badge = div.select_one(".onepl")
            badge_text = badge.get_text(strip=True).replace(" ", "") if badge else ""

            event_item = EventItem(
                promotion_type=(
                    PromotionType.buy_one_get_one_free
                    if badge_text == "1+1"
                    else PromotionType.buy_two_get_one_free
                ),
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
            for category_seq in self.__category_seqs:
                page_num = 1
                while True:
                    params = {
                        "page": page_num,
                        "category_seq": category_seq,
                    }

                    html = await self._fetch_data(
                        session, self._base_url, params=params
                    )
                    event_items = await self.__parse_data(session, html)

                    if not event_items:
                        self.__logger.debug("Finished parsing the data to the end")
                        break
                    data_array.extend(event_items)

                    page_num += 1

        return data_array


async def main():
    crawler = Emart24Crawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
