import pygame
from card_deck.card import Card
from card_deck.default_card import DefaultCard
import random
import json

# Mapeamento das imagens
IMAGES = {
    'treasure1': {'image': pygame.image.load("client/card_deck/images/treasure1.jpeg"), 'w': 245, 'h': 351, 'type': 'treasure'},
    'treasure2': {'image': pygame.image.load("client/card_deck/images/treasure2.jpeg"), 'w': 500, 'h': 809, 'type': 'treasure'},
    'door1': {'image': pygame.image.load("client/card_deck/images/door1.jpg"), 'w': 378, 'h': 585, 'type': 'door'},
    'door2': {'image': pygame.image.load("client/card_deck/images/door2.jpeg"), 'w': 245, 'h': 351, 'type': 'door'},
    'back': {'image': pygame.image.load("client/card_deck/images/back.jpg"), 'w': 379, 'h': 584, 'type': 'back'}
}

class Cards:
    def __init__(self, screen_width, screen_height, cards_info, card_width, card_height, treasure_rect, font_size):
        self.max_card_order = 0
        self.cards = []
        self.back_cards = {
            'treasure': DefaultCard(pygame.transform.smoothscale(IMAGES['back']['image'].subsurface((0, 0, IMAGES['back']['w'], IMAGES['back']['h'])), (card_width, card_height)), 0, 0),
            'door': DefaultCard(pygame.transform.smoothscale(IMAGES['back']['image'].subsurface((IMAGES['back']['w'], 0, IMAGES['back']['w'], IMAGES['back']['h'])), (card_width, card_height)), 0, 0)
        }
        self.expanded_card = None
        self.expanded_card_id = -1
        self.card_width = card_width
        self.card_height = card_height
        self.t_pos = (treasure_rect.x + 0.01 * treasure_rect.w, treasure_rect.y + 0.03 * treasure_rect.h)
        self.d_pos = (treasure_rect.x + 0.26 * treasure_rect.w, treasure_rect.y + 0.03 * treasure_rect.h)
        self.t_discard_pos = (treasure_rect.x + 0.51 * treasure_rect.w, treasure_rect.y + 0.03 * treasure_rect.h)
        self.d_discard_pos = (treasure_rect.x + 0.76 * treasure_rect.w, treasure_rect.y + 0.03 * treasure_rect.h)

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Carregar a fonte
        self.font = pygame.font.Font("client/card_deck/fonts/comicsans.ttf", font_size)

        # Criar os cartões a partir das imagens
        for i, (img_name, img_attrs) in enumerate(IMAGES.items()):
            if img_name == 'back':
                continue
            image = img_attrs['image']
            im_w = img_attrs['w']
            im_h = img_attrs['h']
            im_type = img_attrs['type']
            for j in range(70):
                im_idx = (i * 70) + j
                im_x = j % 10 * im_w
                im_y = j // 10 * im_h

                card = Card(pygame.transform.smoothscale(image.subsurface((im_x, im_y, im_w, im_h)), (card_width, card_height)), 0, 0, im_idx, im_type, im_x, im_y, img_name)
                card.set_info(cards_info[im_idx], screen_width, screen_height)

                self.cards.append(card)

                if card.order > self.max_card_order:
                    self.max_card_order = card.order

        random.shuffle(self.cards)

    def draw(self, win):
        self.cards.sort(key=lambda c: c.get_order())
        t_draw = 0
        d_draw = 0

        door_discard_list = []
        treasure_discard_list = []

        counts = {'deck': {'treasure': 0, 'door': 0}, 'discard': {'treasure': 0, 'door': 0}}

        # Contar as cartas no deck e as descartadas
        self.get_card_counts(door_discard_list, treasure_discard_list, counts)
        
        # Desenhar as cartas descartadas
        self.draw_discarded_cards(win, door_discard_list, treasure_discard_list, counts)

        # Desenhar as cartas no deck
        self.render_deck_cards(win, t_draw, d_draw, counts)

    def get_card_counts(self, door_discard_list, treasure_discard_list, counts):
        for card in self.cards:
            if card.order == 0:
                counts['deck'][card.type] += 1
            elif card.discarded:
                counts['discard'][card.type] += 1

            if card.discarded:
                if card.type == 'treasure':
                    treasure_discard_list.append(card)
                else:
                    door_discard_list.append(card)

    def render_deck_cards(self, win, t_draw, d_draw, counts):
        for card in self.cards:
            if not card.discarded:
                if card.order == 0:
                    if t_draw < 2 and card.get_type() == 'treasure':
                        self.back_cards['treasure'].draw_at(win, (card.x, card.y))
                        t_draw += 1
                        if t_draw == 2:
                            text = self.font.render(str(counts['deck']['treasure']), 1, ((0, 0, 0)))
                            win.blit(text, (card.x, card.y))

                    elif d_draw < 2 and card.get_type() == 'door':
                        self.back_cards['door'].draw_at(win, (card.x, card.y))
                        d_draw += 1
                        if d_draw == 2:
                            text = self.font.render(str(counts['deck']['door']), 1, ((0, 0, 0)))
                            win.blit(text, (card.x, card.y))

                elif card.to_draw:
                    if card.get_face():
                        card.draw(win)
                    else:
                        self.back_cards[card.get_type()].draw_at(win, (card.x, card.y))
                    if card.draging:
                        text = self.font.render(str(card.p_id), 1, ((0, 0, 0)))
                        win.blit(text, (card.x, card.y))

        if self.expanded_card:
            self.expanded_card.draw(win)

    def draw_discarded_cards(self, win, door_discard_list, treasure_discard_list, counts):
        for card in treasure_discard_list[-2:]:
            card.draw(win)
        text = self.font.render(str(counts['discard']['treasure']), 1, ((0, 0, 0)))
        win.blit(text, (self.t_discard_pos[0], self.t_discard_pos[1]))

        for card in door_discard_list[-2:]:
            card.draw(win)
        text = self.font.render(str(counts['discard']['door']), 1, ((0, 0, 0)))
        win.blit(text, (self.d_discard_pos[0], self.d_discard_pos[1]))

    def get_cards(self):
        return self.cards

    def reset(self):
        for card in self.cards:
            card.reset(self.t_pos, self.d_pos)
        random.shuffle(self.cards)

    def reset_discarded(self):
        for card in self.cards:
            if card.discarded:
                card.reset(self.t_pos, self.d_pos)
        random.shuffle(self.cards)

    def click(self, pos, player_id):
        for card in reversed(self.cards):
            if card.focused(pos) and card.to_draw:
                if not card.interact:
                    return None
                if card.click(pos):
                    card.p_id = player_id
                    self.max_card_order += 1
                    card.set_order(self.max_card_order)
                    return card.get_info(self.screen_width, self.screen_height)
        return None

    def release(self, pos, rect_equipments, rect_table, rect_hand):
        for card in reversed(self.cards):
            if card.interact and card.get_draging():
                card.release(pos, rect_equipments, rect_table, rect_hand)
                return card.get_info(self.screen_width, self.screen_height)
        return None

    def move(self, pos, rect_screen, rects, player_id):
        for card in self.cards:
            if card.p_id == player_id:
                if card.move(pos, rect_screen):
                    for rect_name, rect in rects.items():
                        if rect_name == 'screen':
                            continue
                        if rect.get_rect().collidepoint(pos):
                            card.area = rect_name
                            break
                    return card.get_info(self.screen_width, self.screen_height)
        return None

    def reveal(self, pos):
        for card in reversed(self.cards):
            if card.to_draw and card.focused(pos):
                if card.discarded or not card.interact:
                    return None
                if card.reveal(pos):
                    self.max_card_order += 1
                    card.set_order(self.max_card_order)
                    return card.get_info(self.screen_width, self.screen_height)
        return None

    def expand_card(self, pos):
        card_focused = False
        for card in reversed(self.cards):
            if card.focused(pos) and card.to_draw:
                if not card.get_face():
                    break

                if pos[0] < self.screen_width / 2:
                    card_x = pos[0]
                else:
                    card_x = pos[0] - self.card_width * 2
                if pos[1] < self.screen_height / 2:
                    card_y = pos[1]
                else:
                    card_y = pos[1] - self.card_height * 2

                self.expanded_card = card.expand(card_x, card_y, self.screen_width / 2, self.screen_height / 2)
                self.expanded_card_id = card.get_order()

                card_focused = True
                break
        if not card_focused:
            self.expanded_card = None
            self.expanded_card_id = -1

    def collapse_card(self):
        self.expanded_card = None
        self.expanded_card_id = -1

    def discard_cards(self):
        discard = {'treasure': [], 'door': []}
        for card in self.cards:
            if card.p_id != -1:
                discard[card.get_type()].append(card)
        return discard

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.cards, f, indent=4)

    def load(self, path):
        with open(path, "r") as f:
            self.cards = json.load(f)
        self.max_card_order = max(card['order'] for card in self.cards)
        random.shuffle(self.cards)
