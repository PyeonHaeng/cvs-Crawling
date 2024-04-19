import asyncio
import logging

if __name__ == "__main__" or __name__ == "Crawler":
    from crawler.cu_crawler import CUCrawler
    from crawler.emart24_crawler import Emart24Crawler
    from crawler.gs_crawler import GSCrawler
    from crawler.seven_eleven_crawler import SevenElevenCrawler
else:
    from .crawler.cu_crawler import CUCrawler
    from .crawler.emart24_crawler import Emart24Crawler
    from .crawler.gs_crawler import GSCrawler
    from .crawler.seven_eleven_crawler import SevenElevenCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_crawler(crawler):
    logger.info(f"Starting {crawler.__class__.__name__}")
    event_items = await crawler.execute()
    logger.info(
        f"Finished {crawler.__class__.__name__}, total items: {len(event_items)}"
    )
    return event_items


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
    total_items = sum(len(items) for items in results)
    logger.info(f"All crawlers finished, total items: {total_items}")


if __name__ == "__main__":
    asyncio.run(main())
