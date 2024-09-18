from PyQt5.QtCore import  pyqtSignal, QObject
import subprocess
import threading
import time

class PingChecker(QObject):
    ping_result = pyqtSignal(str)

    def __init__(self, lbl_checking):
        super().__init__()
        self.lbl_checking = lbl_checking
        self.ping_result.connect(self.update_ui)
        self.running = False

    def check_ping(self, hostname):
        self.running = True
        def ping():
            while self.running:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                response = subprocess.call(
                    ["ping", "-n", "1", hostname], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    startupinfo=startupinfo
                )
                
                if response == 0:
                    color = 'green'
                else:
                    color = 'red'

                self.ping_result.emit(color)
                time.sleep(5)

        threading.Thread(target=ping, daemon=True).start()

    def update_ui(self, color):
        self.lbl_checking.setStyleSheet(f"background-color: {color};")
