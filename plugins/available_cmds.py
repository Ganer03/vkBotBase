import requests
from plugin_system import Plugin
from settings import PREFIXES

import asyncio

from utils import schedule_coroutine

plugin = Plugin('Помощь',
                usage=['команды - узнать список доступных команд'])

def send_answer(user_id, text, token):
    """Отправка сообщения через запрос к API ВКонтакте."""
    url = "https://api.vk.com/method/messages.send"
    params = {
        'user_id': user_id,
        'message': text,
        'random_id': 0,        # Уникальный ID сообщения
        'access_token': token,  # Токен для доступа к API
        'v': '5.131'            # Версия API
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            print(f"Сообщение успешно отправлено пользователю {user_id}")
        else:
            print(f"Ошибка при отправке сообщения: {data.get('error')}")
    else:
        print(f"HTTP ошибка при отправке сообщения: {response.status_code}")

@plugin.on_command('команды', 'помоги', 'помощь')
async def call(msg, args):
    usages = "🔘Доступные команды:🔘\n"

    for plugin in msg.vk.get_plugins():
        if not plugin.usage:
            continue

        temp = "🔷" + plugin.name + ":🔷" + "\n"

        for usage in plugin.usage:
            temp += "🔶" + PREFIXES[0] + usage + "\n"

        temp += "\n"

        if len(usages) + len(temp) >= 550:
            await msg.answer(usages, True)
            usages = ""

        usages += temp

    send_answer(msg.user_id, usages, msg.vk.token)
