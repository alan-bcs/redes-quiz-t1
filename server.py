import socket
import threading
#import json
from questions import questionsC1, questionsC2

HOST = '127.0.0.1'
PORT = 1100

# Persistência dos rankings
#RANKING_FILE = 'rankings.json'

QUIZZES = {
    "REDES_C1": questionsC1,
    "REDES_C2": questionsC2
}

# CONTROLE DE USUÁRIOS LOGADOS
logged_users = set()
users_lock = threading.Lock()

# CONTROLE DE SALAS MULTIPLAYER
rooms = {}  # {room_id: {'players': [player_name, ...], 'scores': {player_name: score}}}
rooms_lock = threading.Lock()
room_counter = 0


ranking_lock = threading.Lock()

# FUNÇÕES PARA CRIAÇÃO DE SALAS
def create_room(player_name):
    global room_counter
    with rooms_lock:
        room_counter += 1
        room_id = f"sala_{room_counter}"
        rooms[room_id] = {
            'players': [player_name],
            'scores': {player_name: 0}
        }
        print(f"[SALA CRIADA] {room_id} por {player_name}")
        return room_id

# FUNÇÃO PARA ENTRAR EM UMA SALA
def join_room(room_id, player_name):
    with rooms_lock:
        if room_id not in rooms:
            return False, "SALA_NAO_ENCONTRADA"
        
        room = rooms[room_id]
        
        if len(room['players']) >= 5:
            return False, "SALA_CHEIA"
        
        if player_name in room['players']:
            return False, "JA_NA_SALA"
        
        room['players'].append(player_name)
        room['scores'][player_name] = 0
        print(f"[JOGADOR ENTROU] {player_name} entrou em {room_id}")
        return True, "SUCESSO"

# FUNÇÃO PARA SAIR DE UMA SALA (DELETAR SE VAZIA)
def leave_room(room_id, player_name):
    with rooms_lock:
        if room_id not in rooms:
            return
        
        room = rooms[room_id]
        
        if player_name in room['players']:
            room['players'].remove(player_name)
            if player_name in room['scores']:
                del room['scores'][player_name]
            print(f"[JOGADOR SAIU] {player_name} saiu de {room_id}")
        
        # Deleta a sala se ficou vazia
        if len(room['players']) == 0:
            del rooms[room_id]
            print(f"[SALA DELETADA] {room_id} (sala vazia)")

# LISTAR SALAS DISPONÍVEIS
def get_available_rooms():
    with rooms_lock:
        available = []
        for room_id, room_data in rooms.items():
            if len(room_data['players']) < 5:
                available.append({
                    'room_id': room_id,
                    'players_count': len(room_data['players']),
                    'max_players': 5
                })
        return available # retorna apenas salas com vagas

# OBTER JOGADORES NA SALA
def get_room_players(room_id):
    with rooms_lock:
        if room_id in rooms:
            return rooms[room_id]['players'].copy()
        return []

# OBTER RANKING DA SALA
def get_room_ranking(room_id):
    with rooms_lock:
        if room_id in rooms:
            scores = rooms[room_id]['scores']
            ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return ranking
        return []

# ATUALIZAR PONTUAÇÃO NA SALA
def update_room_score(room_id, player_name, correct):
    with rooms_lock:
        if room_id in rooms and player_name in rooms[room_id]['scores']:
            if correct:
                rooms[room_id]['scores'][player_name] += 1
            else:
                # O score nunca fica negativo
                rooms[room_id]['scores'][player_name] = max(0, rooms[room_id]['scores'][player_name] - 1)
            print(f"[SCORE ATUALIZADO] {player_name} em {room_id}: {rooms[room_id]['scores'][player_name]} pontos")

# FUNÇÃO PARA GERENCIAR A CONEXÃO DE UM ÚNICO CLIENTE
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    player_name = None
    score = 0
    selected_quiz = None
    current_room = None

    try:
        # 1. Espera a primeira mensagem do cliente
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
                
                # Aguarda comandos do cliente já logado
                while True:
                    command = conn.recv(1024).decode().strip()
                    
                    if not command:
                        break
                    
                    print(f"[COMANDO] {player_name}: {command}")
                    #print(f"[DEBUG] current_room = {current_room}")
                    
                    # PEDIR RANKING DA SALA (deve vir ANTES do ranking solo!)
                    if command == "PEDIR_RANKING_SALA":
                        #print(f"[DEBUG] PEDIR_RANKING_SALA - current_room = {current_room}")
                        if not current_room:
                            #print(f"[DEBUG] Enviando ERRO:NAO_EM_SALA")
                            conn.sendall(b"ERRO:NAO_EM_SALA\n")
                        else:
                            ranking = get_room_ranking(current_room)
                            if not ranking:
                                ranking_str = ""
                            else:
                                ranking_str = ";".join([f"{name}:{pts}" for name, pts in ranking])
                            response = f"RANKING_SALA:{ranking_str}\n"
                            print(f"[ENVIANDO RANKING] Para sala {current_room}: {response.strip()}")
                            conn.sendall(response.encode())
                    
                    # PROTOCOLO INICIAR QUIZ (SOLO)
                    elif command.startswith("INICIAR_QUIZ:"):
                        parts = command.split(':')
                        if len(parts) == 2:
                            quiz_id = parts[1]
                            if quiz_id in QUIZZES:
                                selected_quiz = QUIZZES[quiz_id]
                                score = 0
                                conn.sendall(b"BEM_VINDO\n")
                                
                                user_quit_solo = False
                                # Loop principal do Quiz
                                for i, q in enumerate(selected_quiz):
                                    options_str = ":".join(q["options"].values())
                                    question_msg = f"PERGUNTA:{i+1}:{q['question']}:{options_str}"
                                    conn.sendall(question_msg.encode() + b'\n')

                                    # Aguarda a resposta do cliente
                                    answer_msg = conn.recv(1024).decode().strip()

                                    # Lógica de saída do quiz
                                    if answer_msg == "QUIT_QUIZ":
                                        user_quit_solo = True
                                        print(f"[QUIZ SOLO] {player_name} desistiu do quiz.")
                                        conn.sendall(b"QUIZ_ENCERRADO\n")
                                        break

                                    answer_parts = answer_msg.split(':')
                                    user_answer = answer_parts[2]

                                    if user_answer == q["answer"]:
                                        score += 1
                                        conn.sendall(b"RESULTADO_CORRETO\n")
                                    else:
                                        conn.sendall(b"RESULTADO_INCORRETO\n")

                                # Fim do Quiz (se não houve desistência)
                                if not user_quit_solo:
                                    conn.sendall(b"FIM_DE_JOGO\n")
                                
                                    # Aguarda pedido de pontuação
                                    final_command = conn.recv(1024).decode().strip()
                                    if final_command == "PEDIR_PONTUACAO":
                                        conn.sendall(f"PONTUACAO_FINAL:{score}\n".encode())
                                
                            else:
                                conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO\n")
                    
                    
                    # PROTOCOLOS DE SALAS MULTIPLAYER
                    # CRIAR SALA
                    elif command == "CRIAR_SALA":
                        if current_room:
                            conn.sendall(b"ERRO:JA_EM_SALA\n")
                        else:
                            room_id = create_room(player_name)
                            current_room = room_id
                            #print(f"[DEBUG] Sala criada, current_room agora é: {current_room}")
                            conn.sendall(f"SALA_CRIADA:{room_id}\n".encode())
                    
                    # LISTAR SALAS
                    elif command == "LISTAR_SALAS":
                        available = get_available_rooms()
                        if not available:
                            conn.sendall(b"SALAS_DISPONIVEIS:\n")
                        else:
                            salas_str = ";".join([
                                f"{r['room_id']}:{r['players_count']}:{r['max_players']}"
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
                                    #print(f"[DEBUG] Entrou na sala, current_room agora é: {current_room}")
                                    conn.sendall(f"ENTROU_SALA:{room_id}\n".encode())
                                else:
                                    conn.sendall(f"ERRO:{reason}\n".encode())
                    
                    # VER JOGADORES NA SALA
                    elif command == "VER_JOGADORES_SALA":
                        #print(f"[DEBUG] VER_JOGADORES_SALA - current_room = {current_room}")
                        if not current_room:
                            conn.sendall(b"ERRO:NAO_EM_SALA\n")
                        else:
                            players = get_room_players(current_room)
                            players_str = ";".join(players)
                            response = f"JOGADORES_SALA:{players_str}\n"
                            print(f"[ENVIANDO] {response.strip()}")
                            conn.sendall(response.encode())
                    
                    # INICIAR QUIZ NA SALA
                    elif command.startswith("INICIAR_QUIZ_SALA"):
                        if not current_room:
                            conn.sendall(b"ERRO:NAO_EM_SALA\n")
                        else:
                            parts = command.split(':')
                            if len(parts) == 2:
                                quiz_id = parts[1]
                                if quiz_id in QUIZZES:
                                    selected_quiz = QUIZZES[quiz_id]
                                    print(f"[QUIZ SALA] {player_name} iniciando quiz {quiz_id} na sala {current_room}")
                                    conn.sendall(b"BEM_VINDO\n")
                                    
                                    user_quit_sala = False
                                    # Loop do Quiz
                                    for i, q in enumerate(selected_quiz):
                                        options_str = ":".join(q["options"].values())
                                        question_msg = f"PERGUNTA:{i+1}:{q['question']}:{options_str}"
                                        conn.sendall(question_msg.encode() + b'\n')

                                        # Aguarda resposta
                                        answer_msg = conn.recv(1024).decode().strip()
                                        
                                        # Lógica de saída do quiz
                                        if answer_msg == "QUIT_QUIZ":
                                            user_quit_sala = True
                                            print(f"[QUIZ SALA] {player_name} desistiu do quiz em {current_room}.")
                                            conn.sendall(b"QUIZ_ENCERRADO\n")
                                            break

                                        # LÓGICA DE PARSING SEGURA
                                        answer_parts = answer_msg.split(':')
                                        if len(answer_parts) == 3 and answer_parts[0] == "RESPONDER_PERGUNTA":
                                            user_answer = answer_parts[2]
                                            correct = (user_answer == q["answer"])
                                            
                                            update_room_score(current_room, player_name, correct)
                                            
                                            if correct:
                                                conn.sendall(b"RESULTADO_CORRETO\n")
                                            else:
                                                conn.sendall(b"RESULTADO_INCORRETO\n")
                                        else:
                                            # Se a mensagem do cliente for inválida
                                            print(f"[AVISO] Mensagem de resposta inválida de {player_name}: {answer_msg}")
                                            conn.sendall(b"ERRO:RESPOSTA_INVALIDA\n")

                                    # Fim do Quiz (se não houve desistência)
                                    if not user_quit_sala:
                                        conn.sendall(b"FIM_DE_JOGO\n")
                                        print(f"[FIM QUIZ SALA] Quiz finalizado para {player_name}")
                                    
                                        # Obtém pontuação final da sala
                                        with rooms_lock:
                                            final_score = rooms.get(current_room, {}).get('scores', {}).get(player_name, 0)
                                    
                                        print(f"[PONTUACAO] {player_name} na sala {current_room}: {final_score} pontos")

                                        # Aguarda pedido de pontuação
                                        final_command = conn.recv(1024).decode().strip()
                                        print(f"[COMANDO FINAL] Recebido: {final_command}")
                                        
                                        if final_command == "PEDIR_PONTUACAO":
                                            response = f"PONTUACAO_FINAL_SALA:{final_score}\n"
                                            print(f"[ENVIANDO] {response.strip()}")
                                            conn.sendall(response.encode())
                                        else:
                                            print(f"[AVISO] Comando inesperado após FIM_DE_JOGO: {final_command}")
                                    
                                else:
                                    conn.sendall(b"ERRO:QUIZ_NAO_ENCONTRADO\n")
                    
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

    except ConnectionResetError:
        print(f"[AVISO] Conexão com {addr} perdida inesperadamente.")
    except Exception as e:
        print(f"[ERRO] Erro ao processar cliente {addr}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Remove o usuário da sala se estiver em alguma
        if current_room:
            leave_room(current_room, player_name)
        
        # Remove o usuário da lista de logados
        if player_name:
            with users_lock:
                logged_users.discard(player_name)
            print(f"[LOGOUT] {player_name} desconectado de {addr}.")
        print(f"[CONEXÃO FECHADA] {addr}")
        conn.close()

def start_server():
    """Inicia o servidor e aguarda por conexões."""

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