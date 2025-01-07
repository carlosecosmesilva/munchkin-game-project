from client.card_deck.card import Card

class TreasureCard(Card):
    def __init__(self, image, x, y, card_id, card_type, im_x, im_y, name, value, bonus):
        super().__init__(image, x, y, card_id, card_type, im_x, im_y, name)
        self.value = value  # Valor em ouro
        self.bonus = bonus  # Bônus de combate

    def get_value(self):
        return self.value

    def get_bonus(self):
        return self.bonus