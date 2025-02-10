import sys
import TouchPortalAPI as TP
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QStatusBar
from PyQt5.QtCore import Qt

PLUGIN_ID = "TouchPortalDeck"
__version__ = "1.0"

class DeckUI(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
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
                    QPushButton:pressed {
                        background-color: #666;
                    }
                """)
                btn.clicked.connect(lambda _, n=row*3+col+1: self.on_button_click(n))
                layout.addWidget(btn, row, col)
                self.buttons.append(btn)

    def on_button_click(self, number):
        self.status_bar.showMessage(f"Button {number} pressed")
        self.client.stateUpdate(f"{PLUGIN_ID}.button.{number}", "pressed")

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
    app = QApplication(sys.argv)
    ui = DeckUI(TPClient)
    ui.show()
    app.exec_()

@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    if (action_data := data.get('data')):
        print(f"Action received: {action_data}")

@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(f"Error: {exc}")

def main():
    try:
        TPClient.connect()
        return 0
    except Exception as e:
        print(f"Exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
