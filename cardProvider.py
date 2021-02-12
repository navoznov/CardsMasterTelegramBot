import json
import random

class CardProvider:
    def __init__(self):
        random.seed()

    def get_all(self):
        json_str = open("cards.json", encoding="utf-8").read()
        cards = json.loads(json_str)["cards"]
        return cards

    def get_random(self):
        cards = self.get_all()
        card =  random.choice(cards)
        return card