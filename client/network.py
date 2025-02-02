import socket
import pickle
import threading

class Network:
    def __init__(self, player_name, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = port
        self.addr = (self.server, self.port)
        self.bytes_message = b''
        self.buffersize = 1024
        self.footersize = 10  # endmessage
        self.lock = threading.Lock()
        self.p = self.connect(player_name)

    def connect(self, player_name):
        try:
            self.client.connect(self.addr)
            self.send(player_name)
            return self.process()
        except Exception as e:
            print('NETWORK 1', e)
            self.send({'message_type': 'quit'})
            raise e

    def send(self, message):
        with self.lock:
            try:
                to_send = pickle.dumps(message) + bytes(f'endmessage', "utf-8")
                self.client.send(to_send)
            except Exception as e:
                print('NETWORK 2', e)
                raise e

    def receive(self):
        try:
            if len(self.bytes_message) > 0:
                return self.process()
            else:
                self.bytes_message = self.client.recv(self.buffersize)
                return self.process()
        except Exception as e:
            print('NETWORK 3', e)
            self.send({'message_type': 'quit'})
            raise e

    def get_all_cards(self):
        try:
            self.client.send(pickle.dumps({'message_type': 'init'}) + bytes(f'endmessage', "utf-8"))
        except Exception as e:
            print('NETWORK 4', e)
            self.send({'message_type': 'quit'})
            raise e

        cards_info = {'message_type': ''}
        while 'message_type' not in cards_info:
            print('trying to init cards')
            cards_info = self.process()
        return cards_info

    def get_player_id(self):
        return self.p['player_id']

    def get_player_list(self):
        return self.p['players']
    
    def get_player_levels(self):
        return self.p['levels']
    
    def process(self):
        try:
            while self.bytes_message.find(b'endmessage') == -1:
                new_msg = self.client.recv(self.buffersize)
                self.bytes_message += new_msg
            to_return = self.bytes_message[:self.bytes_message.find(b'endmessage')]
            self.bytes_message = self.bytes_message[self.bytes_message.find(b'endmessage') + self.footersize:]
            return pickle.loads(to_return)
        except Exception as e:
            print('NETWORK 5', e)
            self.send({'message_type': 'quit'})
            raise e

    def disconnect(self):
        try:
            self.client.close()
        except Exception as e:
            print('NETWORK 6', e)
            raise e
