import json
import socket
import struct
import sys
import TouchPortalAPI as TP
from threading import Thread
import time


PLUGIN_ID = "TouchPortalDeck"

TPClient = TP.Client(
    pluginId = PLUGIN_ID,
    sleepPeriod = 0.05,
    autoClose = True,
    checkPluginId = True,
    maxWorkers = 4
)


@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    print(f"Connected to TP v{data.get('tpVersionString', '?')}")

@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    if (action_data := data.get('data')):
        print(f"Action received: {action_data}")

def main():
    TPClient.connect()
    return 0

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
        while self.running:
            try:
                data = self.socket.recv(1024)
                if data:
                    print(f"Received binary: {data.hex()}")
                    # Handle initial handshake
                    if data.hex() == "1503030002020a":
                        response = struct.pack('!BBBB', 0x02, 0x00, 0x02, 0x0a)
                        self.socket.send(response)
                        print("Sent handshake response")
                        # Send additional pairing info
                        self.send({
                            "type": "pair",
                            "id": "TouchPortalDeck",
                            "version": 1
                        })
                    else:
                        # Handle regular messages
                        try:
                            message = json.loads(data.decode())
                            print(f"Received message: {message}")
                            self.handle_message(message)
                        except:
                            print(f"Raw data: {data.hex()}")
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

if __name__ == "__main__":
    sys.exit(main())
