from client.card_deck.door_card import DoorCard

class CurseCard(DoorCard):
    def __init__(self, image, x, y, card_id, card_type, im_x, im_y, name, effect):
        super().__init__(image, x, y, card_id, card_type, im_x, im_y, name, door_type="curse")
        self.effect = effect  # Descrição da maldição

    def get_effect(self):
        return self.effect