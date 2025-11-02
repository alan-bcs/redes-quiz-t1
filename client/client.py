import socket
from time import sleep
import traceback

from ui import show_menu, quiz_menu_solo, multiplayer_menu, sala_menu, parse_and_display
from handlers import (
    realizar_login, jogar_quiz_solo, listar_salas_disponiveis, 
    ver_jogadores_sala, ver_ranking_sala, jogar_quiz_sala
)

HOST = '127.0.0.1'
PORT = 1100


def main():

    # TELA DE LOGIN
    session_socket, player_name = realizar_login(HOST, PORT)
    if not session_socket:
        return # Falha no login

    try:
        while True:
            user_choice = show_menu(player_name)

            if user_choice == '3':  # Sair
                print('\nEncerrando sessão...')
                session_socket.sendall(b"LOGOUT\n") # Adicionado \n por segurança
                sleep(1)
                print('Até logo!')
                break
            
            elif user_choice == '1':  # Quiz Solo
                solo_choice = quiz_menu_solo()

                if solo_choice == '3':
                    continue

                quiz_id = 'REDES_C1' if solo_choice == '1' else 'REDES_C2'
                jogar_quiz_solo(session_socket, quiz_id)


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
                                
                                # Loop da sala (movido para função dedicada)
                                handle_room_loop(session_socket, room_id)
                                break
                            elif message.startswith("ERRO"):
                                parse_and_display(message)
                                sleep(2)
                                break
                
                elif mp_choice == '2':  # Entrar em sala
                    salas = listar_salas_disponiveis(session_socket)
                    
                    if salas is None or len(salas) == 0:
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
                                        
                                        # Loop da sala (movido para função dedicada)
                                        handle_room_loop(session_socket, room_id)
                                        break
                                    elif message.startswith("ERRO"):
                                        parse_and_display(message)
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
        traceback.print_exc()
        sleep(2)
    finally:
        session_socket.close()
        print("\nConexão encerrada.")

def handle_room_loop(session_socket, room_id):
    """Loop principal de interação dentro de uma sala."""
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

if __name__ == "__main__":
    main()