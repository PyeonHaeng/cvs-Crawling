import aiohttp
import asyncio
import json
import logging

if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType


class GSCrawler(Crawler):
    __logger = logging.getLogger(__name__)
    _base_url = "http://gs25.gsretail.com/gscvs/ko/products/event-goods-search"
    __parameter_lists = ["ONE_TO_ONE", "TWO_TO_ONE"]

    async def __parse_data(
        self, session: aiohttp.ClientSession, json_data
    ) -> list[EventItem]:
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
                image_url=(
                    item["attFileNm"]
                    if await self._is_valid_image(session, item["attFileNm"])
                    else None
                ),
            )
            event_items.append(event_item)
        return event_items

    async def execute(self):
        data_array = []

        async with aiohttp.ClientSession() as session:
            for parameter_list in self.__parameter_lists:
                page_num = 1
                while True:
                    params = {
                        "pageNum": page_num,
                        "pageSize": 20,
                        "parameterList": parameter_list,
                    }
                    json_data = json.loads(
                        await self._fetch_data(session, self._base_url, params=params)
                    )
                    event_items = await self.__parse_data(session, json_data)

                    if not event_items:
                        self.__logger.debug("Finished parsing the data to the end")
                        break
                    data_array.extend(event_items)

                    total_pages = json_data["pagination"]["numberOfPages"]
                    if page_num >= total_pages:
                        break
                    self.__logger.debug(f"PageNumber Increasing... {page_num}")
                    page_num += 1
                self.__logger.debug(f"GS: {parameter_list} Done.")

        return data_array


async def main():
    crawler = GSCrawler()
    items = await crawler.execute()
    print(len(items))


if __name__ == "__main__":
    asyncio.run(main())
