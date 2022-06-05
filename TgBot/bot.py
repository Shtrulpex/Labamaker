from TgBot.config import *
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Hello!')


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    await message.answer('Goodbye')

@dp.message_handler(content_types=)
@dp.message_handler()
async def default(message: types.Message):
    await message.reply('What???')
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
