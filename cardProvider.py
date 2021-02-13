import json
import random


class CardProvider:
    def __init__(self):
        random.seed()

    def get_all(self):
        json_str = open("cards.json", encoding="utf-8").read()
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