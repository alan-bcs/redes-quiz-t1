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
        
        # Tenta conectar e fazer login
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            s.sendall(f"LOGIN:{player_name}".encode())
            
            # Aguarda resposta do servidor
            response = s.recv(1024).decode().strip()
            
            if response == "LOGIN_ACEITO":
                print(f"\n✓ Login realizado com sucesso! Bem-vindo(a), {player_name}!")
                sleep(1.5)
                return s, player_name  # Retorna o socket conectado e o nome
            
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

# FUNCAO PARA MOSTRAR O MENU INICIAL
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

# FUNCAO PARA TRATAR A MENSAGEM RECEBIDA DO SERVIDOR
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
                            session_socket.sendall(b"PEDIR_RANKING")

                        elif message.startswith("RANKING"):
                            input("\nPressione Enter para voltar ao menu...")
                            quiz_over = True
                            break

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