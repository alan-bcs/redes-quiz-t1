from time import sleep
from utils import limpar_terminal

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