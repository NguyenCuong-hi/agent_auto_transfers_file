from PyQt5.QtCore import QThread, pyqtSignal
import socket
import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
from socket_client import send_file_socket

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


class FileDetection(FileSystemEventHandler):
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def on_created(self, event):
        if not event.is_directory:
            new_file = event.src_path
            transfer_thread = TransferThread(host=self.host, port=self.port, file_path=new_file)
            transfer_thread.stop()
            


class DirectoryMonitorThread(QThread):
    file_added = pyqtSignal(str)
    
    def __init__(self, directory, host, port):
        super().__init__()
        self.directory = directory
        self.host = host
        self.port = port
        self.observer = None

    def run(self):
        event_handler = FileDetection(host=self.host, port=self.port)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()

    def stop(self):
        if self.observer:
            self.observer.stop()

def load_existing_files(directory, file_list, socket):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path not in file_list:
                send_file_socket(file_path=file_path, client_socket=socket)
                                            
