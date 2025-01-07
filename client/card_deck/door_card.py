
from client.card_deck.card import Card

class DoorCard(Card):
    def __init__(self, image, x, y, card_id, card_type, im_x, im_y, name, door_type):
        super().__init__(image, x, y, card_id, card_type, im_x, im_y, name)
        self.door_type = door_type  # Tipo da porta (ex: monstro, maldição, etc.)

    def get_door_type(self):
        return self.door_type