import socket
import os
from time import sleep

DEBUG = False
HOST = '127.0.0.1'
PORT = 1100


def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

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

# MENU PRINCIPAL
def show_menu(player_name):
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print(f"Quiz de Redes - Logado como: {player_name}")
        print("="*50)
        print("Opções:")
        print("  1. Modo de quizzes solo")
        print("  2. Modo de quizzes multiplayer")
        #print("  3. Ver Rankings modo solo")
        print("  3. Sair")

        choice = input("Escolha uma opção: ")
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Opção inválida. Tente novamente.")
            sleep(1.5)

# MENU DE QUIZZES SOLO
def quiz_menu_solo():
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print('Selecione o quiz do capítulo deseja praticar!')
        print("="*50)
        print('Opções:')
        print('  1. Capítulo 1: Introdução a Redes de Computadores')
        print('  2. Capítulo 2: Camada de Aplicação')
        print('  3. Voltar')
        choice = input('Escolha uma opção: ')

        if choice in ['1', '2', '3']:
            return choice
        else:
            print('Opção inválida. Tente novamente.')
            sleep(1.5)

# MENU MULTIPLAYER
def multiplayer_menu():
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print('MODO MULTIPLAYER')
        print("="*50)
        print('Opções:')
        print('  1. Criar nova sala')
        print('  2. Entrar em sala existente')
        print('  3. Voltar')
        choice = input('Escolha uma opção: ')

        if choice in ['1', '2', '3']:
            return choice
        else:
            print('Opção inválida. Tente novamente.')
            sleep(1.5)

# MENU DA SALA
def sala_menu(room_id):
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print(f'SALA: {room_id}')
        print("="*50)
        print('Um acerto vale 1 ponto e um erro desconta 1 ponto. Tente alcançar a maior pontuação!')
        print('Opções:')
        print('  1. Listar participantes da sala')
        print('  2. Ranking da sala')
        print('  3. Praticar quiz capítulo 1')
        print('  4. Praticar quiz capítulo 2')
        print('  5. Sair da sala')
        choice = input('Escolha uma opção: ')

        if choice in ['1', '2', '3', '4', '5']:
            return choice
        
        print('Opção inválida. Tente novamente.')
        sleep(1.5)

# FUNÇÃO PARA TRATAR A MENSAGEM RECEBIDA DO SERVIDOR
def parse_and_display(message):
    parts = message.split(':', 1)
    command = parts[0]

    if command == "BEM_VINDO":
        print("\n[SERVIDOR] Conectado e pronto! O quiz vai começar.")
        sleep(1.5)
    elif command == "PERGUNTA":
        limpar_terminal()
        _, num, text, options_str = message.split(':', 3)
        options = options_str.split(':')
        
        print("\n" + "-"*50)
        print(f"Pergunta {num}: {text}")
        for i, opt in enumerate(options):
            print(f"  {chr(65+i)}) {opt}")
        print("-"*50)

    elif command == "RESULTADO_CORRETO":
        print("Resposta Correta!")
        sleep(1.5)
    elif command == "RESULTADO_INCORRETO":
        print("Resposta Incorreta")
        sleep(1.5)
    elif command == "FIM_DE_JOGO":
        print("\n" + "="*50)
        print("--- Fim do Questionário! ---")
    elif command == "PONTUACAO_FINAL":
        print(f"\nContagem de acertos: {parts[1]} acertos.")
    elif command == "PONTUACAO_FINAL_SALA":
        print(f"\nSua pontuação total na sala: {parts[1]} pontos.")
    elif command == "RANKING_SALA":
        limpar_terminal()
        print("\n" + "="*50)
        print("RANKING DA SALA")
        print("="*50)
        
        if len(parts) < 2 or not parts[1]:
            print("\nO ranking da sala está vazio.")
            print("Jogue pelo menos um quiz para aparecer no ranking!")
        else:
            ranking_data = parts[1].split(';')
            if not ranking_data or ranking_data[0] == '':
                print("\nO ranking da sala está vazio.")
                print("Jogue pelo menos um quiz para aparecer no ranking!")
            else:
                print("\nClassificação:")
                for i, entry in enumerate(ranking_data):
                    if ':' in entry:
                        name, score = entry.split(':')
                        print(f"  {i+1}º - {name}: {score} pontos")
        print("="*50)
    elif command == "ERRO":
        print(f"[ERRO DO SERVIDOR] {parts[1]}")
    else:
        print(f"[DEBUG] Mensagem desconhecida: {message}")

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
    while not fim_de_jogo:
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
                user_answer = input("Sua resposta (A, B, C ou D): ").strip().upper()
                if user_answer in ['A', 'B', 'C', 'D']:
                    session_socket.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}\n".encode())
                    break
                else:
                    print("Resposta inválida.")
            
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
    
    # Receber pontuação final
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

def main():

    # TELA DE LOGIN
    session_socket, player_name = realizar_login(HOST, PORT)

    try:
        while True:
            user_choice = show_menu(player_name)

            if user_choice == '3':  # Sair
                print('\nEncerrando sessão...')
                session_socket.sendall(b"LOGOUT")
                sleep(1)
                print('Até logo!')
                break
            
            elif user_choice == '1':  # Quiz Solo
                user_choice = quiz_menu_solo()

                if user_choice == '3':
                    continue

                if user_choice == '1':
                    quiz_id = 'REDES_C1'
                elif user_choice == '2':
                    quiz_id = 'REDES_C2'

                # Envia comando para iniciar quiz
                session_socket.sendall(f"INICIAR_QUIZ:{quiz_id}".encode())

                # Lógica de recebimento com buffer
                buffer = ""
                quiz_over = False
                while not quiz_over:
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
                                user_answer = input("Sua resposta (A, B, C ou D): ").strip().upper()
                                if user_answer in ['A', 'B', 'C', 'D']:
                                    session_socket.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}\n".encode())
                                    break
                                else:
                                    print("Resposta inválida.")
                        
                        elif message == "FIM_DE_JOGO":
                            session_socket.sendall(b"PEDIR_PONTUACAO\n")
                        
                        elif message.startswith("PONTUACAO_FINAL"):
                            input("\nPressione Enter para voltar ao menu...")
                            quiz_over = True
                            break

            elif user_choice == '2':  # Multiplayer
                mp_choice = multiplayer_menu()
                
                if mp_choice == '3':  # Voltar
                    continue
                
                elif mp_choice == '1':  # Criar sala
                    session_socket.sendall(b"CRIAR_SALA\n")
                    
                    buffer = ""
                    while True:
                        data = session_socket.recv(2048).decode()
                        if not data:
                            print("\n[ERRO] Conexão perdida com o servidor.")
                            break
                        
                        buffer += data
                        
                        if '\n' in buffer:
                            message, buffer = buffer.split('\n', 1)
                            if message.startswith("SALA_CRIADA"):
                                room_id = message.split(':')[1]
                                print(f"\nSala '{room_id}' criada com sucesso!")
                                sleep(2)
                                
                                # Loop da sala
                                in_room = True
                                while in_room:
                                    sala_choice = sala_menu(room_id)
                                    
                                    if sala_choice == '1':  # Ver jogadores
                                        ver_jogadores_sala(session_socket)
                                        input("\nPressione Enter para continuar...")
                                    
                                    elif sala_choice == '2':  # Ranking da sala
                                        ver_ranking_sala(session_socket)
                                        input("\nPressione Enter para continuar...")
                                    
                                    elif sala_choice == '3':  # Quiz Cap 1
                                        jogar_quiz_sala(session_socket, 'REDES_C1')
                                    
                                    elif sala_choice == '4':  # Quiz Cap 2
                                        jogar_quiz_sala(session_socket, 'REDES_C2')
                                    
                                    elif sala_choice == '5':  # Sair da sala
                                        print("\nSaindo da sala...")
                                        session_socket.sendall(b"SAIR_SALA\n")
                                        
                                        buffer_temp = ""
                                        while True:
                                            data = session_socket.recv(2048).decode()
                                            if not data:
                                                break
                                            buffer_temp += data
                                            if '\n' in buffer_temp:
                                                msg, buffer_temp = buffer_temp.split('\n', 1)
                                                if msg == "SAIU_SALA":
                                                    print("Você saiu da sala.")
                                                    sleep(1)
                                                break
                                        in_room = False
                                
                                break
                            elif message.startswith("ERRO"):
                                parse_and_display(message)
                                sleep(2)
                                break
                
                elif mp_choice == '2':  # Entrar em sala
                    salas = listar_salas_disponiveis(session_socket)
                    
                    if salas is None:
                        sleep(2)
                        continue
                    
                    if len(salas) == 0:
                        input("\nPressione Enter para voltar...")
                        continue
                    
                    print("\n" + "-"*50)
                    escolha = input("Digite o número da sala para entrar (ou 0 para voltar): ")
                    
                    if escolha == '0':
                        continue
                    
                    try:
                        idx = int(escolha) - 1
                        if 0 <= idx < len(salas):
                            room_id = salas[idx]
                            session_socket.sendall(f"ENTRAR_SALA:{room_id}\n".encode())
                            
                            buffer = ""
                            while True:
                                data = session_socket.recv(2048).decode()
                                if not data:
                                    print("\n[ERRO] Conexão perdida com o servidor.")
                                    break
                                
                                buffer += data
                                
                                if '\n' in buffer:
                                    message, buffer = buffer.split('\n', 1)
                                    if message.startswith("ENTROU_SALA"):
                                        room_id = message.split(':')[1]
                                        print(f"\nVocê entrou na sala '{room_id}'!")
                                        sleep(2)
                                        
                                        # Loop da sala
                                        in_room = True
                                        while in_room:
                                            sala_choice = sala_menu(room_id)
                                            
                                            if sala_choice == '1':  # Ver jogadores
                                                ver_jogadores_sala(session_socket)
                                                input("\nPressione Enter para continuar...")
                                            
                                            elif sala_choice == '2':  # Ranking da sala
                                                ver_ranking_sala(session_socket)
                                                input("\nPressione Enter para continuar...")
                                            
                                            elif sala_choice == '3':  # Quiz Cap 1
                                                jogar_quiz_sala(session_socket, 'REDES_C1')
                                            
                                            elif sala_choice == '4':  # Quiz Cap 2
                                                jogar_quiz_sala(session_socket, 'REDES_C2')
                                            
                                            elif sala_choice == '5':  # Sair da sala
                                                print("\nSaindo da sala...")
                                                session_socket.sendall(b"SAIR_SALA\n")
                                                
                                                buffer_temp = ""
                                                while True:
                                                    data = session_socket.recv(2048).decode()
                                                    if not data:
                                                        break
                                                    buffer_temp += data
                                                    if '\n' in buffer_temp:
                                                        msg, buffer_temp = buffer_temp.split('\n', 1)
                                                        if msg == "SAIU_SALA":
                                                            print("Você saiu da sala.")
                                                            sleep(1)
                                                        break
                                                in_room = False
                                        
                                        break
                                    elif message.startswith("ERRO"):
                                        parts = message.split(':')
                                        if len(parts) > 1:
                                            erro = parts[1]
                                            if erro == "SALA_CHEIA":
                                                print("\nEsta sala já está cheia (máximo 5 jogadores).")
                                            elif erro == "SALA_NAO_ENCONTRADA":
                                                print("\nSala não encontrada.")
                                            else:
                                                print(f"\nErro: {erro}")
                                        sleep(2)
                                        break
                        else:
                            print("\nNúmero inválido.")
                            sleep(1.5)
                    except ValueError:
                        print("\nEntrada inválida.")
                        sleep(1.5)

    except ConnectionResetError:
        print("\n[ERRO] Conexão com o servidor foi perdida.")
        sleep(2)
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema: {e}")
        import traceback
        traceback.print_exc()
        sleep(2)
    finally:
        session_socket.close()
        print("\nConexão encerrada.")

if __name__ == "__main__":
    main()