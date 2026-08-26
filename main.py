import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота берется из переменных окружения Render
TOKEN = os.getenv("BOT_TOKEN", "8957204394:AAFBWR8sH95eQZzvxiVc6ehxNKv4mVb_kE8")
# Ссылка на Mini App
WEBAPP_URL = "https://abdulborimusaev0122-hub.github.io/tictactoe/?v=2"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальная клавиатура с кнопкой игры для всех пользователей
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Играть в Крестики-Нолики",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )

# Единый обработчик команды /start для всех пользователей
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в Крестики-Нолики!\n\n"
        "Нажми на кнопку ниже, чтобы начать игру:",
        reply_markup=get_main_keyboard()
    )

# Простой HTTP-сервер для поддержки активности сервиса на Render
async def handle_ping(request):
    return web.Response(text="Bot is online and running!")

async def main():
    # Запуск фонового веб-сервера для Render
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/ping", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # Старт поллинга бота
    logging.info("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
