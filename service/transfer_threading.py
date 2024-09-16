import os
import socket
import time

from PyQt5.QtCore import QThread, pyqtSignal
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from socket_client import send_file_socket


class TransferThread(QThread):
    transfer_progress = pyqtSignal(str)

    def __init__(self, host, port, file_path, callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.callback = callback
        self.file_path = file_path
        self.running = True
        self.max_retries = 3
        self.retry_interval = 5

    def run(self):
        if not os.path.exists(self.file_path):
            self.transfer_progress.emit(f"File {self.file_path} not exist.")
            print(f"File {self.file_path} not exist.")
            return

        retries = 0
        while retries < self.max_retries and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                self.transfer_progress.emit(f"Connection to {self.host}:{self.port} successful.")
                print(f"Connection to {self.host}:{self.port} successful.")

                self.send_file(sock, self.file_path)

            except socket.error as e:
                retries += 1
                self.transfer_progress.emit(f"Connection failed ({retries}/{self.max_retries}): {e}")
                print(f"Connection failed ({retries}/{self.max_retries}): {e}")

                if retries < self.max_retries:
                    self.transfer_progress.emit(f"Retrying in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    self.transfer_progress.emit("Maximum retry attempts reached. Transfer failed.")
                    print("Maximum retry attempts reached. Transfer failed.")

    def send_file(self, sock, file_path):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            sock.send(f"{file_name}|{file_size}".encode('utf-8'))
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    sock.sendall(chunk.endcode('utf-8'))
                    self.transfer_progress.emit(f"\nTransferring: {file_path}...")
                    print(f"Transferring: {file_path}...")
            self.transfer_progress.emit(f"\nTransfer {file_path} successful.")
            print(f"Transfer {file_path} successful.")
        except Exception as e:
            self.transfer_progress.emit(f"\nAn error current transfer file: {e}")
            print(f"\nAn error current transfer file: {e}")

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


def load_existing_files(directory, socket):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            send_file_socket(file_path=file_path, client_socket=socket)
