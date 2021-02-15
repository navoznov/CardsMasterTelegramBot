class Card:
    EMPTY_ID = -1

    def __init__(self, text, tag, author, country, id: int = EMPTY_ID):
        self.id = id
        self.text = text
        self.tag = tag
        self.author = author
        self.country = country

    @staticmethod
    def from_dict(card_dict: dict) -> Card:
        id = card_dict.get("id", EMPTY_ID)
        author = card_dict.get("author", None)
        country = card_dict.get("country", None)
        card = Card(card_dict["text"], card_dict["tag"], author, country, id)
        return card
