import json
import socket
import struct
import sys
from threading import Thread

class TouchPortalPlugin:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.connect()
        
    def connect(self):
        try:
            self.socket.connect(('127.0.0.1', 12136))
            print("Connected to Touch Portal")
            self.pair()
            self.start_listening()
        except Exception as e:
            print(f"Connection error: {str(e)}")
            
    def pair(self):
        self.send({
            'type': 'pair',
            'id': 'TouchPortalDeck'
        })
        
    def send(self, data):
        try:
            message = json.dumps(data)
            self.socket.send(struct.pack('!L', len(message)))
            self.socket.send(message.encode())
        except Exception as e:
            print(f"Send error: {str(e)}")
            
    def start_listening(self):
        Thread(target=self.listen_loop).start()
            
    def listen_loop(self):
        while self.running:
            try:
                data = self.socket.recv(8)
                if data:
                    size = struct.unpack('!L', data[:4])[0]
                    data = self.socket.recv(size)
                    message = json.loads(data)
                    self.handle_message(message)
            except:
                print("Connection lost")
                break
                
    def handle_message(self, message):
        print(f"Received: {message}")
        
    def run(self):
        try:
            while self.running:
                pass
        except KeyboardInterrupt:
            self.running = False
            self.socket.close()

def main():
    plugin = TouchPortalPlugin()
    plugin.run()

if __name__ == '__main__':
    main()