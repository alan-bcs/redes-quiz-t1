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
        print("  2. Modo de quizzes online")
        print("  3. Ver Rankings gerais modo online")
        print("  4. Ver Rankings gerais modo offline")
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
        print('  1. Capítulo 1: Conceitos inicias de estruturas de redes') # descrever melhor depois
        print('  2. Capítulo 2: ')
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
        sleep(1)
    elif command == "RESULTADO_INCORRETO":
        print("Resposta Incorreta.")
        sleep(1)
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

        if user_choice == '4':
            print('Até logo!')
            break
        
        elif user_choice == '1':
            user_choice = quiz_menu_solo()

            if(user_choice == '3'):
                main() #voltar para o menu inicial
                break

            if(user_choice == '1'):
                quiz_id = 'REDES_C1'
            elif(user_choice == '2'):
                quiz_id = 'REDES_C2'
            
            player_name = input("Digite seu nome: ").strip()
            if not player_name: player_name = "Convidado"

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT))
                    s.sendall(f"INICIAR_QUIZ:{quiz_id}:{player_name}".encode())

                    # Loop de comunicação com o servidor
                    while True:
                        server_msg = s.recv(2048).decode()
                        if not server_msg: break
                        
                        parse_and_display(server_msg)

                        if server_msg.startswith("PERGUNTA"):
                            num_pergunta = server_msg.split(':')[1]
                            while True:
                                user_answer = input("Sua resposta (A, B, C ou D): ").strip().upper()
                                if user_answer in ['A', 'B', 'C', 'D']:
                                    s.sendall(f"RESPONDER_PERGUNTA:{num_pergunta}:{user_answer}".encode())
                                    break
                                else:
                                    print("Resposta inválida.")
                        
                        elif server_msg == "FIM_DE_JOGO":
                            s.sendall(b"PEDIR_PONTUACAO")
                            server_msg_pontuacao = s.recv(1024).decode()
                            parse_and_display(server_msg_pontuacao)
                            
                            s.sendall(b"PEDIR_RANKING")
                            server_msg_ranking = s.recv(1024).decode()
                            parse_and_display(server_msg_ranking)
                            input("\nPressione Enter para voltar ao menu...")
                            break
                
                except ConnectionRefusedError:
                    print("\n[ERRO] Não foi possível conectar ao servidor. Verifique se ele está online.")
                    sleep(2)
                except Exception as e:
                    print(f"\n[ERRO] Ocorreu um problema: {e}")
                    sleep(2)

        elif user_choice == '3':
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT))
                    s.sendall(b"PEDIR_RANKING")
                    ranking_msg = s.recv(1024).decode()
                    parse_and_display(ranking_msg)
                    input("\nPressione Enter para voltar ao menu...")
                except ConnectionRefusedError:
                    print("\n[ERRO] Não foi possível conectar ao servidor. Verifique se ele está online.")
                    sleep(2)


if __name__ == "__main__":
    main()