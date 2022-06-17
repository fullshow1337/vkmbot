from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from main import api
from .utils import convert_duration


async def get_keyboards (data: dict) -> dict:
    """
    Get keyboards

    :param state:
    """
    number, answer = 1, ''
    keyboard = InlineKeyboardMarkup(row_width=5)
    items = await api.search_music(
        query=data['query'], offset=data['offset'])
    for item in items['items']:
        answer += f"<b>{number}</b>. {item['artist']} - {item['title']} " \
                  f"<b>{convert_duration(item['duration'])}</b>\n"
        callback_data = f"{item['owner_id']}_{item['id']}"
        keyboard.insert(
            InlineKeyboardButton(text=f'{number}', callback_data=callback_data)
        )
        number += 1
    if data['offset'] == 0:
        keyboard.add(
            InlineKeyboardButton(text='➡️', callback_data='next_page')
        )
    elif len(items['items']) >= 10:
        keyboard.add(
            InlineKeyboardButton(text='⬅️', callback_data='old_page'),
            InlineKeyboardButton(text='➡️', callback_data='next_page')
        )
    else:
        keyboard.add(
            InlineKeyboardButton(text='⬅️', callback_data='old_page')
        )
    return {'text': answer, 'keyboard': keyboard, 'count': items['count']}
