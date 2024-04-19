import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType


class CUCrawler(Crawler):
    def __init__(self):
        self.__url = "https://cu.bgfretail.com/event/plusAjax.do"
        super().__init__()

    def __parse_data(self, html) -> list[EventItem]:
        soup = BeautifulSoup(html, "html.parser")
        event_items = []
        for li in soup.select("li.prod_list"):
            image_url = li.select_one(".prod_img img")["src"]
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
            print(event_item)
            event_items.append(event_item)
        return event_items

    async def __fetch_data(self, session, page_index, search_condition) -> str:
        data = {
            "pageIndex": page_index,
            "listType": 0,
            "searchCondition": search_condition,
        }
        async with session.post(self.__url, data=data) as response:
            return await response.text()

    async def execute(self) -> list[EventItem]:
        search_conditions = [23, 24]
        data_array = []

        async with aiohttp.ClientSession() as session:
            for search_condition in search_conditions:
                page_num = 1
                while True:
                    html = await self.__fetch_data(session, page_num, search_condition)
                    event_items = self.__parse_data(html)
                    if not event_items:
                        break
                    data_array.extend(event_items)

                    page_num += 1

        # 결과 출력
        print(f"Total data count: {len(data_array)}")
        return data_array


async def main():
    crawler = CUCrawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())