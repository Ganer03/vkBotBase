# Standart library
import asyncio
import json
import random
import string

import aiohttp
import hues
import time

from captcha_solver import CaptchaSolver
import requests

from methods import is_available_from_group
from methods import is_available_from_public
from utils import MessageEventData, chunks, Attachment, RequestFuture, schedule_coroutine, SendFrom

from database import *
from vkapi import VkClient

solver = None

try:
    from settings import CAPTCHA_KEY, CAPTCHA_SERVER, TOKEN, SCOPE, APP_ID

    if CAPTCHA_KEY and CAPTCHA_KEY:
        solver = CaptchaSolver(CAPTCHA_SERVER, api_key=CAPTCHA_KEY)
except (ImportError, AttributeError):
    pass


class NoPermissions(Exception):
    pass


async def enter_captcha(url):
    if not solver:
        return hues.warn('Введите данные для сервиса решения капч в settings.py!')

    session = aiohttp.ClientSession()

    with session as ses:
        async with ses.get(url) as resp:
            img_data = await resp.read()
            data = solver.solve_captcha(img_data)
            return data


async def enter_confirmation_сode():
    hues.error("Похоже, у вас утсановлена двухфакторная авторизация!")
    hues.error("Пожалуйста, введите код подтверждения:")

    code = input()

    hues.success("Спасибо! Продолжаю приём сообщений")

    return code


class VkPlus(object):
    def __init__(self, bot, users_data: list=[], proxies: list=[], app_id: int=5982451, scope=140489887):
        self.bot = bot
        self.users = []
        self.tokens = []
        self.scope = scope
        self.group = False
        self.app_id = app_id
        self.proxies = proxies
        self.users_data = users_data
        self.current_user = 0
        self.current_token = 0

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_vk())

    async def init_vk(self):
        """Инициализация сессий ВК API"""
        current_proxy = 0

        for user in self.users_data:
            if self.proxies:
                proxy = self.proxies[current_proxy % len(self.proxies)]
                current_proxy += 1

            else:
                proxy = None

            if len(user) == 1:
                client = VkClient(proxy)
                await client.group(user[0])

                self.tokens.append(client)
                self.group = True

            else:
                client = VkClient(proxy)
                await client.user(user[0], user[1], self.app_id, self.scope)

                self.users.append(client)



    async def method(self, key: str, data=None, send_from=None, nowait=False):
        """Выполняет метод API VK с дополнительными параметрами"""
        if send_from is None:
            if self.group and is_available_from_group(key):
                send_from = SendFrom.GROUP
            elif is_available_from_public(key):
                send_from = SendFrom.USER
            else:
                send_from = SendFrom.USER

        task = RequestFuture(key, data, send_from)

        client = None

        if self.users and send_from == SendFrom.USER:
            client = self.users[self.current_user % len(self.users)]
            self.current_user += 1
        elif self.tokens and send_from == SendFrom.GROUP:
            client = self.tokens[self.current_token % len(self.tokens)]
            self.current_token += 1

        if not client:
            hues.error(f"Некому выполнять: {task.key}")
            return None

        if key == 'messages.send':
            url = f"https://api.vk.com/method/{key}"
            params = {
                **data,
                'random_id': random.randint(1, 2**31 - 1), 
                'access_token': client.token,               
                'v': '5.131'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    hues.error(f"Ошибка при отправке сообщения: {result['error']}")
                else:
                    hues.success("Сообщение успешно отправлено")
            else:
                hues.error(f"HTTP ошибка: {response.status_code}")
            return result

        # Обработка других методов
        client.queue.put_nowait(task)

        if nowait:
            return None

        return await asyncio.wait_for(task, None)


    @staticmethod
    def anti_flood():
        """Возвращает строку из 5 символов (букв и цифр)"""
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    async def mark_as_read(self, message_ids):
        """Отмечает сообщение(я) как прочитанное(ые)"""
        await self.method('messages.markAsRead', {'message_ids': message_ids})

    async def resolve_name(self, screen_name):
        """Функция для перевода короткого имени в числовой ID"""
        try:
            for val in ('club', 'public', 'event'):
                screen_name = screen_name.replace(val, '')
            possible_id = int(screen_name)
            return possible_id

        except ValueError:
            result = await self.method('utils.resolveScreenName',
                                       {'screen_name': screen_name})
            if not result:
                return False

            return result.get('object_id')


class Message(object):
    """Класс, объект которого передаётся в плагин для упрощённого ответа"""
    __slots__ = ('_data', 'vk', 'conf', 'user', 'cid', 'user_id', "peer_id", "text",
                 'body', 'timestamp', 'answer_values', 'brief_attaches', '_full_attaches', 'msg_id')

    def __init__(self, vk_api_object: VkPlus, data: MessageEventData):
        self._data = data
        self.vk = vk_api_object
        self.user = False
        # Если сообщение из конференции
        if data.conf:
            self.user = False
            self.cid = int(data.peer_id)
        else:
            self.user = True
        self.user_id = data.user_id
        self.peer_id = data.peer_id
        self.body = data.body
        self.text = self.body
        self.msg_id = data.msg_id
        self.timestamp = data.time
        self.brief_attaches = data.attaches
        self._full_attaches = []
        # Словарь для отправки к ВК при ответе
        if self.user:
            self.answer_values = {'user_id': self.user_id}
        else:
            self.answer_values = {'chat_id': self.cid}

    @property
    async def full_attaches(self):
        # Если мы уже получали аттачи для этого сообщения, возвратим их
        if self._full_attaches:
            return self._full_attaches

        values = {'message_ids': self.msg_id,
                  'preview_length': 1}
        # Получаем полную информацию о сообщении в ВК (включая аттачи)
        full_message_data = await self.vk.method('messages.getById', values)

        if not full_message_data:
            # Если пришёл пустой ответ от VK API
            return []

        message = full_message_data['items'][0]
        if "attachments" not in message:
            # Если нет аттачей
            return
        # Проходимся по всем аттачам
        for raw_attach in message["attachments"]:
            # Тип аттача
            a_type = raw_attach['type']
            # Получаем сам аттач
            attach = raw_attach[a_type]

            link = ""
            # Ищём ссылку на фото
            for k, v in attach.items():
                if "photo_" in k:
                    link = v
            # Получаем access_key для аттача
            key = attach.get('access_key')
            attach = Attachment(a_type, attach['owner_id'], attach['id'], key, link)
            # Добавляем к нашему внутреннему списку аттачей
            self._full_attaches.append(attach)

        return self._full_attaches

    async def answer(self, msg: str, nowait=False, **additional_values):
        """Функция ответа на сообщение для плагинов"""
        # Если длина сообщения больше 550 символов (получено эмпирическим путём)
        if len(msg) > 2048:
            # Делим сообщение на список частей (каждая по 15 строк)
            msgs = list(chunks(msg, 2048))
        else:
            # Иначе - создаём список из нашего сообщения
            msgs = [msg]
        if additional_values is None:
            additional_values = dict()
        # Отправляем каждое сообщение из списка
        for msg in msgs:
            data = msgs[0] if not len(msgs) > 1 else '\n'.join(msgs)
            values = dict(**self.answer_values, message=data, **additional_values)
            await self.vk.method('messages.send', values, nowait=nowait)
