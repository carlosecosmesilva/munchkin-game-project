import random
import socket
from _thread import *
import pickle
import threading
import time

# Defina o número máximo de jogadores
MAX_PLAYERS = 4
MAX_WAIT_TIME = 10  # Tempo máximo de espera em segundos para jogadores humanos

# ONLINE
server = ""
port = 3389

# LOCAL
# server = "IP_DA_SUA_REDE"
# port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print('SERVER 1', str(e))

s.listen(5)
print("Waiting for a connection, Server Started")

conn_lock = threading.Lock()
ids_lock = threading.Lock()
cards_lock = threading.Lock()
level_lock = threading.Lock()

cards = {}

# Função para simular um jogador IA
def simulate_ai_player():
    ai_player_id = f'IA_{random.randint(1, 100)}'
    print(f'Jogador IA {ai_player_id} entrou no jogo.')
    return ai_player_id

def init_cards(cards):
    for i in range(280):
        cards[i] = {
                'x': 0.404,
                'y': 0.7575,
                'p_id': -1,
                'draging': False,
                'order': 0,
                'face': False,
                'area': 'deck',
                'discarded': False
        }
        if i >= 140:
            cards[i]['x'] = 0.504

def reset_discarded_cards(cards):
    for i in range(280):
        if cards[i]['discarded']:
            cards[i] = {
                    'x': 0.404,
                    'y': 0.7575,
                    'p_id': -1,
                    'draging': False,
                    'order': 0,
                    'face': False,
                    'area': 'deck',
                    'discarded': False
            }
            if i >= 140:
                cards[i]['x'] = 0.504

def discard_player_cards(player, cards):
    for c_id, card in cards.items():
        if card['p_id'] == player and ((not card['discarded'] and card['area'] in ['hand', 'equipments']) or card['draging']):
            card['x'] = 0.604
            if c_id >= 140:
                card['x'] = 0.704
            card['y'] = 0.7575
            card['draging'] = False
            card['face'] = True
            card['area'] = 'deck'
            card['discarded'] = True

def set_player_cards(player, cards):
    for c_id, card in cards.items():
        if card['p_id'] == player and card['discarded']:
            card['x'] = 0.004
            card['y'] = 0.7575
            card['draging'] = False
            card['face'] = True
            card['area'] = 'hand'
            card['discarded'] = False

init_cards(cards)

clients = []
ids = []
player_levels = {}
def threaded_client(conn):
    global cards
    bytes_message = b''
    buffersize = 1024
    footersize = 10 #endmessage
    # criar variavel footer com endmessage

    while bytes_message.find(b'endmessage') == -1:
        try:
            data = conn.recv(buffersize)
        except Exception as e:
            print('SERVER 2', e)
            with conn_lock:
                clients.remove(conn)
            try:
                conn.close()
            except Exception as e:
                print('SERVER 2.1', e)
            return # ate aqui o id não foi enviado e o cliente não pegou cartas ainda

        bytes_message += data
    data = bytes_message[:bytes_message.find(b'endmessage')]
    player = pickle.loads(data)
    bytes_message = bytes_message[bytes_message.find(b'endmessage') + footersize:]

    if player in ids:
        count = 1
        while(player + str(count)) in ids:
            count += 1
        player = player + str(count)

    with ids_lock:
        with conn_lock:
            ids.append(player)
            with level_lock:
                if not player in player_levels:
                    player_levels[player] = '1'
                try:
                    conn.send(pickle.dumps({'player_id': player, 'players': ids, 'levels': player_levels}) + bytes(f'endmessage', "utf-8"))
                except Exception as e:
                    print('SERVER 3', e)

    with conn_lock:
        for c in clients:
            if c == conn:
                continue
            with level_lock:
                message = {'message_type': 'players_update', 'message': {'player': player, 'levels': player_levels}} # aqui devolver a carta pro player nos clientes
            try:
                c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
            except Exception as e:
                print('SERVER 4', e)

    set_player_cards(player, cards)

    while True:
        try:
            while bytes_message.find(b'endmessage') == -1:
                try:
                    try:
                        data = conn.recv(buffersize)
                    except:
                        # print('server sending heartbeat')
                        message = {'message_type': 'heartbeat'}
                        conn.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                        data = conn.recv(buffersize)
                        # print('server receiving heartbeat')
                except Exception as e:
                    print('SERVER 5', player, e)
                    with conn_lock:
                        clients.remove(conn)
                        for c in clients:
                            message = {'message_type': 'player_disconnected', 'message': player}
                            try:
                                c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                            except Exception as e:
                                print('SERVER 2.2', e)
                    with ids_lock:
                        ids.remove(player)
                    try:
                        conn.close()
                    except Exception as e:
                        print('SERVER 2.1', e)
                    with cards_lock:
                        discard_player_cards(player, cards)
                    return

                bytes_message += data
            data = bytes_message[:bytes_message.find(b'endmessage')]
            data = pickle.loads(data)
            bytes_message = bytes_message[bytes_message.find(b'endmessage') + footersize:]
            if data['message_type'] == 'init':
                with conn_lock:
                    with cards_lock:
                        try:
                            conn.sendall(pickle.dumps(cards) + bytes(f'endmessage', "utf-8"))
                        except Exception as e:
                            print('SERVER 6', e)

            elif data['message_type'] == 'quit':
                with cards_lock:
                    discard_player_cards(player, cards)
                break

            elif data['message_type'] == 'score_update':
                with conn_lock:
                    for c in clients:
                        if c == conn:
                            continue
                        message = {'message_type': 'score_update', 'message': data['message']}
                        try:
                            c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                        except Exception as e:
                            print('SERVER 6.1', e)

            elif data['message_type'] == 'level_update':
                with conn_lock:
                    with level_lock:
                        player_levels[data['message']['player']] = data['message']['level']
                        for c in clients:
                            if c == conn:
                                continue
                            message = {'message_type': 'level_update', 'message': {'player': data['message']['player'], 'level': data['message']['level']}}
                            try:
                                c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                            except Exception as e:
                                print('SERVER 6.2', e)

            elif data['message_type'] == 'reset_game':
                with cards_lock:
                    init_cards(cards)
                with conn_lock:
                    for c in clients:
                        if c == conn:
                            continue
                        message = {'message_type': 'reset_game', 'message': data['message']}
                        try:
                            c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                        except Exception as e:
                            print('SERVER 7', e)

            elif data['message_type'] == 'reset_discarded':
                with cards_lock:
                    reset_discarded_cards(cards)
                with conn_lock:
                    for c in clients:
                        if c == conn:
                            continue
                        message = {'message_type': 'reset_discarded', 'message': data['message']}
                        try:
                            c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                        except Exception as e:
                            print('SERVER 7.1', e)

            elif data['message_type'] == 'dice_roll':
                with conn_lock:
                    for c in clients:
                        if c == conn:
                            continue
                        message = {'message_type': 'dice_roll', 'message': data['message']}
                        try:
                            c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                        except Exception as e:
                            print('SERVER 8', e)

            elif data['message_type'] == 'card_update':
                    with cards_lock:
                        cards[data['message']['id']] = data['message']['data']
                    with conn_lock:
                        for c in clients:
                            if c == conn:
                                continue
                            message = {'message_type': 'card_update', 'message': data['message']}
                            try:
                                c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
                            except Exception as e:
                                print('SERVER 9', e)
        except Exception as e:
            print('SERVER 9.1', e)
            print(data)
            break

    print("Lost connection")
    # passar pra dentro do with lock abaixo
    with ids_lock:
        if player in ids: ids.remove(player)
    with conn_lock: #lock precisa do global?
        clients.remove(conn)
        message = {'message_type': 'self_disconnected'}
        try:
            conn.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
        except Exception as e:
            print('SERVER 10', e)
        for c in clients:
            message = {'message_type': 'player_disconnected', 'message': player}
            try:
                c.sendall(pickle.dumps(message) + bytes(f'endmessage', "utf-8"))
            except Exception as e:
                print('SERVER 11', e)
    try:
        conn.close()
    except Exception as e:
        print('SERVER 12', e)

while True:
    # Espera até que o número de jogadores seja menor que o máximo
    while len(clients) >= MAX_PLAYERS:
        print(f'Sala cheia! Esperando... (Jogadores atuais: {len(clients)})')
        time.sleep(3)

    print('Tamanho da sala: ', len(clients))

    start_time = time.time()  # Registra o tempo de início da espera
    conn, addr = s.accept()
    conn.settimeout(3)
    print("Conectado a:", addr)

    with conn_lock:
        clients.append(conn)

    # Verifica se há espaço na sala antes de adicionar o cliente
    if len(clients) <= MAX_PLAYERS:
        start_new_thread(threaded_client, (conn,))
    
    # Verifica o tempo de espera
    while len(clients) < MAX_PLAYERS and time.time() - start_time < MAX_WAIT_TIME:
        print(f'Aguardando mais jogadores... Tempo de espera: {int(time.time() - start_time)} segundos.')
        time.sleep(1)

    # Se não tiver jogadores suficientes após o tempo de espera, adicione IA
    if len(clients) < MAX_PLAYERS:
        print(f'Adicionando jogadores IA para completar a sala...')
        while len(clients) < MAX_PLAYERS:
            ai_player_id = simulate_ai_player()
            with conn_lock:
                # Simula a adição de um jogador IA. A IA deve ser configurada para agir automaticamente.
                # Aqui, vamos simplesmente adicionar um novo "jogador" à lista de conexões.
                clients.append(None)  # Adiciona um 'None' para IA, já que a IA não usa uma conexão real.
            # Simula o comportamento da IA com uma thread separada, se necessário.
            start_new_thread(threaded_client, (None,))  # Não passa conexão real para o IA, só como marcador.
        
    # Começa o jogo com os jogadores humanos e IA juntos
    if len(clients) == MAX_PLAYERS:
        print("Sala cheia com jogadores humanos e IA! O jogo começará.")