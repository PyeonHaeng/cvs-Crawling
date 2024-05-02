import aiomysql
import os


class AsyncSQL:
    def __init__(self, charset: str = "utf8") -> None:
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
                return await cur.fetchall()
