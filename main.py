import asyncio  # Библиотека синхронизации
import logging  # Библиотека логирования
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config  # настройка конфигурации подключение Токена
from handlers.start import router  # подключение модуля commands

loop = asyncio.get_event_loop()  # синхронизация
bot = Bot(token=config.TOKEN, loop=loop)  # бот
storage = MemoryStorage()  # синхронизация
dp = Dispatcher(storage=storage)  # Диспетчер

logging.basicConfig(level=logging.INFO)  # логирование

dp.include_router(router)


async def main():  # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    # asyncio.run(main())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.create_task(main())
        loop.run_forever()
        print("ok")
    except KeyboardInterrupt:
        print("404")
