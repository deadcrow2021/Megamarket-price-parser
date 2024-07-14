import os


BOT_KEY = 'bot_api_key'

# магазины, для которых ориентируюсь только на цену товара
PRICE_SHOPS = [
    'Digital 123',
    'asdStore',
    'qwe.Market',
    ]

# магазины, для которых ориентируюсь только на разницу (цена - бонусы)
BONUS_SHOPS = [
    'zxc.Store',
    ]


# id чата
CHAT_ID = -10010000000000

# задержка между ссылками
DELAY_BETWEEN_LINKS = 5 # seconds
# задержка между циклами парсинга
DELAY_BETWEEN_PARSE_CYCLES = 15 # minutes

# путь к текущей папке (в которой лежит этот файл)
CURRENT_DIR_PATH = os.path.dirname(__file__)
# путь к файлу с ссылками
DATA_PATH = os.path.join(CURRENT_DIR_PATH, 'links_test.xlsx')

