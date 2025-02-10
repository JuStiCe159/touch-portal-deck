import json
import socket
import struct
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QStatusBar
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import sys

class ConnectionHandler(QThread):
    status_changed = pyqtSignal(str, bool)  # message, is_connected
    data_received = pyqtSignal(dict)
    
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.running = True
        
    def run(self):
        self.status_changed.emit("Connected to Touch Portal", True)
        while self.running:
            try:
                data = self.socket.recv(8)
                if data:
                    size = struct.unpack('!L', data[:4])[0]
                    data = self.socket.recv(size)
                    message = json.loads(data)
                    self.data_received.emit(message)
            except:
                self.status_changed.emit("Connection lost - Retrying...", False)
                break

class DeckUI(QMainWindow):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('Touch Portal Deck')
        self.setGeometry(100, 100, 400, 450)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)
        
        self.buttons = []
        for row in range(3):
            for col in range(3):
                btn = QPushButton(f"{row*3 + col + 1}")
                btn.setMinimumSize(100, 100)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #333;
                        color: white;
                        border: 2px solid #555;
                        border-radius: 10px;
                        font-size: 24px;
                    }
                    QPushButton:disabled {
                        background-color: #222;
                        border-color: #444;
                    }
                """)
                btn.clicked.connect(lambda _, n=row*3+col+1: self.on_button_click(n))
                layout.addWidget(btn, row, col)
                self.buttons.append(btn)
                
    def update_status(self, message, connected):
        self.status_bar.showMessage(message)
        color = "#4CAF50" if connected else "#F44336"
        self.status_bar.setStyleSheet(f"background-color: {color}")
        for btn in self.buttons:
            btn.setEnabled(connected)

    def on_button_click(self, number):
        self.plugin.send({
            'type': 'action',
            'actionId': 'deck_button',
            'data': [{'value': str(number)}]
        })
        # Visual feedback
        btn = self.buttons[number-1]
        original_style = btn.styleSheet()
        btn.setStyleSheet(original_style + "background-color: #4CAF50;")
        QTimer.singleShot(200, lambda: btn.setStyleSheet(original_style))

class TouchPortalPlugin:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ui = DeckUI(self)
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.socket.connect(('127.0.0.1', 12136))
            self.connection = ConnectionHandler(self.socket)
            self.connection.status_changed.connect(self.ui.update_status)
            self.connection.start()
            self.pair()
        except Exception as e:
            self.ui.update_status(f"Connection error: {str(e)}", False)
            QTimer.singleShot(5000, self.connect)
            
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
            self.ui.update_status(f"Send error: {str(e)}", False)
            
    def run(self):
        self.ui.show()
        self.app.exec_()

def main():
    plugin = TouchPortalPlugin()
    plugin.run()

if __name__ == '__main__':
    main()