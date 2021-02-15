from cardProvider import CardProvider
from options import Options
from optionsParser import OptionsParser
from telegramBot import TelegramBot
from cardRepository import CardRepository
from card import Card

options = OptionsParser.parse()
card_provider = CardProvider()
card_repository = CardRepository('cards1.db')
cards = card_repository.get_by_tag("Политика")
text = "Каждый имеет право на свободу и личную неприкосновенность"
card = Card(text, "Закон", "Конституция РФ", "РФ")
card_repository.add(card)

bot = TelegramBot(options.telegram_bot_token, card_provider)
bot.go()
