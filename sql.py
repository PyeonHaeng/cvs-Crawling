import aiomysql
import os
import asyncio
from dotenv import load_dotenv


class AsyncSQL:
    def __init__(self, charset: str = "utf8") -> None:
        load_dotenv()
        self.__config = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "db": os.getenv("DB_NAME"),
            "charset": charset,
        }
        self.__pool = None

    async def __aenter__(self):
        try:
            self.__pool = await aiomysql.create_pool(**self.__config)
            return self
        except Exception as e:
            print(f"SQL Error, {e}")
            raise e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__pool is not None:
            self.__pool.close()
            await self.__pool.wait_closed()

    async def execute(self, query, *args):
        async with self.__pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                if query.lower().startswith(("select", "show")):
                    return await cur.fetchall()
                else:
                    await conn.commit()
                    return None


async def main():
    async with AsyncSQL() as async_sql:
        result = await async_sql.execute(
            "SELECT id FROM main_products WHERE name = %s", "반찬단지)연근조림120g"
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
