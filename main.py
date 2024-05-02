import asyncio
import logging
from datetime import datetime

if __name__ == "__main__" or __name__ == "main":
    from crawler.cu_crawler import CUCrawler
    from crawler.emart24_crawler import Emart24Crawler
    from crawler.gs_crawler import GSCrawler
    from crawler.seven_eleven_crawler import SevenElevenCrawler
    from crawler.event_items import PromotionType
    from sql import AsyncSQL
else:
    from .crawler.cu_crawler import CUCrawler
    from .crawler.emart24_crawler import Emart24Crawler
    from .crawler.gs_crawler import GSCrawler
    from .crawler.seven_eleven_crawler import SevenElevenCrawler
    from .sql import AsyncSQL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_crawler(crawler):
    logger.info(f"Starting {crawler.__class__.__name__}")
    event_items = await crawler.execute()
    logger.info(
        f"Finished {crawler.__class__.__name__}, total items: {len(event_items)}"
    )
    return event_items


async def get_or_create_main_product(async_sql, name, image_url):
    select_query = "SELECT id FROM main_products WHERE name = %s"
    result = await async_sql.execute(select_query, name)

    if result:
        return result[0]["id"]
    else:
        insert_query = "INSERT INTO main_products (name, image_url) VALUES (%s, %s)"
        await async_sql.execute(insert_query, name, image_url)
        return await async_sql.execute("SELECT LAST_INSERT_ID()")[0]["LAST_INSERT_ID()"]


async def save_to_db(event_items):
    async with AsyncSQL() as async_sql:
        for item in event_items:
            main_product_id = await get_or_create_main_product(
                async_sql, item.name, item.image_url
            )
            insert_query = """
                INSERT INTO products (main_product_id, name, price, promotion, store, event_month)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            name = item.name
            price = item.price
            promotion = item.promotion_type.value
            store = item.store.value
            event_month = datetime.now().strftime("%Y-%m-01")

            await async_sql.execute(
                insert_query,
                main_product_id,
                name,
                price,
                promotion,
                store,
                event_month,
            )

        logging.info(f"Inserted {len(event_items)} items into the database")


async def main():
    crawlers = [
        SevenElevenCrawler(),
        CUCrawler(),
        Emart24Crawler(),
        GSCrawler(),
    ]

    tasks = []

    for crawler in crawlers:
        task = asyncio.create_task(run_crawler(crawler))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    all_items = [item for sublist in results for item in sublist]
    await save_to_db(all_items)

    total_items = sum(len(items) for items in results)
    logger.info(f"All crawlers finished, total items: {total_items}")


if __name__ == "__main__":
    asyncio.run(main())
