import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config  # настройка конфигурации подключение Токена
from handlers.start import router  # подключение модуля commands

# настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=config.TOKEN)  # loop не нужен, aiogram сам управляет циклом событий
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    # Запуск бота
    try:
        await dp.start_polling(bot)  # aiogram сам обрабатывает исключения
    except KeyboardInterrupt:
        await bot.close()  # важно корректно закрыть бот
        logging.info("Бот остановлен.")
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")  # Логирование ошибок
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())  # Упрощен запуск
