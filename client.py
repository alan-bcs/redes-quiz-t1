import socket
import os
from time import sleep

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# === FUNÇÃO DE LOGIN ===
def realizar_login(HOST, PORT):
    """Realiza o login do usuário no servidor."""
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print("BEM-VINDO AO QUIZ DE REDES DE COMPUTADORES!")
        print("="*50)
        print("\nPor favor, faça login para continuar.")
        player_name = input("\nDigite seu nome de usuário: ").strip()
        
        if not player_name:
            print("\n[ERRO] O nome não pode estar vazio.")
            sleep(2)
            continue
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            s.sendall(f"LOGIN:{player_name}".encode())
            
            response = s.recv(1024).decode().strip()
            
            if response == "LOGIN_ACEITO":
                print(f"\n✓ Login realizado com sucesso! Bem-vindo(a), {player_name}!")
                sleep(1.5)
                return s, player_name
            
            elif response.startswith("LOGIN_NEGADO"):
                parts = response.split(':')
                if len(parts) > 1 and parts[1] == "NOME_EM_USO":
                    print(f"\n✗ O nome '{player_name}' já está em uso.")
                    print("Por favor, escolha outro nome.")
                else:
                    print("\n✗ Login negado pelo servidor.")
                s.close()
                sleep(2)
            
            else:
                print(f"\n✗ Resposta inesperada do servidor: {response}")
                s.close()
                sleep(2)
        
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
        print("  3. Ver Rankings modo solo")
        print("  4. Sair")

        choice = input("Escolha uma opção: ")
        if choice in ['1', '2', '3', '4']:
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

# MENU DA SALA (quando já está dentro)
def sala_menu(room_id, is_host):
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print(f'SALA: {room_id}')
        if is_host:
            print('(Você é o HOST da sala)')
        print("="*50)
        print('Opções:')
        print('  1. Ver jogadores na sala')
        if is_host:
            print('  2. Iniciar quiz')
        print('  3. Sair da sala')
        choice = input('Escolha uma opção: ')

        if is_host:
            if choice in ['1', '2', '3']:
                return choice
        else:
            if choice in ['1', '3']:
                return choice
        
        print('Opção inválida. Tente novamente.')
        sleep(1.5)

# RANKING MENU SOLO
def ranking_menu_solo():
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print('Selecione o ranking que deseja visualizar!')
        print("="*50)
        print('Opções:')
        print('  1. Ranking - Capítulo 1')
        print('  2. Ranking - Capítulo 2')
        print('  3. Voltar')
        choice = input('Escolha uma opção: ')
        if choice in ['1', '2', '3']:
            return choice
        else:
            print('Opção inválida. Tente novamente.')
            sleep(1.5)

# FUNÇÃO PARA TRATAR A MENSAGEM RECEBIDA DO SERVIDOR
def parse_and_display(message):
    parts = message.split(':', 1)
    command = parts[0]

    if command == "BEM_VINDO":
        print("\n[SERVIDOR] Conectado e pronto! O quiz vai começar.")
        sleep(1)
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
        print("✓ Resposta Correta!")
        sleep(1.5)
    elif command == "RESULTADO_INCORRETO":
        print("✗ Resposta Incorreta.")
        sleep(1.5)
    elif command == "FIM_DE_JOGO":
        print("\n" + "="*50)
        print("--- Fim do Questionário! ---")
    elif command == "PONTUACAO_FINAL":
        print(f"\nSua pontuação final: {parts[1]} pontos.")
    elif command == "RANKING":
        limpar_terminal()
        print("\n--- RANKING GERAL ---")
        ranking_data = parts[1].split(';')
        if not ranking_data or ranking_data[0] == '':
            print("O ranking está vazio.")
        else:
            for i, entry in enumerate(ranking_data):
                if ':' in entry:
                    name, score = entry.split(':')
                    print(f"{i+1}º Lugar: {name} - {score} pontos")
        print("---------------------")
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
    
    session_socket.sendall(b"LISTAR_SALAS")
    
    buffer = ""
    while True:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida com o servidor.")
            return None
        
        buffer += data
        
        if '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
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
                        room_id, host, players_count, max_players = sala_info.split(':')
                        salas.append(room_id)
                        print(f"  {i+1}. {room_id} (Host: {host}) - Jogadores: {players_count}/{max_players}")
                    
                    return salas
            break
    
    return None

# FUNÇÃO PARA VER JOGADORES NA SALA
def ver_jogadores_sala(session_socket):
    session_socket.sendall(b"VER_JOGADORES_SALA")
    
    buffer = ""
    while True:
        data = session_socket.recv(2048).decode()
        if not data:
            print("\n[ERRO] Conexão perdida com o servidor.")
            break
        
        buffer += data
        
        if '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            if message.startswith("JOGADORES_SALA"):
                limpar_terminal()
                parts = message.split(':', 2)
                host = parts[1]
                players_str = parts[2]
                players = players_str.split(';')
                
                print("\n" + "="*50)
                print("JOGADORES NA SALA")
                print("="*50)
                print(f"\nHost: {host}\n")
                print("Jogadores:")
                for i, player in enumerate(players):
                    marker = "HOST" if player == host else "PLAYER"
                    print(f"  {marker} {player}")
                print(f"\nTotal: {len(players)}/5")
                print("="*50)
                break
            elif message.startswith("ERRO"):
                parse_and_display(message)
                break

def main():
    HOST = '127.0.0.1'
    PORT = 1100

    # === TELA DE LOGIN ===
    session_socket, player_name = realizar_login(HOST, PORT)

    try:
        while True:
            user_choice = show_menu(player_name)

            if user_choice == '4':  # Sair
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
                                    session_socket.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}".encode())
                                    break
                                else:
                                    print("Resposta inválida.")
                        
                        elif message == "FIM_DE_JOGO":
                            session_socket.sendall(b"PEDIR_PONTUACAO")
                        
                        elif message.startswith("PONTUACAO_FINAL"):
                            input("\nPressione Enter para voltar ao menu...")
                            quiz_over = True
                            break

            elif user_choice == '2':  # Multiplayer
                mp_choice = multiplayer_menu()
                
                if mp_choice == '3':  # Voltar
                    continue
                
                elif mp_choice == '1':  # Criar sala
                    session_socket.sendall(b"CRIAR_SALA")
                    
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
                                print(f"\n✓ Sala '{room_id}' criada com sucesso!")
                                print("Você é o host da sala.")
                                sleep(2)
                                
                                # Loop da sala
                                in_room = True
                                while in_room:
                                    sala_choice = sala_menu(room_id, is_host=True)
                                    
                                    if sala_choice == '1':  # Ver jogadores
                                        ver_jogadores_sala(session_socket)
                                        input("\nPressione Enter para continuar...")
                                    
                                    elif sala_choice == '2':  # Iniciar quiz (TODO)
                                        print("\n[INFO] Funcionalidade de iniciar quiz será implementada em breve!")
                                        sleep(2)
                                    
                                    elif sala_choice == '3':  # Sair da sala
                                        print("\nSaindo da sala...")
                                        session_socket.sendall(b"SAIR_SALA")
                                        
                                        buffer_temp = ""
                                        while True:
                                            data = session_socket.recv(2048).decode()
                                            if not data:
                                                break
                                            buffer_temp += data
                                            if '\n' in buffer_temp:
                                                msg, buffer_temp = buffer_temp.split('\n', 1)
                                                if msg == "SAIU_SALA":
                                                    print("✓ Você saiu da sala.")
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
                            session_socket.sendall(f"ENTRAR_SALA:{room_id}".encode())
                            
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
                                        print(f"\n✓ Você entrou na sala '{room_id}'!")
                                        sleep(2)
                                        
                                        # Loop da sala (não é host)
                                        in_room = True
                                        while in_room:
                                            sala_choice = sala_menu(room_id, is_host=False)
                                            
                                            if sala_choice == '1':  # Ver jogadores
                                                ver_jogadores_sala(session_socket)
                                                input("\nPressione Enter para continuar...")
                                            
                                            elif sala_choice == '3':  # Sair da sala
                                                print("\nSaindo da sala...")
                                                session_socket.sendall(b"SAIR_SALA")
                                                
                                                buffer_temp = ""
                                                while True:
                                                    data = session_socket.recv(2048).decode()
                                                    if not data:
                                                        break
                                                    buffer_temp += data
                                                    if '\n' in buffer_temp:
                                                        msg, buffer_temp = buffer_temp.split('\n', 1)
                                                        if msg == "SAIU_SALA":
                                                            print("✓ Você saiu da sala.")
                                                            sleep(1)
                                                        break
                                                in_room = False
                                        
                                        break
                                    elif message.startswith("ERRO"):
                                        parts = message.split(':')
                                        if len(parts) > 1:
                                            erro = parts[1]
                                            if erro == "SALA_CHEIA":
                                                print("\n✗ Esta sala já está cheia (máximo 5 jogadores).")
                                            elif erro == "SALA_EM_JOGO":
                                                print("\n✗ Esta sala já começou o quiz.")
                                            elif erro == "SALA_NAO_ENCONTRADA":
                                                print("\n✗ Sala não encontrada.")
                                            else:
                                                print(f"\n✗ Erro: {erro}")
                                        sleep(2)
                                        break
                        else:
                            print("\nNúmero inválido.")
                            sleep(1.5)
                    except ValueError:
                        print("\nEntrada inválida.")
                        sleep(1.5)

            elif user_choice == '3':  # Ver Rankings
                ranking_choice = ranking_menu_solo()

                if ranking_choice == '3':
                    continue

                if ranking_choice == '1':
                    quiz_id_req = 'REDES_C1'
                elif ranking_choice == '2':
                    quiz_id_req = 'REDES_C2'

                # Envia requisição de ranking
                session_socket.sendall(f"PEDIR_RANKING:{quiz_id_req}".encode())
                
                # Recebe e processa a resposta com buffer
                buffer = ""
                ranking_received = False
                
                while not ranking_received:
                    data = session_socket.recv(2048).decode()
                    if not data:
                        print("\n[ERRO] Conexão perdida com o servidor.")
                        break
                    
                    buffer += data
                    
                    # Procura por uma linha completa
                    while '\n' in buffer:
                        message, buffer = buffer.split('\n', 1)
                        if not message:
                            continue
                        
                        if message.startswith("RANKING"):
                            parse_and_display(message)
                            ranking_received = True
                            break
                
                input("\nPressione Enter para voltar ao menu...")

    except ConnectionResetError:
        print("\n[ERRO] Conexão com o servidor foi perdida.")
        sleep(2)
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema: {e}")
        sleep(2)
    finally:
        session_socket.close()
        print("\nConexão encerrada.")

if __name__ == "__main__":
    main()