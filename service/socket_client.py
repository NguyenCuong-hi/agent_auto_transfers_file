import socket
import time
import os

class ConnectionSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_socket(self, retry = 5, delay = 5):
        attemp = 0
        while attemp < retry:
            try:

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.host, self.port))
                return sock
            except socket.error as e:
                print(f"Failed to connect to {self.host}:{self.port} due to error: {e}")
            attemp += 1
            print(f"Retrying... ({attemp}/{retry})")
            time.sleep(delay)
        return None
        
    
    def send_file(self, sock, file_path):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            sock.send(file_name.encode())
            sock.send(str(file_size).encode())
            with open(file_path, 'r', encoding='utf-8') as file:
                c = 0
                while c < file_size:
                    chunk = file.read()
                    if not chunk:
                        break
                    sock.send(chunk.encode('utf-8'))
                    c += len(chunk)
                    print(f"Transferring: {file_path}...")
            print(f"Transfer {file_path} successful.")
            sock.close()
        except Exception as e:
            print(f"\nAn error current transfer file: {e}")
            sock.close()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
