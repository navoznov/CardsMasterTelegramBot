from cardProvider import CardProvider
from options import Options
from optionsParser import OptionsParser
from telegramBot import TelegramBot

options = OptionsParser.parse()
card_provider = CardProvider()
bot = TelegramBot(options.telegram_bot_token, card_provider)
bot.go()
