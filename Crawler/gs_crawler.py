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
    logging.basicConfig(level=logging.INFO)
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

    async def __fetch_data(self, session, parameter_list, page_num, max_retries=3):
        params = {
            "pageNum": page_num,
            "pageSize": 20,
            "parameterList": parameter_list,
        }
        retry_count = 0
        while retry_count < max_retries:
            try:
                async with session.get(self._base_url, params=params) as response:
                    if response.status == 200:
                        return json.loads(await response.json())
                    self.__logger.error(
                        f"Request failed with status code: {response.status}"
                    )
                    retry_count += 1
                    await asyncio.sleep(1)  # 1초 대기 후 재시도
            except aiohttp.ServerDisconnectedError as error:
                self.__logger(f"Server Disconnected: {str(error)}")
                retry_count += 1
                await asyncio.sleep(1)  # 1초 대기 후 재시도
            except aiohttp.ClientError as error:
                self.__logger(f"Request failed: {str(error)}")
                retry_count += 1
                await asyncio.sleep(1)  # 1초 대기 후 재시도
        raise Exception("Max retries exceed")

    async def execute(self):
        data_array = []

        async with aiohttp.ClientSession() as session:
            for parameter_list in self.__parameter_lists:
                page_num = 1
                while True:
                    json_data = await self.__fetch_data(
                        session, parameter_list, page_num
                    )
                    if "results" not in json_data:
                        self.__logger.debug("Finished parsing the data to the end")
                        break

                    event_items = await self.__parse_data(session, json_data)
                    data_array.extend(event_items)

                    total_pages = json_data["pagination"]["numberOfPages"]
                    if page_num >= total_pages:
                        break

                    page_num += 1

        self.__logger.info(f"Total data count: {len(data_array)}")
        return data_array


async def main():
    crawler = GSCrawler()
    items = await crawler.execute()


if __name__ == "__main__":
    asyncio.run(main())
