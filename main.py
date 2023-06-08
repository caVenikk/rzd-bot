import asyncio
import logging

from handlers import dp


async def main():
    try:
        await dp.start_polling()
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
