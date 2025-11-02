import socket
from time import sleep
from utils import debug_log, limpar_terminal
from ui import parse_and_display

# FUNÇÃO DE LOGIN
def realizar_login(HOST, PORT):
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print("BEM-VINDO AO QUIZ DE REDES DE COMPUTADORES!")
        print("="*50)
        print("\nPor favor, faça login para continuar.")
        player_name = input("\nDigite seu nome de usuário: ").strip()
        
        if not player_name:
            print("\n[ERRO] O nome não pode estar vazio.")
            sleep(1.5)
            continue
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            s.sendall(f"LOGIN:{player_name}\n".encode())
            
            response = s.recv(1024).decode().strip()
            
            if response == "LOGIN_ACEITO":
                print(f"\nLogin realizado com sucesso! Bem-vindo(a), {player_name}!")
                sleep(1.5)
                return s, player_name
            
            elif response.startswith("LOGIN_NEGADO"):
                parts = response.split(':')
                if len(parts) > 1 and parts[1] == "NOME_EM_USO":
                    print(f"\nO nome '{player_name}' já está em uso.")
                    print("Por favor, escolha outro nome.")
                else:
                    print("\nLogin negado pelo servidor.")
                s.close()
                sleep(1.5)
            
            else:
                print(f"\nResposta inesperada do servidor: {response}")
                s.close()
                sleep(1.5)
        
        except ConnectionRefusedError:
            print("\n[ERRO] Não foi possível conectar ao servidor.")
            print("Verifique se o servidor está online.")
            sleep(2)
        except Exception as e:
            print(f"\n[ERRO] Ocorreu um problema: {e}")
            sleep(2)

# FUNÇÃO PARA JOGAR QUIZ SOLO
def jogar_quiz_solo(session_socket, quiz_id):
    # Envia comando para iniciar quiz
    session_socket.sendall(f"INICIAR_QUIZ:{quiz_id}\n".encode())

    # Lógica de recebimento com buffer
    buffer = ""
    quiz_over = False
    user_quit = False

    while not quiz_over and not user_quit:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida com o servidor.")
            return
        buffer += data

        while '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            if not message:
                continue

            parse_and_display(message)

            if message.startswith("PERGUNTA"):
                num_pergunta = message.split(':')[1]
                while True:
                    user_answer = input("Sua resposta (A, B, C ou D) [ou 'SAIR' para desistir]: ").strip().upper()
                    if user_answer in ['A', 'B', 'C', 'D']:
                        session_socket.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}\n".encode())
                        break
                    elif user_answer == 'SAIR':
                        print("Desistindo do quiz...")
                        session_socket.sendall(b"QUIT_QUIZ\n")
                        user_quit = True
                        break
                    else:
                        print("Resposta inválida.")
                if user_quit:
                    break
            
            elif message == "FIM_DE_JOGO":
                session_socket.sendall(b"PEDIR_PONTUACAO\n")
            
            elif message.startswith("PONTUACAO_FINAL"):
                input("\nPressione Enter para voltar ao menu...")
                quiz_over = True
                break
            elif message == "QUIZ_ENCERRADO":
                print("\n[AVISO] Você desistiu do quiz.")
                input("\nPressione Enter para voltar ao menu...")
                user_quit = True
                break
        if user_quit:
            break

# FUNÇÃO PARA LISTAR SALAS DISPONÍVEIS
def listar_salas_disponiveis(session_socket):
    limpar_terminal()
    print("\n" + "="*50)
    print("SALAS DISPONÍVEIS")
    print("="*50)
    
    debug_log("Enviando LISTAR_SALAS")
    session_socket.sendall(b"LISTAR_SALAS\n")
    
    buffer = ""
    while True:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida com o servidor.")
            return None
        
        buffer += data
        debug_log(f"Recebido: {repr(buffer)}")
        
        if '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            debug_log(f"Processando mensagem: {message}")
            if message.startswith("SALAS_DISPONIVEIS"):
                parts = message.split(':', 1)
                if len(parts) == 1 or parts[1] == '':
                    print("\nNenhuma sala disponível no momento.")
                    return []
                else:
                    salas_str = parts[1]
                    salas_list = salas_str.split(';')
                    salas = []
                    
                    print("\nSalas disponíveis:\n")
                    for i, sala_info in enumerate(salas_list):
                        room_id, players_count, max_players = sala_info.split(':')
                        salas.append(room_id)
                        print(f"  {i+1}. {room_id} - Jogadores: {players_count}/{max_players}")
                    
                    return salas
            break
    
    return None

# FUNÇÃO PARA VER JOGADORES NA SALA
def ver_jogadores_sala(session_socket):
    debug_log("Enviando VER_JOGADORES_SALA")
    session_socket.sendall(b"VER_JOGADORES_SALA\n")
    
    buffer = ""
    while True:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida com o servidor.")
            break
        
        buffer += data
        debug_log(f"Recebido: {repr(buffer)}")
        
        if '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            debug_log(f"Processando mensagem: {message}")
            if message.startswith("JOGADORES_SALA"):
                limpar_terminal()
                parts = message.split(':', 1)
                players_str = parts[1]
                players = players_str.split(';')
                
                print("\n" + "="*50)
                print("PARTICIPANTES DA SALA")
                print("="*50)
                print("\nJogadores:")
                for i, player in enumerate(players):
                    print(f"  {i+1}. {player}")
                print(f"\nTotal: {len(players)}/5")
                print("="*50)
                break
            elif message.startswith("ERRO"):
                parse_and_display(message)
                break

# FUNÇÃO PARA VER RANKING DA SALA
def ver_ranking_sala(session_socket):
    debug_log("Enviando PEDIR_RANKING_SALA")
    session_socket.sendall(b"PEDIR_RANKING_SALA\n")
    
    buffer = ""
    
    try:
        session_socket.settimeout(5.0)  # Timeout de 5 segundos
        
        while True:
            data = session_socket.recv(2048).decode()
            debug_log(f"Dados recebidos: {repr(data)}")
            
            if not data:
                print("\n[ERRO] Conexão perdida com o servidor.")
                return
            
            buffer += data
            debug_log(f"Buffer atual: {repr(buffer)}")
            
            if '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                debug_log(f"Processando mensagem: {repr(message)}")
                
                if not message:
                    continue
                    
                if message.startswith("RANKING_SALA"):
                    parse_and_display(message)
                    break
                elif message.startswith("ERRO"):
                    parse_and_display(message)
                    break
                else:
                    debug_log(f"Mensagem inesperada ignorada: {message}")
                    continue
    
    except socket.timeout:
        print("\n[ERRO] Timeout ao aguardar ranking do servidor.")
    except Exception as e:
        print(f"\n[ERRO] Erro ao receber ranking: {e}")
    finally:
        session_socket.settimeout(None)  # Remove timeout

# FUNÇÃO PARA JOGAR QUIZ NA SALA
def jogar_quiz_sala(session_socket, quiz_id):
    debug_log(f"Iniciando quiz na sala: {quiz_id}")
    session_socket.sendall(f"INICIAR_QUIZ_SALA:{quiz_id}\n".encode())
    
    buffer = ""
    
    while True:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida.")
            return
        buffer += data
        
        if '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            if message == "BEM_VINDO":
                parse_and_display(message)
                break
            elif message.startswith("ERRO"):
                parse_and_display(message)
                return
    

    fim_de_jogo = False
    user_quit = False

    while not fim_de_jogo and not user_quit:
        while '\n' not in buffer:
            data = session_socket.recv(2048).decode()
            if not data:
                print("\n[ERRO] Conexão perdida.")
                return
            buffer += data
        
        message, buffer = buffer.split('\n', 1)
        debug_log(f"Quiz - Mensagem: {message}")
        
        if message.startswith("PERGUNTA"):
            parse_and_display(message)
            num_pergunta = message.split(':')[1]
            
            while True:
                user_answer = input("Sua resposta (A, B, C ou D) [ou 'SAIR' para desistir]: ").strip().upper()
                if user_answer in ['A', 'B', 'C', 'D']:
                    session_socket.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}\n".encode())
                    break
                elif user_answer == 'SAIR':
                    print("Desistindo do quiz...")
                    session_socket.sendall(b"QUIT_QUIZ\n")
                    user_quit = True
                    break
                else:
                    print("Resposta inválida.")
            if user_quit:
                break

            # Esperar resultado
            while '\n' not in buffer:
                data = session_socket.recv(2048).decode()
                if not data:
                    return
                buffer += data
            
            message, buffer = buffer.split('\n', 1)
            parse_and_display(message) # message = RESULTADO_CORRETO ou RESULTADO_INCORRETO 
            
        elif message == "FIM_DE_JOGO":
            parse_and_display(message)
            session_socket.sendall(b"PEDIR_PONTUACAO\n")
            fim_de_jogo = True

        # Lógica de saída
        elif message == "QUIZ_ENCERRADO":
            print("\nO quiz foi encerrado pelo servidor.")
            user_quit = True
            break

    # Confirmar saída do quiz
    if user_quit and not message == "QUIZ_ENCERRADO":
        while '\n' not in buffer:
            data = session_socket.recv(2048).decode()
            if not data: return
            buffer += data
        message, buffer = buffer.split('\n', 1)
        if message == "QUIZ_ENCERRADO":
            print("[SERVIDOR] Confirmação de saída recebida.")
    
    # Receber pontuação final
    if fim_de_jogo:
        while True:
            while '\n' not in buffer:
                data = session_socket.recv(2048).decode()
                if not data:
                    return
                buffer += data
            
            message, buffer = buffer.split('\n', 1)
            debug_log(f"Mensagem final: {message}")
            
            if message.startswith("PONTUACAO_FINAL_SALA"):
                parse_and_display(message)
                break
    
    print("\n" + "="*50)
    input("Pressione Enter para voltar ao menu da sala...")
    limpar_terminal()