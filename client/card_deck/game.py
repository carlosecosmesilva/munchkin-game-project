import pygame
import time
from ctypes import windll
from card_deck.cards import Cards
from card_deck.table import Table
from card_deck.players import Players
from card_deck.scores import Scores
import threading
from client.card_deck.aiplayers import AIPlayer

# Classes globais
cards_class = None
players = None
players_class = None
table_class = None
scores_class = None

# Locks para evitar condições de corrida
cards_class_lock = threading.Lock()
players_class_lock = threading.Lock()
table_class_lock = threading.Lock()
scores_class_lock = threading.Lock()

# Variáveis de controle
running = False

# Limites de tela e tamanho de jogadores
X_LIMITS_DEFAULT = [0.4, 0.8]
Y_LIMITS_DEFAULT = [0.25, 0.75]
W_PLAYERS_DEFAULT = X_LIMITS_DEFAULT[0] / 2
H_PLAYERS_DEFAULT = Y_LIMITS_DEFAULT[0] / 5

def caller(obj, method, args, lock):
    with lock:
        return getattr(obj, method)(*args)

def listen(network):
    try:
        global cards_class, players_class, table_class, scores_class, players, running
        while not running:
            time.sleep(0.01)
        while running:
            message = network.receive()
            if message:
                message_type = message['message_type']
                if message_type == 'card_update':
                    caller(cards_class, 'update', [message['message']], cards_class_lock)
                elif message_type == 'player_disconnected':
                    caller(cards_class, 'discard_player', [message['message']], cards_class_lock)
                    players.remove(message['message'])
                    caller(players_class, 'delete_player', [players, message['message']], players_class_lock)
                elif message_type == 'players_update':
                    players.append(message['message']['player'])
                    caller(players_class, 'update_players', [players, message['message']['levels']], players_class_lock)
                    caller(cards_class, 'set_player_cards', [message['message']['player']], cards_class_lock)
                elif message_type == 'reset_game':
                    caller(cards_class, 'reset', [], cards_class_lock)
                elif message_type == 'reset_discarded':
                    caller(cards_class, 'reset_discarded', [], cards_class_lock)
                elif message_type == 'dice_roll':
                    caller(table_class, 'dice_roll', [message['message']], table_class_lock)
                elif message_type == 'level_update':
                    caller(players_class, 'set_level', [message['message']['player'], message['message']['level']], players_class_lock)
                elif message_type == 'score_update':
                    caller(scores_class, 'set_number', [message['message']['type'], message['message']['value']], scores_class_lock)
                elif message_type == 'heartbeat':
                    network.send({'message_type': 'heartbeat'})
                elif message_type == 'self_disconnected':
                    break
        print('listen ended')
    except Exception as e:
        print('listen error ', e)
        network.send({'message_type': 'quit'})
        raise e

def play(network):
    try:
        global cards_class, players, players_class, table_class, scores_class, running

        DEFAULT_WIDTH = 527
        DEFAULT_HEIGHT = 317
        DEFAULT_SCALE_X = 46
        DEFAULT_SCALE_Y = 74
        DEFAULT_FIELD_FONT_SIZE = 11
        DEFAULT_CARD_FONT_SIZE = 11

        FPS = 20
        typed_word = ''
        reset_word = 'reset12345'
        reset_discarded_word = 'reset54321'

        player_id = network.get_player_id()
        players = network.get_player_list()
        player_levels = network.get_player_levels()

        player_selected = -1
        player_hover = -1

        pygame.init()
        screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("munchkin")
        clock = pygame.time.Clock()

        # Ajuste da janela no Windows
        user32 = windll.user32
        ShowWindow = user32.ShowWindow
        wm_info = pygame.display.get_wm_info()['window']
        ShowWindow(wm_info, 3)

        SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()

        scale_x = int(DEFAULT_SCALE_X * SCREEN_WIDTH / DEFAULT_WIDTH)
        scale_y = int(DEFAULT_SCALE_Y * SCREEN_HEIGHT / DEFAULT_HEIGHT)
        FIELD_FONT_SIZE = int(DEFAULT_FIELD_FONT_SIZE * SCREEN_WIDTH / DEFAULT_WIDTH)
        CARD_FONT_SIZE = int(DEFAULT_CARD_FONT_SIZE * SCREEN_HEIGHT / DEFAULT_HEIGHT)

        x_limits = [x * SCREEN_WIDTH for x in X_LIMITS_DEFAULT]
        y_limits = [y * SCREEN_HEIGHT for y in Y_LIMITS_DEFAULT]
        w_players = W_PLAYERS_DEFAULT * SCREEN_WIDTH
        h_players = H_PLAYERS_DEFAULT * SCREEN_HEIGHT

        table_class = Table(SCREEN_WIDTH, SCREEN_HEIGHT, player_id, x_limits, y_limits, FIELD_FONT_SIZE)
        cards_info = network.get_all_cards()

        cards_class = Cards(SCREEN_WIDTH, SCREEN_HEIGHT, cards_info, scale_x, scale_y, table_class.get_rect('deck'), CARD_FONT_SIZE)
        cards_class.set_draw_interact(player_selected, player_hover, player_id)

        players_class = Players(players, player_levels, w_players, h_players, FIELD_FONT_SIZE)
        scores_class = Scores(x_limits[0], SCREEN_WIDTH, SCREEN_HEIGHT, FIELD_FONT_SIZE)

        # Verificar se o jogador atual é IA
        is_ai = False
        ai_player = None
        if player_id == "AI_PLAYER_ID":  # Ajuste o ID do jogador IA
            is_ai = True
            ai_player = AIPlayer(players, player_levels, w_players, h_players, FIELD_FONT_SIZE)

        running = True

        while running:
            action = None
            caller(cards_class, 'set_draw_interact', [player_selected, player_hover, player_id], cards_class_lock)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    network.send({'message_type': 'quit'})
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if caller(table_class, 'get_collidepoint', ['players', event.pos], table_class_lock):
                            player_selected = caller(players_class, 'focused', [pygame.mouse.get_pos(), 'select'], players_class_lock)
                        if caller(table_class, 'get_collidepoint', ['logs', event.pos], table_class_lock):
                            dice_result = caller(table_class, 'dice_roll', [None], table_class_lock)
                            network.send({'message_type': 'dice_roll', 'message': dice_result})
                        action = caller(cards_class, 'click', [event.pos, player_id], cards_class_lock)

                    if event.button == 3 and not pygame.mouse.get_pressed()[0]:
                        action = caller(cards_class, 'reveal', [event.pos], cards_class_lock)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        action = caller(cards_class, 'release', [event.pos, caller(table_class, 'get_rect', ['equipments'], table_class_lock), caller(table_class, 'get_rect', ['table'], table_class_lock), caller(table_class, 'get_rect', ['hand'], table_class_lock)], cards_class_lock)

                elif event.type == pygame.MOUSEMOTION:
                    if caller(table_class, 'get_collidepoint', ['players', event.pos], table_class_lock):
                        player_hover = caller(players_class, 'focused', [pygame.mouse.get_pos(), 'hover'], players_class_lock)
                        caller(cards_class, 'set_draw_interact', [player_selected, player_hover, player_id], cards_class_lock)
                    elif not caller(table_class, 'get_collidepoint', ['equipments', event.pos], table_class_lock):
                        if player_hover != -1 or player_selected != -1:
                            player_hover = -1
                            player_selected = -1
                            caller(players_class, 'clear', [], players_class_lock)
                            caller(cards_class, 'set_draw_interact', [player_selected, player_hover, player_id], cards_class_lock)
                    action = caller(cards_class, 'hover', [event.pos], cards_class_lock)

            if is_ai:
                ai_action = ai_player.make_move()
                network.send(ai_action)
            
            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()
    except Exception as e:
        print('play error', e)
        network.send({'message_type': 'quit'})
        raise e

def main(network):
    try:
        # Inicializa e começa a escutar e jogar em threads separadas
        listen_thread = threading.Thread(target=listen, args=(network,))
        play_thread = threading.Thread(target=play, args=(network,))
        
        listen_thread.start()
        play_thread.start()
        
        listen_thread.join()
        play_thread.join()
        
    except Exception as e:
        print(f"Erro ao iniciar o jogo: {e}")