import logging

from aiogram.utils.executor import start_polling, Dispatcher

from handlers import dp


def on_events():
    async def startup(_: Dispatcher) -> None:
        pass

    async def shutdown(dispatcher: Dispatcher) -> None:
        logging.info("Closing storage...")
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()
        logging.info("Bot shutdown...")

    return startup, shutdown


if __name__ == "__main__":
    on_startup, on_shutdown = on_events()
    start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
