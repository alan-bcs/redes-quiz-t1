import socket
import threading
from questoesC1 import questions


QUIZZES = {
    "REDES_C1": questions
}
ranking = []
ranking_lock = threading.Lock() # Lock para proteger o acesso concorrente ao ranking

def handle_client(conn, addr): # funcao para gerenciar a conexão de um único cliente
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    player_name = "Convidado"
    score = 0
    selected_quiz = None

    try:
        # 1. Espera a primeira mensagem do cliente
        init_message = conn.recv(1024).decode()

        # protocolo pedir ranking
        if init_message == "PEDIR_RANKING":
            with ranking_lock:
                if not ranking:
                    ranking_str = "Ainda nao ha pontuacoes no ranking."
                else:
                    ranking_str = ";".join([f"{name}:{pts}" for name, pts in ranking])
            conn.sendall(f"RANKING:{ranking_str}".encode())
            return

        # Lógica original para iniciar o quiz
        parts = init_message.split(':')
        if parts[0] == "INICIAR_QUIZ" and len(parts) == 3:
            quiz_id = parts[1]
            player_name = parts[2]
            if quiz_id in QUIZZES:
                selected_quiz = QUIZZES[quiz_id]
                conn.sendall(b"BEM_VINDO")
            else:
                conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO")
                return # Encerra a thread
        else:
            return # Encerra se a primeira mensagem for inválida

        # 2. Loop principal do Quiz
        for i, q in enumerate(selected_quiz):
            # Formata a mensagem da pergunta conforme o protocolo
            options_str = ":".join(q["options"].values())
            question_msg = f"PERGUNTA:{i+1}:{q['question']}:{options_str}"
            conn.sendall(question_msg.encode())

            # Aguarda a resposta do cliente
            answer_msg = conn.recv(1024).decode() 
            answer_parts = answer_msg.split(':')
            user_answer = answer_parts[2]

            if user_answer == q["answer"]:
                score += 1
                conn.sendall(b"RESULTADO_CORRETO")
            else:
                conn.sendall(b"RESULTADO_INCORRETO")

        # 3. Fim do Quiz
        conn.sendall(b"FIM_DE_JOGO")
        
        # Adiciona ao ranking de forma segura
        with ranking_lock:
            ranking.append((player_name, score))
            ranking.sort(key=lambda item: item[1], reverse=True)

        # 4. Aguarda comandos finais (PONTUACAO, RANKING)
        while True:
            final_command = conn.recv(1024).decode()
            if final_command == "PEDIR_PONTUACAO":
                conn.sendall(f"PONTUACAO_FINAL:{score}".encode())
            elif final_command == "PEDIR_RANKING":
                with ranking_lock:
                    ranking_str = ";".join([f"{name}:{pts}" for name, pts in ranking])
                conn.sendall(f"RANKING:{ranking_str}".encode())
            elif not final_command:
                break

    except ConnectionResetError:
        print(f"[AVISO] Conexão com {addr} perdida inesperadamente.")
    finally:
        print(f"[CONEXÃO FECHADA] {addr}")
        conn.close()

def start_server():
    """Inicia o servidor e aguarda por conexões."""
    HOST = '127.0.0.1'
    PORT = 1100

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[INICIADO] Servidor escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()