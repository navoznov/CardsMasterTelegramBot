from cardProvider import CardProvider
from options import Options
from optionsParser import OptionsParser
from telegramBot import TelegramBot

# получаем настройки приложения
options = OptionsParser.parse()

card_provider = CardProvider()
card = card_provider.get_random("Политика")
tags = card_provider.get_all_tags()

# создаем и запускаем телеграм бота
bot = TelegramBot(options.telegram_bot_token)
bot.go()

pass
