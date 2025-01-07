from card_deck.field import Field

# Cores definidas para os resultados
WINNER_COLOR = (60, 218, 37)
LOSER_COLOR = (242, 36, 13)
DEFAULT_COLOR = (100, 112, 100)

class Scores:
    def __init__(self, table_start_x, screen_width, screen_height, font_size):
        table_center_x = (screen_width + table_start_x) / 2
        delta = 0.01 * screen_width
        field_w = 0.13 * screen_width
        field_h = 0.06 * screen_height
        
        # Definindo as instâncias dos campos de placar
        self.scores = {
            'player': Field(table_center_x + delta, 0.01 * screen_height, field_w, field_h, DEFAULT_COLOR, 'player: 0', font_size),
            'monster': Field(table_center_x - field_w - delta, 0.01 * screen_height, field_w, field_h, DEFAULT_COLOR, 'monster: 0', font_size)
        }

    def draw(self, win):
        for field in self.scores.values():
            field.draw(win)
    
    def collidepoint(self, pos):
        return any(field.rect.collidepoint(pos) for field in self.scores.values())

    def backspace(self, pos):
        for field in self.scores.values():
            if field.rect.collidepoint(pos):
                # Modifica o texto dependendo da quantidade de dígitos
                field.text = self._modify_text_for_backspace(field.text)
                self.update_colors()
                return {'type': field.text.split(' ')[0][:-1], 'value': field.text.split(' ')[1]}

    def add_number(self, pos, number):
        for field in self.scores.values():
            if field.rect.collidepoint(pos):
                field.text = self._modify_text_for_addition(field.text, number)
                self.update_colors()
                return {'type': field.text.split(' ')[0][:-1], 'value': field.text.split(' ')[1]}

    def set_number(self, type, number):
        self.scores[type].text = f'{self.scores[type].text.split(" ")[0]} {number}'
        self.update_colors()

    def update_colors(self):
        player_power, monster_power = self._get_powers()
        
        if player_power == 0 and monster_power == 0:
            self._set_colors(DEFAULT_COLOR, DEFAULT_COLOR)
        elif player_power > monster_power:
            self._set_colors(WINNER_COLOR, LOSER_COLOR)
        else:
            self._set_colors(LOSER_COLOR, WINNER_COLOR)

    def _modify_text_for_backspace(self, text):
        text_value = text.split(' ')[1]
        if len(text_value) == 1 and text_value != '0':  # Se um único dígito
            return text[:-1] + '0'
        elif len(text_value) == 2:  # Se dois dígitos
            return text[:-1]
        return text

    def _modify_text_for_addition(self, text, number):
        if len(text.split(' ')[1]) == 1:  # Se apenas um dígito
            if text[-1] == '0':
                return text[:-1] + number
            else:
                return text + number
        return text

    def _get_powers(self):
        player_power = int(self.scores['player'].text.split(' ')[1])
        monster_power = int(self.scores['monster'].text.split(' ')[1])
        return player_power, monster_power

    def _set_colors(self, player_color, monster_color):
        self.scores['player'].color = player_color
        self.scores['monster'].color = monster_color
