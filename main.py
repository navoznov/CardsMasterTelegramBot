from cardService import CardService
from options import Options
from optionsParser import OptionsParser
from telegramBot import TelegramBot
from cardRepository import CardRepository
from card import Card

options = OptionsParser.parse()
card_repository = CardRepository()
card_service = CardService(card_repository)
bot = TelegramBot(options.telegram_bot_token, card_service)
bot.go()
