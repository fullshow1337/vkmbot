from aiogram import md

def clear_text (text: str) -> str:
    return md.quote_html(text)


def convert_duration (seconds: int) -> str:
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if len(f'{seconds}') == 1:
        return "{}:0{}".format(minutes, seconds)
    return "{}:{}".format(minutes, seconds)
