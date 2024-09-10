from PyQt5.QtCore import QThread, pyqtSignal
import socket
from service.socket_client import connection_socket

import os


class TransferThread(QThread):
    transfer_progress = pyqtSignal(str)

    def __init__(self, host, port, file_path, callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.callback = callback
        self.file_path = file_path
        self.running = True

    def run(self):
        if not os.path.exists(self.file_path):
            self.transfer_progress.emit(f"File {self.file_path} not exist.")
            return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            self.transfer_progress.emit(f"Connecting to {self.host}:{self.port} successful.")

            self.send_file(sock, self.file_path)

        except socket.error as e:
            self.transfer_progress.emit(f"An error connection: {e}")
        finally:
            sock.close()

    def send_file(self, sock, file_path):
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    self.transfer_progress.emit(f"Transferring: {file_path}...")
            self.transfer_progress.emit(f"Transfer {file_path} successful.")
        except Exception as e:
            self.transfer_progress.emit(f"An error current transfer file: {e}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
