from cardRepository import CardRepository
from card import Card
import random

class CardService:
    def __init__(self, card_repository: CardRepository):
        self.__card_repository = card_repository
        random.seed()

    def get_all(self):
        return self.__card_repository.get_all()

    def get_by_tag(self, tag: str):
        return self.__card_repository.get_by_tag(tag)

    def get_random_card(self, tag: str = None) -> Card:
        cards = self.__card_repository.get_all()
        if tag != None:
            cards = [card for card in cards if tag == card.tag]

        card = random.choice(cards)
        return card

    def get_all_tags(self):
        cards = self.__card_repository.get_all()
        all_tags = [card.tag for card in cards]
        return list(set(all_tags))
