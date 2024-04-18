if __name__ == "__main__" or __name__ == "Crawler":
    from base.crawler import Crawler
    from event_items import EventItem
    from event_items import PromotionType
else:
    from .base.crawler import Crawler
    from .event_items import EventItem
    from .event_items import PromotionType

import requests
import json


class GSCrawler(Crawler):
    def __init__(self):
        self.__url = "http://gs25.gsretail.com/gscvs/ko/products/event-goods-search"
        super().__init__()

    def parse_data(self):
        pass

    def execute(self):
        parameter_lists = ["ONE_TO_ONE", "TWO_TO_ONE"]
        page_size = 20
        data_array = []

        for parameter_list in parameter_lists:
            page_num = 1
            while True:
                params = {
                    "pageNum": page_num,
                    "pageSize": page_size,
                    "parameterList": parameter_list,
                }
                response = requests.get(self.__url, params=params)

                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    break

                # 받아온 데이터를 문자열로 변환
                json_string = response.json()

                # JSON 형식으로 변환
                json_data = json.loads(json_string)

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

                    data_array.append(event_item)
                    print(event_item)

                total_pages = json_data["pagination"]["numberOfPages"]
                if page_num >= total_pages:
                    break

                page_num += 1

        # 결과 출력
        print(f"Total data count: {len(data_array)}")
        print(data_array)


if __name__ == "__main__":
    crawler = GSCrawler()
    crawler.execute()
