import socket
import threading
from client_handler import handle_client


HOST = '127.0.0.1' 
PORT = 1100

def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[INICIADO] Servidor escutando em {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[DESLIGANDO] Servidor sendo desligado...")
        server_socket.close()

if __name__ == "__main__":
    start_server()