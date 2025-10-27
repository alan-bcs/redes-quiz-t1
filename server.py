import socket
import threading
import json
from questions import questionsC1, questionsC2

# Persistência dos rankings
RANKING_FILE = 'rankings.json'

QUIZZES = {
    "REDES_C1": questionsC1,
    "REDES_C2": questionsC2
}

# CONTROLE DE USUÁRIOS LOGADOS
logged_users = set()
users_lock = threading.Lock()

# CONTROLE DE SALAS MULTIPLAYER
rooms = {}  # {room_id: {'host': player_name, 'players': [player_name, ...], 'quiz_id': None, 'status': 'waiting'}}
rooms_lock = threading.Lock()
room_counter = 0  # Contador para gerar IDs sequenciais de salas

# FUNÇÃO PARA CARREGAR O ARQUIVO .JSON
def load_rankings():
    try:
        with open(RANKING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# FUNÇÃO QUE SALVA DICIONÁRIO DE RANKINGS NO .JSON
def save_rankings(rankings_data):
    with open(RANKING_FILE, 'w') as f:
        json.dump(rankings_data, f, indent=4)

rankings = load_rankings()
ranking_lock = threading.Lock()

# FUNÇÕES DE GERENCIAMENTO DE SALAS
def create_room(host_name):
    """Cria uma nova sala e retorna o room_id"""
    global room_counter
    with rooms_lock:
        room_counter += 1
        room_id = f"sala_{room_counter}"
        rooms[room_id] = {
            'host': host_name,
            'players': [host_name],
            'quiz_id': None,
            'status': 'waiting',  # waiting, playing, finished
            'scores': {}  # {player_name: score}
        }
        print(f"[SALA CRIADA] {room_id} por {host_name}")
        return room_id

def delete_room(room_id):
    """Remove uma sala"""
    with rooms_lock:
        if room_id in rooms:
            del rooms[room_id]
            print(f"[SALA DELETADA] {room_id}")

def join_room(room_id, player_name):
    """Adiciona um jogador a uma sala. Retorna True se bem-sucedido."""
    with rooms_lock:
        if room_id not in rooms:
            return False, "SALA_NAO_ENCONTRADA"
        
        room = rooms[room_id]
        
        if room['status'] != 'waiting':
            return False, "SALA_EM_JOGO"
        
        if len(room['players']) >= 5:
            return False, "SALA_CHEIA"
        
        if player_name in room['players']:
            return False, "JA_NA_SALA"
        
        room['players'].append(player_name)
        print(f"[JOGADOR ENTROU] {player_name} entrou em {room_id}")
        return True, "SUCESSO"

def leave_room(room_id, player_name):
    """Remove um jogador de uma sala. Se for o host, deleta a sala."""
    with rooms_lock:
        if room_id not in rooms:
            return
        
        room = rooms[room_id]
        
        if player_name in room['players']:
            room['players'].remove(player_name)
            print(f"[JOGADOR SAIU] {player_name} saiu de {room_id}")
        
        # Se o host saiu ou sala ficou vazia, deleta a sala
        if player_name == room['host'] or len(room['players']) == 0:
            del rooms[room_id]
            print(f"[SALA DELETADA] {room_id} (host saiu ou sala vazia)")

def get_available_rooms():
    """Retorna lista de salas disponíveis"""
    with rooms_lock:
        available = []
        for room_id, room_data in rooms.items():
            if room_data['status'] == 'waiting' and len(room_data['players']) < 5:
                available.append({
                    'room_id': room_id,
                    'host': room_data['host'],
                    'players_count': len(room_data['players']),
                    'max_players': 5
                })
        return available

def get_room_players(room_id):
    """Retorna lista de jogadores na sala"""
    with rooms_lock:
        if room_id in rooms:
            return rooms[room_id]['players'].copy()
        return []

def notify_room_players(room_id, message, exclude_player=None):
    """Envia uma mensagem para todos os jogadores da sala (exceto exclude_player)"""
    # Esta função será implementada mantendo referências aos sockets dos clientes
    pass

# FUNÇÃO PARA GERENCIAR A CONEXÃO DE UM ÚNICO CLIENTE
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    player_name = None
    score = 0
    selected_quiz = None
    current_room = None  # ID da sala em que o jogador está

    try:
        # 1. Espera a primeira mensagem do cliente (pode ser LOGIN ou PEDIR_RANKING)
        init_message = conn.recv(1024).decode().strip()

        # === PROTOCOLO DE LOGIN ===
        if init_message.startswith("LOGIN"):
            parts = init_message.split(':')
            if len(parts) == 2:
                requested_name = parts[1].strip()
                
                with users_lock:
                    if requested_name in logged_users:
                        conn.sendall(b"LOGIN_NEGADO:NOME_EM_USO\n")
                        print(f"[LOGIN NEGADO] {addr} tentou usar o nome '{requested_name}' já em uso.")
                        return
                    else:
                        logged_users.add(requested_name)
                        player_name = requested_name
                        conn.sendall(b"LOGIN_ACEITO\n")
                        print(f"[LOGIN ACEITO] {addr} logado como '{player_name}'.")
                
                # Agora aguarda os próximos comandos do cliente já logado
                while True:
                    command = conn.recv(1024).decode().strip()
                    
                    if not command:
                        break
                    
                    # PROTOCOLO PEDIR RANKING (SOLO)
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
                    
                    # PROTOCOLO INICIAR QUIZ (SOLO)
                    elif command.startswith("INICIAR_QUIZ"):
                        parts = command.split(':')
                        if len(parts) == 2:
                            quiz_id = parts[1]
                            if quiz_id in QUIZZES:
                                selected_quiz = QUIZZES[quiz_id]
                                score = 0 # Reseta o score no início do quiz
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
                                
                                # O cliente vai pedir a pontuação. Aguardamos esse comando.
                                final_command = conn.recv(1024).decode().strip()
                                if final_command == "PEDIR_PONTUACAO":
                                    conn.sendall(f"PONTUACAO_FINAL:{score}\n".encode())
                                # Após enviar a pontuação, o quiz termina e o servidor volta a escutar
                                # por comandos do menu principal no loop 'while True' externo.
                                
                            else:
                                conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO\n")
                    
                    # === PROTOCOLOS MULTIPLAYER ===
                    
                    # CRIAR SALA
                    elif command == "CRIAR_SALA":
                        if current_room:
                            conn.sendall(b"ERRO:JA_EM_SALA\n")
                        else:
                            room_id = create_room(player_name)
                            current_room = room_id
                            conn.sendall(f"SALA_CRIADA:{room_id}\n".encode())
                    
                    # LISTAR SALAS
                    elif command == "LISTAR_SALAS":
                        available = get_available_rooms()
                        if not available:
                            conn.sendall(b"SALAS_DISPONIVEIS:\n")
                        else:
                            salas_str = ";".join([
                                f"{r['room_id']}:{r['host']}:{r['players_count']}:{r['max_players']}"
                                for r in available
                            ])
                            conn.sendall(f"SALAS_DISPONIVEIS:{salas_str}\n".encode())
                    
                    # ENTRAR EM SALA
                    elif command.startswith("ENTRAR_SALA"):
                        parts = command.split(':')
                        if len(parts) == 2:
                            room_id = parts[1]
                            if current_room:
                                conn.sendall(b"ERRO:JA_EM_SALA\n")
                            else:
                                success, reason = join_room(room_id, player_name)
                                if success:
                                    current_room = room_id
                                    conn.sendall(f"ENTROU_SALA:{room_id}\n".encode())
                                else:
                                    conn.sendall(f"ERRO:{reason}\n".encode())
                    
                    # VER JOGADORES NA SALA
                    elif command == "VER_JOGADORES_SALA":
                        if not current_room:
                            conn.sendall(b"ERRO:NAO_EM_SALA\n")
                        else:
                            players = get_room_players(current_room)
                            with rooms_lock:
                                host = rooms[current_room]['host'] if current_room in rooms else ""
                            players_str = ";".join(players)
                            conn.sendall(f"JOGADORES_SALA:{host}:{players_str}\n".encode())
                    
                    # SAIR DA SALA
                    elif command == "SAIR_SALA":
                        if current_room:
                            leave_room(current_room, player_name)
                            conn.sendall(b"SAIU_SALA\n")
                            current_room = None
                        else:
                            conn.sendall(b"ERRO:NAO_EM_SALA\n")
                    
                    # LOGOUT
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
        # Remove o usuário da sala se estiver em alguma
        if current_room:
            leave_room(current_room, player_name)
        
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