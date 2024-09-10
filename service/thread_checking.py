from PyQt5.QtCore import QThread, pyqtSignal
import socket
import time


class ConnectionChecker(QThread):
    connection_status = pyqtSignal(bool)

    def __init__(self, host, port, timeout=5, retry_interval=5):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.running = True

    def run(self):
        connection_established = False
        sock = None

        while self.running:
            if not connection_established:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.timeout)
                    sock.connect((self.host, self.port))
                    connection_established = True
                    print(f"Connected to {self.host}:{self.port}")
                    self.connection_status.emit(True)

                except socket.timeout:
                    print(
                        f"Connection to {self.host}:{self.port} timed out. Retrying in {self.retry_interval} seconds...")
                    self.connection_status.emit(False)
                except socket.error as e:
                    print(
                        f"Error connecting to {self.host}:{self.port}: {e}. Retrying in {self.retry_interval} seconds...")
                    self.connection_status.emit(False)

            else:
                try:
                    sock.send(b'PING')
                    print(f"Connection is alive with {self.host}:{self.port}")
                    self.connection_status.emit(True)
                except socket.error as e:
                    print(f"Connection lost: {e}. Attempting to reconnect...")
                    connection_established = False
                    sock.close()
                    self.connection_status.emit(False)

            time.sleep(self.retry_interval)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
