import socket
import threading
import json
from questions import questionsC1, questionsC2

# persistência dos rankings
RANKING_FILE = 'rankings.json'

QUIZZES = {
    "REDES_C1": questionsC1,
    "REDES_C2": questionsC2
}

# FUNCAO PARA CARREGAR O ARQUIVO .JSON.
def load_rankings():
    try:
        with open(RANKING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# FUNCAO QUE  SALVA DICIONÁRIO DE RANKINGS NO .JSON
def save_rankings(rankings_data):
    with open(RANKING_FILE, 'w') as f:
        json.dump(rankings_data, f, indent=4)

rankings = load_rankings()
ranking_lock = threading.Lock() # lock para proteger o acesso concorrente ao ranking

# FUNCAO PARA GERENCIAR A CONEXAO DE UM UNICO CLIENTE
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    player_name = "Convidado"
    score = 0
    selected_quiz = None

    try:
        # 1. Espera a primeira mensagem do cliente
        init_message = conn.recv(1024).decode()

        # protocolo pedir ranking
        if init_message.startswith("PEDIR_RANKING"):
            parts = init_message.split(':')
            if len(parts) == 2:
                quiz_id_req = parts[1]
                with ranking_lock:
                    # Pega o ranking específico para o quiz solicitado
                    specific_ranking = rankings.get(quiz_id_req, [])
                    if not specific_ranking:
                        ranking_str = "" # Envia string vazia se o ranking não existir
                    else:
                        ranking_str = ";".join([f"{name}:{pts}" for name, pts in specific_ranking])
                conn.sendall(f"RANKING:{ranking_str}\n".encode())
            return

        # Lógica original para iniciar o quiz
        parts = init_message.split(':')
        if parts[0] == "INICIAR_QUIZ" and len(parts) == 3:
            quiz_id = parts[1]
            player_name = parts[2]
            if quiz_id in QUIZZES:
                selected_quiz = QUIZZES[quiz_id]
                conn.sendall(b"BEM_VINDO\n")
            else:
                conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO\n")
                return # Encerra a thread
        else:
            return

        # 2. Loop principal do Quiz
        for i, q in enumerate(selected_quiz):
            # Formata a mensagem da pergunta conforme o protocolo
            options_str = ":".join(q["options"].values())
            question_msg = f"PERGUNTA:{i+1}:{q['question']}:{options_str}"
            conn.sendall(question_msg.encode()+ b'\n')

            # Aguarda a resposta do cliente
            answer_msg = conn.recv(1024).decode() 
            answer_parts = answer_msg.split(':')
            user_answer = answer_parts[2]

            if user_answer == q["answer"]:
                score += 1
                conn.sendall(b"RESULTADO_CORRETO\n")
            else:
                conn.sendall(b"RESULTADO_INCORRETO\n")

        # 3. Fim do Quiz
        conn.sendall(b"FIM_DE_JOGO\n")
        
        # --- LÓGICA DE ATUALIZAÇÃO DO RANKING ---
        with ranking_lock:
            specific_quiz_ranking = rankings.get(quiz_id, [])
            
            player_found = False
            # Itera sobre o ranking para encontrar o jogador
            for i, (name, old_score) in enumerate(specific_quiz_ranking):
                if name == player_name:
                    player_found = True
                    # Se a nova pontuação for maior, atualiza a entrada existente
                    if score > old_score:
                        specific_quiz_ranking[i] = (player_name, score)
                    # Se for igual ou menor, não faz nada e sai do loop
                    break
            
            # Se o jogador não foi encontrado na lista, adiciona como novo
            if not player_found:
                specific_quiz_ranking.append((player_name, score))

            # Reordena o ranking pela pontuação (maior para menor)
            specific_quiz_ranking.sort(key=lambda item: item[1], reverse=True)
            
            # Atualiza o dicionário principal e salva no arquivo
            rankings[quiz_id] = specific_quiz_ranking
            save_rankings(rankings)

        # 4. Aguarda comandos finais (PONTUACAO, RANKING)
        while True:
            final_command = conn.recv(1024).decode()
            if final_command == "PEDIR_PONTUACAO":
                conn.sendall(f"PONTUACAO_FINAL:{score}\n".encode())
            elif final_command == "PEDIR_RANKING":
                with ranking_lock:
                    ranking_str = ";".join([f"{name}:{pts}" for name, pts in rankings.get(quiz_id, [])])
                conn.sendall(f"RANKING:{ranking_str}\n".encode())
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