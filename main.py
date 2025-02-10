import json
import socket
import struct
import sys
from threading import Thread
import time

class TouchPortalPlugin:
    def __init__(self):
        print("Starting Touch Portal Plugin...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.connect()
        
    def connect(self):
        print("Attempting to connect to Touch Portal...")
        try:
            self.socket.connect(('192.168.0.26', 12135))
            print("Connected to Touch Portal")
            self.pair()
            self.start_listening()
        except Exception as e:
            print(f"Connection error: {str(e)}")
            time.sleep(5)  # Wait 5 seconds before retry
            self.connect()
            
    def pair(self):
        print("Sending pair request...")
        self.send({
            'type': 'pair',
            'id': 'TouchPortalDeck'
        })
        print("Pair request sent")
        
    def send(self, data):
        try:
            message = json.dumps(data)
            self.socket.send(struct.pack('!L', len(message)))
            self.socket.send(message.encode())
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Send error: {str(e)}")
            
    def start_listening(self):
        print("Starting listener thread...")
        Thread(target=self.listen_loop).start()
            
    def listen_loop(self):
        print("Starting listen loop...")
        while self.running:
            try:
                # Read message length (4 bytes)
                length_bytes = bytearray()
                while len(length_bytes) < 4:
                    byte = self.socket.recv(1)
                    if byte:
                        length_bytes.extend(byte)
                
                # Read actual message
                message_bytes = bytearray()
                message_length = struct.unpack('!L', length_bytes)[0]
                
                if 0 < message_length < 1024:  # Reasonable message size
                    while len(message_bytes) < message_length:
                        chunk = self.socket.recv(message_length - len(message_bytes))
                        if chunk:
                            message_bytes.extend(chunk)
                    
                    try:
                        message = json.loads(message_bytes.decode())
                        print(f"Received message: {message}")
                        self.handle_message(message)
                    except json.JSONDecodeError:
                        print(f"Raw data: {message_bytes.hex()}")
                else:
                    print("Resetting connection - invalid message size")
                    self.socket.close()
                    self.connect()
                    break
                    
            except Exception as e:
                print(f"Connection reset: {str(e)}")
                self.connect()
                break    
    def handle_message(self, message):
        print(f"Handling message: {message}")
        if message.get('type') == 'action':
            print(f"Action received: {message}")
        
    def run(self):
        print("Plugin running, press Ctrl+C to stop")
        try:
            while self.running:
                time.sleep(1)  # Prevent CPU hogging
        except KeyboardInterrupt:
            print("Shutting down...")
            self.running = False
            self.socket.close()

def main():
    plugin = TouchPortalPlugin()
    plugin.run()

if __name__ == '__main__':
    main()
