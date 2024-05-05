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
        last_id_result = await async_sql.execute("SELECT LAST_INSERT_ID()")
        return last_id_result[0]["LAST_INSERT_ID()"]


async def product_exists(
    async_sql, main_product_id, name, price, promotion, store, event_date
) -> bool:
    select_query = "SELECT COUNT(*) as count FROM products WHERE main_product_id = %s AND name = %s AND price = %s AND promotion = %s AND store = %s AND event_date = %s"
    result = await async_sql.execute(
        select_query, main_product_id, name, price, promotion, store, event_date
    )
    return result[0]["count"] > 0


async def save_to_db(event_items):
    # 로깅용 변수
    inserted_count = 0
    skipped_count = 0
    try:
        async with AsyncSQL() as async_sql:
            for item in event_items:
                main_product_id = await get_or_create_main_product(
                    async_sql, item.name, item.image_url
                )

                name = item.name
                price = item.price
                promotion = item.promotion_type.value
                store = item.store.value
                event_date = datetime.now().strftime("%Y-%m-01")

                if await product_exists(
                    async_sql,
                    main_product_id,
                    name,
                    price,
                    promotion,
                    store,
                    event_date,
                ):
                    logging.info(f"Skipping duplicate item: {name} ({store})")
                    skipped_count += 1
                    continue

                insert_query = """
                    INSERT INTO products (main_product_id, name, price, promotion, store, event_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                await async_sql.execute(
                    insert_query,
                    main_product_id,
                    name,
                    price,
                    promotion,
                    store,
                    event_date,
                )
                inserted_count += 1

                insert_back_up_query = """
                    INSERT INTO back_up (name, image_url, price, store, promotion, event_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                await async_sql.execute(
                    insert_back_up_query,
                    name,
                    item.image_url,
                    price,
                    store,
                    promotion,
                    event_date,
                )

            logging.info(f"Inserted {inserted_count} items into the database")
            logging.info(f"Skipped {skipped_count} duplicate items")
    except Exception as e:
        logging.error(f"Error occurred while saving to the database: {str(e)}")
        raise e


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
