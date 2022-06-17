import logging

from aiogram import types
from aiogram.bot import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

import keyboards
import config
from vk_music_api import vk_music_api
from vk_music_api.exceptions import MusicNotFound, VkApiError

logging.basicConfig(level=logging.INFO)
dp = Dispatcher(
    bot=Bot(config.bot_token, parse_mode=types.ParseMode.HTML), storage=MemoryStorage()
)

api = vk_music_api(access_token=config.access_token, user_agent=config.user_agent)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Кчау✌️\nС помощью этого бота ты сможешь скачать любой трек из ВКонтакте. Просто напиши исполнителя либо название трека.")

@dp.message_handler()
async def text_message (message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'], data['query'] = 1, message.text,
        data['offset'] = 0
        keyboard_data = await keyboards.get_keyboards(data)
        await message.answer(
            text=keyboard_data['text'], reply_markup=keyboard_data['keyboard'])


@dp.callback_query_handler(text='next_page')
async def call_inline_next (call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.answer()
        data['page'] = data['page'] + 1
        data['offset'] = data['offset'] + 10
        keyboard_data = await keyboards.get_keyboards(data)
        await call.message.edit_text(
            text=keyboard_data['text'], reply_markup=keyboard_data['keyboard'])


@dp.callback_query_handler(text='old_page')
async def call_inline_old (call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.answer()
        if data['offset'] != 0:
            data['page'] = data['page'] - 1
            data['offset'] = data['offset'] - 10
            keyboard_data = await keyboards.get_keyboards(data)
            await call.message.edit_text(
                text=keyboard_data['text'], reply_markup=keyboard_data['keyboard'])


@dp.callback_query_handler()
async def download_track (call: types.CallbackQuery):
    await call.answer()
    await types.ChatActions.upload_audio()
    data = await api.get_music_file(data=await api.get_music(call.data))
    await call.message.answer_audio(
        audio=data['audio'], title=data['title'], performer=data['artist'])
    data['audio'].close()


@dp.errors_handler(exception=MusicNotFound)
async def message_error (update: types.Update, exception: Exception):
    await update.message.reply('Исполнитель/Трек не найдены❌')
    return True


@dp.errors_handler(exception=VkApiError)
async def message_error (update: types.Update, exception: Exception):
    await update.message.reply('Error')
    return True


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True
    )
