import socket
import os
from time import sleep

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


# FUNCAO PARA MOSTRAR O MENU INICIAL
def show_menu():
    while True:
        print("\n" + "="*50)
        print("Bem-vindo ao Quiz de Redes de Computadores!")
        print("="*50)
        print("Opções:")
        print("  1. Iniciar Quiz: Introdução a Redes (Capítulo 1)")
        print("  2. Ver Ranking")
        print("  3. Sair")

        choice = input("Escolha uma opção: ")
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Opção inválida. Tente novamente.")
            sleep(1.5)
            limpar_terminal()

def parse_and_display(message): #funcao para tratar a mensagem recebida
    parts = message.split(':', 1) # Separar apenas o comando do resto
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
        user_choice = show_menu()

        if user_choice == '3':
            print("Até logo!")
            break
        
        elif user_choice == '1':
            limpar_terminal()
            quiz_id = "REDES_C1"
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

        elif user_choice == '2':
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