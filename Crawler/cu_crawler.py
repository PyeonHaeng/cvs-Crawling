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


class CUCrawler(Crawler):
    logging.basicConfig(level=logging.INFO)
    __logger = logging.getLogger(__name__)
    _base_url = "https://cu.bgfretail.com/event/plusAjax.do"
    __search_conditions = [23, 24]  # 1+1, 2+1

    async def __parse_data(
        self, session: aiohttp.ClientSession, html: str
    ) -> list[EventItem]:
        soup = BeautifulSoup(html, "html.parser")
        event_items = []
        for li in soup.select("li.prod_list"):
            image_url = li.select_one(".prod_img img")["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if not await self._is_valid_image(session, image_url):
                image_url = None
            name = li.select_one(".prod_text .name p").get_text(strip=True)
            price = int(
                li.select_one(".prod_text .price strong")
                .get_text(strip=True)
                .replace(",", "")
            )
            badge = li.select_one(".badge span")
            badge_text = badge.get_text(strip=True) if badge else ""

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
            for search_condition in self.__search_conditions:
                page_num = 1
                while True:
                    data = {
                        "pageIndex": page_num,
                        "listType": 0,
                        "searchCondition": search_condition,
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

        return data_array


async def main():
    crawler = CUCrawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
