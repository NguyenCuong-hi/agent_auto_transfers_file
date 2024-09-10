import socket
import time


def connection_socket(file_path, client_socket):
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client_socket.sendall(data)
    client_socket.close()


def checking_connect_to_server(HOST, PORT, timeout=5, retry_interval=5):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.settimeout(timeout)
            s.connect((HOST, PORT))

            print(f"Connected to {HOST}:{PORT}")
        except socket.timeout:
            print(f"Connection to {HOST}:{PORT} timed out. Retrying in {retry_interval} seconds...")
        except socket.error as e:
            print(f"Error connecting to {HOST}:{PORT}: {e}. Retrying in {retry_interval} seconds...")
        time.sleep(retry_interval)
