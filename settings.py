"""
Описание возможных значений:
False - нет, True - да
() - кортеж, заполняется элементами через запятую
'' - строка, само содержимое пишется между кавычками
"""
# Данные для авторизации бота
# Кортеж из одного элемента - токен группы
# Кортеж из 2х элементов - логин/ пароль пользователя
# Если в кортеже 1 элемент - запятая в конце обязательна!

# Если ввести несколько пользователей, методы, требующие пользователя будут выполняться по
# очереди от лица этих аккаунтов.

# Если ввести несколько токенов групп, метода, которые можно выполнить от лица группы
# Будут выполняться от лица этих групп.

# # # Не рекомендуется вводить токены разных групп
# # # Не рекомендуется вводить несколько пользователей, если не введена группа(т.к. бот будет отвечать
# # # по очереди от разных аккаунтов).
USERS = (
          ("vk1.a.nBP2FduQfJYyHuuLeiATaQNEmo22LG0tclPcWuFyRgLYeyYYPCqXSvX7QeblcYDoMXeCqhuOsnfXhePyyZ7iRSxOzOPb5vIf8D0VN1O1XCu-WmPz9y232lWkypTDOGaookiqdzKWj79oaCG7fI_sKDpy5woqQIlN5qOUjELn3Zw6Yn8KybXO2WcEDLHO49mIxgSHEzk2DZNxmPh-XhelFg",),
        # ("LOGIN", "PASSWORD"),
    )
# Прокси для подключения к VK API с помощью данных из USERS
PROXIES = (
        # ("ADDRESS", PORT, "USER", "PASSWORD"),
    )
# Является ли бот группой
IS_GROUP = True
# Нужно ли писать получаемые сообщения в лог
LOG_MESSAGES = True
# Нужно ли писать выполняемые команды в лог
LOG_COMMANDS = True
# Префиксы сообщений, с помощью которых бот будет понимать, что обращаются к нему.
PREFIXES = ('!', )
# Принимать ли все заявки в друзья автоматически
ACCEPT_FRIENDS = False
# Черный список пользователей (не особо полезно)
BLACKLIST = (0, )
# Список администраторов
ADMINS = ()
# ID приложения, через которое бот будет авторизовываться
APP_ID = 5982451
# Максимальные права - https://vk.com/dev/permissions
SCOPE = 140489887

# Задержка между исполнением команд для одного пользователя. Антифлуд
# Рекомендуемое значение - 1 секунда
FLOOD_INTERVAL = 1

# На текущий момент может принимать значение -  rucaptcha или antigate
CAPTCHA_SERVER = "rucaptcha"  # Сервис для решения капч.
CAPTCHA_KEY = ""  # API ключ для сервиса решения капч

# Данные для базы данных PostgreSQL
# DATABASE_SETTINGS = ("DATABASE NAME", "HOST", PORT, "USER", "PASSWORD")
DATABASE_SETTINGS = ("PostgreSQL-5166","83.166.236.211",5432,"user","6m3P37c2j6s3LM(C6")
DATABASE_DRIVER = "postgresql"  #  Может принимать значения: mysql, postgresql
DATABASE_CHARSET = 'utf8'  # utf8, utf8mb4, latin1 и т.д.

# Загружаются только указанные плагины или все, при отсутствии значения
# ENABLED_PLUGINS = [
#     'available_cmds',
#     'exchange_rate',
#     'memes',
#     'loaded_plugins',
#     'say_joke',
#     'tts',
#     ]
ENABLED_PLUGINS = []
