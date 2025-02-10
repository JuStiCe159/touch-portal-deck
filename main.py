import json
import socket
import struct
import sys
from threading import Thread
import time

class TouchPortalPlugin:
    def __init__(self):
        print("Starting Touch Portal Plugin...")
        self.running = True
        self.connect()
        
    def connect(self):
        while self.running:
            try:
                print("Attempting to connect to Touch Portal...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(('192.168.0.26', 12135))
                print("Connected to Touch Portal")
                self.pair()
                self.start_listening()
                break
            except Exception as e:
                print(f"Connection error: {str(e)}")
                time.sleep(5)
            
    def pair(self):
        print("Sending pair request...")
        self.send({
            'type': 'pair',
            'id': 'TouchPortalDeck'
        })
        print("Pair request sent")
        
    def send(self, data):
        message = json.dumps(data)
        self.socket.send(message.encode() + b'\n')
        print(f"Sent message: {message}")
            
    def start_listening(self):
        print("Starting listener thread...")
        Thread(target=self.listen_loop).start()
            
    def listen_loop(self):
        print("Starting listen loop...")
        buffer = bytearray()
        while self.running:
            try:
                chunk = self.socket.recv(1024)
                if chunk:
                    buffer.extend(chunk)
                    if len(buffer) >= 4:
                        # Process binary protocol
                        print(f"Processing binary data: {buffer.hex()}")
                        # Send acknowledgment
                        self.socket.send(b'\x02\x00')
                        buffer.clear()
                else:
                    print("Reconnecting...")
                    if self.running:
                        self.connect()
                    break
            except Exception as e:
                print(f"Listen error: {str(e)}")
                if self.running:
                    self.connect()
                break   
    def handle_message(self, message):
        print(f"Handling message: {message}")
        
    def run(self):
        print("Plugin running, press Ctrl+C to stop")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
            self.running = False
            self.socket.close()

def main():
    plugin = TouchPortalPlugin()
    plugin.run()

if __name__ == '__main__':
    main()
