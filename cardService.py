from cardRepository import CardRepository


class CardService:
    def __init__(self, card_repository: CardRepository):
        self.__card_repository = card_repository
        random.seed()

    def get_all(self) -> list(Card):
        return self.__card_repository.get_all()

        def get_by_tag(self, tag: str) -> list(Card):
        return self.__card_repository.get_by_tag(tag)

    def get_random(self, tag: str = None) -> Card:
        cards = self.__card_repository.get_all()
        if tag != None:
            cards = [card for card in cards if tag == card.tag]

        card = random.choice(cards)
        return card

    def get_all_tags(self) -> list(str):
        cards = self.__card_repository.get_all()
        all_tags = [card.tag for card in cards]
        return list(set(all_tags))
