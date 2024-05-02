from dataclasses import dataclass
from enum import Enum


class PromotionType(Enum):
    buy_one_get_one_free = "BUY_ONE_GET_ONE_FREE"
    buy_two_get_one_free = "BUY_TWO_GET_ONE_FREE"


class ConvenienceStoreType(Enum):
    gs25 = "GS25"
    seven_eleven = "SEVEN_ELEVEN"
    cu = "CU"
    emart24 = "EMART24"


@dataclass
class EventItem:
    promotion_type: PromotionType
    store: ConvenienceStoreType
    event_name: str
    price: int
    name: str
    image_url: str
