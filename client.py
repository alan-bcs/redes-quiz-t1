import socket
import os
from time import sleep

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


# FUNCAO PARA MOSTRAR O MENU INICIAL
def show_menu():
    while True:
        limpar_terminal()
        print("\n" + "="*50)
        print("Bem-vindo ao Quiz de Redes de Computadores!")
        print("="*50)
        print("Opções:")
        print("  1. Modo de quizzes solo")
        print("  2. Modo de quizzes multiplayer")
        print("  3. Ver Rankings modo solo")
        print("  4. Ver Rankings modo multiplayer")
        print("  5. Sair")

        choice = input("Escolha uma opção: ")
        if choice in ['1', '2', '3', '4', '5']:
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
        print('  1. Capítulo 1: Introdução a Redes de Computadores') # descrever melhor depois
        print('  2. Capítulo 2: Camada de Aplicação')
        print('  3. Voltar')
        choice = input('Escolha uma opção: ')

        if choice in ['1', '2', '3']:
            return choice
        else:
            print('Opção inválida. Tente novamente.')
            sleep(1.5)


# MENU QUIZ ONLINE
def quiz_menu_online():
    while True:
        limpar_terminal()

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
        
        # printar pergunta
        print("\n" + "-"*50)
        print(f"Pergunta {num}: {text}")
        for i, opt in enumerate(options):
            print(f"  {chr(65+i)}) {opt}")
        print("-"*50)

    elif command == "RESULTADO_CORRETO":
        print("Resposta Correta!")
        sleep(1.5)
    elif command == "RESULTADO_INCORRETO":
        print("Resposta Incorreta.")
        sleep(1.5)
    elif command == "FIM_DE_JOGO":
        print("\n" + "="*50)
        print("--- Fim do Questionário! ---")
    elif command == "PONTUACAO_FINAL":
        print(f"\nSua pontuação final: {parts[1]} pontos.")
    elif command == "RANKING":
        limpar_terminal()
        print("\n--- RANKING GERAL ---")
        # parts[1] contém os dados do ranking
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

    while True:
        limpar_terminal()
        user_choice = show_menu() # PEGAR OPCAO DO USUARIO

        if user_choice == '5':
            print('Até logo!')
            break
        
        elif user_choice == '1':
            user_choice = quiz_menu_solo()

            if(user_choice == '3'):
                continue #voltar menu inicial

            if(user_choice == '1'):
                quiz_id = 'REDES_C1'
            elif(user_choice == '2'):
                quiz_id = 'REDES_C2'
            
            limpar_terminal()
            player_name = input("Digite seu nome: ").strip()
            if not player_name: player_name = "Convidado"

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT))
                    s.sendall(f"INICIAR_QUIZ:{quiz_id}:{player_name}".encode())

                    # --- LÓGICA DE RECEBIMENTO COM BUFFER ---
                    buffer = ""
                    quiz_over = False
                    while not quiz_over:
                        data = s.recv(2048).decode()
                        if not data:
                            break
                        buffer += data

                        while '\n' in buffer:
                            message, buffer = buffer.split('\n', 1)
                            if not message: continue

                            parse_and_display(message)

                            if message.startswith("PERGUNTA"):
                                num_pergunta = message.split(':')[1]
                                while True:
                                    user_answer = input("Sua resposta (A, B, C ou D): ").strip().upper()
                                    if user_answer in ['A', 'B', 'C', 'D']:
                                        s.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}".encode())
                                        break
                                    else:
                                        print("Resposta inválida.")
                            
                            elif message == "FIM_DE_JOGO":
                                s.sendall(b"PEDIR_PONTUACAO")
                            
                            elif message.startswith("PONTUACAO_FINAL"):
                                s.sendall(b"PEDIR_RANKING")

                            elif message.startswith("RANKING"):
                                input("\nPressione Enter para voltar ao menu...")
                                quiz_over = True
                                break
                
                except ConnectionRefusedError:
                    print("\n[ERRO] Não foi possível conectar ao servidor. Verifique se ele está online.")
                    sleep(2)
                except Exception as e:
                    print(f"\n[ERRO] Ocorreu um problema: {e}")
                    sleep(2)

        elif user_choice == '3':

            ranking_choice = ranking_menu_solo()

            if ranking_choice == '3':
                continue

            if(ranking_choice == '1'):
                quiz_id_req = 'REDES_C1'
            elif(ranking_choice == '2'):
                quiz_id_req = 'REDES_C2'

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT))
                    s.sendall(f"PEDIR_RANKING:{quiz_id_req}".encode())
                    # A resposta do ranking pode não ter \n, então recebemos direto
                    ranking_msg = s.recv(1024).decode()
                    if '\n' in ranking_msg: # Limpa o \n se o servidor enviar
                        ranking_msg = ranking_msg.strip()
                    parse_and_display(ranking_msg)
                    input("\nPressione Enter para voltar ao menu...")
                except ConnectionRefusedError:
                    print("\n[ERRO] Não foi possível conectar ao servidor. Verifique se ele está online.")
                    sleep(2)


if __name__ == "__main__":
    main()