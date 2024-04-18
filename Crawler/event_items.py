from dataclasses import dataclass
from enum import Enum


class PromotionType(Enum):
    buy_one_get_one_free = "1+1"
    buy_two_get_one_free = "2+1"


@dataclass
class EventItem:
    promotion_type: PromotionType
    event_name: str
    price: int
    name: str
    image_url: str
