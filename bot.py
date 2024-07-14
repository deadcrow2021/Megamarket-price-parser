from aiogram import Bot, Dispatcher
import asyncio

from constants import BOT_KEY

bot = Bot(BOT_KEY)

disp = Dispatcher()

async def main():
    await disp.start_polling(bot)
    

if __name__ == '__main__':
    asyncio.run(main())
