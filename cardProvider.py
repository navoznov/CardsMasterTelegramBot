import json
import random
import os
from shutil import copyfile

class CardProvider:
    __CARDS_FILENAME = "cards.json"
    __DEFAULT_CARDS_FILENAME = "defaultCards.json"

    def __init__(self):
        random.seed()

        # если первый запуск и еще нет файла с карточками то копируем дефолтный файл
        if not os.path.isfile(self.__CARDS_FILENAME):
            copyfile(self.__DEFAULT_CARDS_FILENAME, self.__CARDS_FILENAME)

    def get_all(self):
        json_str = open(self.__CARDS_FILENAME, encoding="utf-8").read()
        cards = json.loads(json_str)["cards"]
        return cards

    def get_random(self, tag: str = None):
        cards = self.get_all()
        if tag != None:
            cards = [card for card in cards if tag in card["tags"]]

        card = random.choice(cards)
        return card

    def get_all_tags(self):
        cards = self.get_all()
        all_tags = []
        for card in cards:
            card_tags = card["tags"]
            all_tags = all_tags + card_tags

        return list(set(all_tags))