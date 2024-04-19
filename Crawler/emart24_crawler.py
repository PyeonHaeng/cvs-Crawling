import aiohttp
import asyncio
from bs4 import BeautifulSoup

if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType


class Emart24Crawler(Crawler):
    def __init__(self):
        self.__url = "https://emart24.co.kr/goods/event"
        super().__init__()

    def __parse_data(self, html) -> list[EventItem]:
        soup = BeautifulSoup(html, "html.parser")
        event_items = []
        for div in soup.select("div.itemWrap"):
            image_url = div.select_one(".itemImg img")["src"]
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
            print(event_item)
            event_items.append(event_item)
        return event_items

    async def __fetch_data(self, session, page, category_seq) -> str:
        params = {
            "page": page,
            "category_seq": category_seq,
        }
        async with session.get(self.__url, params=params) as response:
            return await response.text()

    async def execute(self) -> list[EventItem]:
        category_seqs = [1, 2]  # 1+1, 2+1 각각 가져오기
        data_array = []

        async with aiohttp.ClientSession() as session:
            for category_seq in category_seqs:
                page_num = 1
                while True:
                    html = await self.__fetch_data(session, page_num, category_seq)
                    event_items = self.__parse_data(html)
                    if not event_items:
                        break
                    data_array.extend(event_items)

                    page_num += 1

        # 결과 출력
        print(f"Total data count: {len(data_array)}")
        return data_array


async def main():
    crawler = Emart24Crawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
