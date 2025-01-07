
from client.card_deck.door_card import DoorCard

class MonsterCard(DoorCard):
    def __init__(self, image, x, y, card_id, card_type, im_x, im_y, name, level, reward, bad_stuff):
        super().__init__(image, x, y, card_id, card_type, im_x, im_y, name, door_type="monster")
        self.level = level  # Nível do monstro
        self.reward = reward  # Recompensa ao derrotar
        self.bad_stuff = bad_stuff  # Consequências ao perder

    def get_level(self):
        return self.level

    def get_reward(self):
        return self.reward

    def get_bad_stuff(self):
        return self.bad_stuff