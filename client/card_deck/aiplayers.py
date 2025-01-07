import random
import pygame
from card_deck.cards import Cards
from card_deck.players import Players
from card_deck.table import Table
from card_deck.scores import Scores

class AIPlayer:
    def __init__(self, player_id, player_name, cards_class, players_class, table_class, scores_class, network):
        # Atributos básicos do jogador IA
        self.player_id = player_id
        self.player_name = player_name
        self.cards_class = cards_class
        self.players_class = players_class
        self.table_class = table_class
        self.scores_class = scores_class
        self.network = network

        # Inicialização do estado do jogador
        self.cards = []
        self.level = 1
        self.selected_card = None
        self.dice_result = None
        self.player_hover = -1
        self.player_selected = -1

    def update_cards(self, new_cards):
        self.cards = new_cards
        self.selected_card = None

    def play_turn(self):
        if self.selected_card is None:
            self.select_card()
        
        # Simula rolar o dado
        if self.dice_result is None:
            self.roll_dice()

        self.interact_with_other_players()

    def select_card(self):
        if self.cards:
            # Se a IA estiver em um nível mais baixo, prioriza cartas de ataque
            attack_cards = [card for card in self.cards if 'attack' in card['type']]
            if attack_cards:
                self.selected_card = random.choice(attack_cards)
            else:
                # Caso contrário, escolhe uma carta aleatória
                self.selected_card = random.choice(self.cards)
            self.click_card(self.selected_card)

    def click_card(self, card):
        print(f"{self.player_name} selecionou a carta {card['name']}")
        # Atualiza as cartas do jogador
        self.network.send({'message_type': 'card_update', 'message': card})

    def roll_dice(self):
        self.dice_result = random.randint(1, 6)
        print(f"{self.player_name} rolou o dado: {self.dice_result}")
        self.network.send({'message_type': 'dice_roll', 'message': self.dice_result})

    def make_move(self):
        if self.selected_card:
            self.discard_card(self.selected_card)

    def discard_card(self, card):
        print(f"{self.player_name} descartou a carta {card['name']}")
        self.network.send({'message_type': 'card_update', 'message': {'action': 'discard', 'card': card}})

    def update_level(self, new_level):
        self.level = new_level
        print(f"{self.player_name} agora está no nível {self.level}")
        
        # A IA prioriza aumentar o nível quando estiver muito atrás
        if self.level < 3:
            print(f"{self.player_name} está tentando subir de nível!")
            self.network.send({'message_type': 'level_update', 'message': {'player': self.player_id, 'level': self.level}})
        elif self.level >= 3:
            # Busca vitória, priorizando ataques
            self.network.send({'message_type': 'win_attempt', 'message': {'player': self.player_id}})

    def interact_with_other_players(self):
        # Avalia a melhor ação para tomar
        target_player = self.choose_target_player()
        action = self.decide_action(target_player)
        print(f"{self.player_name} decide {action} {target_player['name']}")
        self.network.send({'message_type': 'player_action', 'message': {'action': action, 'target': target_player}})

    def choose_target_player(self):
        # A IA prefere interagir com jogadores mais fracos ou mais vulneráveis
        opponents = [player for player in self.players_class.players if player['id'] != self.player_id]
        # Ordena os jogadores pelo nível (menor nível é mais fraco)
        opponents.sort(key=lambda p: p['level'])
        return opponents[0]  # Retorna o jogador mais fraco (pode ser ajustado)

    def decide_action(self, target_player):
        # Lógica mais complexa para decidir se deve atacar ou negociar
        if target_player['level'] < self.level:
            return 'attack'  # Ataque jogadores mais fracos
        elif target_player['level'] == self.level:
            # Negociar ou até formar alianças
            if random.random() < 0.5:  # 50% de chance de tentar negociar
                return 'negotiate'
            else:
                return 'attack'
        else:
            # Ignorar ou buscar uma carta de defesa contra jogadores mais fortes
            return 'ignore'

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Processa clique de IA
            if event.button == 1:  # Botão esquerdo
                if self.table_class.get_collidepoint('players', event.pos):
                    self.player_selected = self.players_class.focused(event.pos, 'select')
                elif self.table_class.get_collidepoint('logs', event.pos):
                    self.roll_dice()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                # Implementa uma lógica para quando a IA deseja descartar cartas
                self.discard_card(self.selected_card)
            elif event.key == pygame.K_a:
                # A IA pode tomar uma ação especial aqui, dependendo do tipo de carta ou situação
                self.perform_special_action()

    def perform_special_action(self):
        # A IA pode executar uma ação especial dependendo de uma condição no jogo
        print(f"{self.player_name} realizou uma ação especial!")
        self.network.send({'message_type': 'special_action', 'message': self.player_name})

    def perform_actions(self):
        self.play_turn()
        self.make_move()
