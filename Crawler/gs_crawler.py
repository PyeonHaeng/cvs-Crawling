import aiohttp
import asyncio
import json

if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType


class GSCrawler(Crawler):
    def __init__(self):
        self.__url = "http://gs25.gsretail.com/gscvs/ko/products/event-goods-search"
        super().__init__()

    def __parse_data(self, json_data) -> list[EventItem]:
        event_items = []
        for item in json_data["results"]:
            event_item = EventItem(
                promotion_type=(
                    PromotionType.buy_one_get_one_free
                    if item["eventTypeNm"] == "1+1"
                    else PromotionType.buy_two_get_one_free
                ),
                event_name=item["goodsNm"],
                price=item["price"],
                name=item["abrGoodsNm"],
                image_url=item["attFileNm"],
            )
            event_items.append(event_item)
        return event_items

    async def __fetch_data(self, session, parameter_list, page_num, page_size):
        params = {
            "pageNum": page_num,
            "pageSize": page_size,
            "parameterList": parameter_list,
        }
        async with session.get(self.__url, params=params) as response:
            return await json.loads(response.json())

    async def execute(self):
        parameter_lists = ["ONE_TO_ONE", "TWO_TO_ONE"]
        page_size = 20
        data_array = []

        async with aiohttp.ClientSession() as session:
            for parameter_list in parameter_lists:
                page_num = 1
                while True:
                    json_data = await self.__fetch_data(
                        session, parameter_list, page_num, page_size
                    )
                    if "results" not in json_data:
                        print("Error: Invalid response")
                        break

                    event_items = self.__parse_data(json_data)
                    data_array.extend(event_items)

                    total_pages = json_data["pagination"]["numberOfPages"]
                    if page_num >= total_pages:
                        break

                    page_num += 1

        # 결과 출력
        print(f"Total data count: {len(data_array)}")
        return data_array


async def main():
    crawler = GSCrawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
