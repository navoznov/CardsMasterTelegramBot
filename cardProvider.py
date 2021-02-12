import json

class CardProvider:
    @staticmethod
    def get_all():
        json_str = open("cards.json", encoding="utf-8").read()
        cards = json.loads(json_str)
        return cards