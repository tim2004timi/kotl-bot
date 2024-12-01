import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties

from handlers import register_handlers


TOKEN = "8029600416:AAHC6ejKwFDa1k9b39aKEInMVYURsAYvlvo"
commands = [
    types.BotCommand(command="/start", description="Начать"),
    types.BotCommand(command="/menu", description="Меню"),
    types.BotCommand(command="/help", description="Помощь"),
    types.BotCommand(command="/about", description="О боте"),
]


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    print("Бот запущен!")

    register_handlers(dp)
    await bot.set_my_commands(commands)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
