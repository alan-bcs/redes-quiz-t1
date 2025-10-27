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

# CONTROLE DE USUÁRIOS LOGADOS
logged_users = set()  # conjunto de nomes de usuários atualmente logados
users_lock = threading.Lock()  # lock para proteger o acesso concorrente aos usuários

# FUNCAO PARA CARREGAR O ARQUIVO .JSON.
def load_rankings():
    try:
        with open(RANKING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# FUNCAO QUE SALVA DICIONÁRIO DE RANKINGS NO .JSON
def save_rankings(rankings_data):
    with open(RANKING_FILE, 'w') as f:
        json.dump(rankings_data, f, indent=4)

rankings = load_rankings()
ranking_lock = threading.Lock()  # lock para proteger o acesso concorrente ao ranking

# FUNCAO PARA GERENCIAR A CONEXAO DE UM UNICO CLIENTE
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    player_name = None
    score = 0
    selected_quiz = None

    try:
        # 1. Espera a primeira mensagem do cliente (pode ser LOGIN ou PEDIR_RANKING)
        init_message = conn.recv(1024).decode().strip()

        # === PROTOCOLO DE LOGIN ===
        if init_message.startswith("LOGIN"):
            parts = init_message.split(':')
            if len(parts) == 2:
                requested_name = parts[1].strip()
                
                with users_lock:
                    # Verifica se o nome já está em uso
                    if requested_name in logged_users:
                        conn.sendall(b"LOGIN_NEGADO:NOME_EM_USO\n")
                        print(f"[LOGIN NEGADO] {addr} tentou usar o nome '{requested_name}' já em uso.")
                        return
                    else:
                        # Registra o usuário como logado
                        logged_users.add(requested_name)
                        player_name = requested_name
                        conn.sendall(b"LOGIN_ACEITO\n")
                        print(f"[LOGIN ACEITO] {addr} logado como '{player_name}'.")
                
                # Agora aguarda os próximos comandos do cliente já logado
                while True:
                    command = conn.recv(1024).decode().strip()
                    
                    if not command:
                        break
                    
                    # PROTOCOLO PEDIR RANKING
                    if command.startswith("PEDIR_RANKING"):
                        parts = command.split(':')
                        if len(parts) == 2:
                            quiz_id_req = parts[1]
                            with ranking_lock:
                                specific_ranking = rankings.get(quiz_id_req, [])
                                if not specific_ranking:
                                    ranking_str = ""
                                else:
                                    ranking_str = ";".join([f"{name}:{pts}" for name, pts in specific_ranking])
                            conn.sendall(f"RANKING:{ranking_str}\n".encode())
                    
                    # PROTOCOLO INICIAR QUIZ
                    elif command.startswith("INICIAR_QUIZ"):
                        parts = command.split(':')
                        if len(parts) == 2:
                            quiz_id = parts[1]
                            if quiz_id in QUIZZES:
                                selected_quiz = QUIZZES[quiz_id]
                                conn.sendall(b"BEM_VINDO\n")
                                
                                # Loop principal do Quiz
                                for i, q in enumerate(selected_quiz):
                                    options_str = ":".join(q["options"].values())
                                    question_msg = f"PERGUNTA:{i+1}:{q['question']}:{options_str}"
                                    conn.sendall(question_msg.encode() + b'\n')

                                    # Aguarda a resposta do cliente
                                    answer_msg = conn.recv(1024).decode()
                                    answer_parts = answer_msg.split(':')
                                    user_answer = answer_parts[2]

                                    if user_answer == q["answer"]:
                                        score += 1
                                        conn.sendall(b"RESULTADO_CORRETO\n")
                                    else:
                                        conn.sendall(b"RESULTADO_INCORRETO\n")

                                # Fim do Quiz
                                conn.sendall(b"FIM_DE_JOGO\n")
                                
                                # Atualização do ranking
                                with ranking_lock:
                                    specific_quiz_ranking = rankings.get(quiz_id, [])
                                    
                                    player_found = False
                                    for i, (name, old_score) in enumerate(specific_quiz_ranking):
                                        if name == player_name:
                                            player_found = True
                                            if score > old_score:
                                                specific_quiz_ranking[i] = (player_name, score)
                                            break
                                    
                                    if not player_found:
                                        specific_quiz_ranking.append((player_name, score))

                                    specific_quiz_ranking.sort(key=lambda item: item[1], reverse=True)
                                    rankings[quiz_id] = specific_quiz_ranking
                                    save_rankings(rankings)
                                
                                # Aguarda comandos finais (PONTUACAO, RANKING)
                                while True:
                                    final_command = conn.recv(1024).decode().strip()
                                    if final_command == "PEDIR_PONTUACAO":
                                        conn.sendall(f"PONTUACAO_FINAL:{score}\n".encode())
                                    elif final_command == "PEDIR_RANKING":
                                        with ranking_lock:
                                            ranking_str = ";".join([f"{name}:{pts}" for name, pts in rankings.get(quiz_id, [])])
                                        conn.sendall(f"RANKING:{ranking_str}\n".encode())
                                    elif final_command == "SAIR" or not final_command:
                                        break
                                
                                # Reseta o score para um novo quiz
                                score = 0
                            else:
                                conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO\n")
                    
                    elif command == "LOGOUT" or command == "SAIR":
                        break
            else:
                conn.sendall(b"ERRO:FORMATO_INVALIDO\n")
                return
        
        # PROTOCOLO PEDIR RANKING (sem login, para visualização rápida)
        elif init_message.startswith("PEDIR_RANKING"):
            parts = init_message.split(':')
            if len(parts) == 2:
                quiz_id_req = parts[1]
                with ranking_lock:
                    specific_ranking = rankings.get(quiz_id_req, [])
                    if not specific_ranking:
                        ranking_str = ""
                    else:
                        ranking_str = ";".join([f"{name}:{pts}" for name, pts in specific_ranking])
                conn.sendall(f"RANKING:{ranking_str}\n".encode())
            return

    except ConnectionResetError:
        print(f"[AVISO] Conexão com {addr} perdida inesperadamente.")
    except Exception as e:
        print(f"[ERRO] Erro ao processar cliente {addr}: {e}")
    finally:
        # Remove o usuário da lista de logados ao desconectar
        if player_name:
            with users_lock:
                logged_users.discard(player_name)
            print(f"[LOGOUT] {player_name} desconectado de {addr}.")
        print(f"[CONEXÃO FECHADA] {addr}")
        conn.close()

def start_server():
    """Inicia o servidor e aguarda por conexões."""
    HOST = '127.0.0.1'
    PORT = 1100

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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