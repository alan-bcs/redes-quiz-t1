from state import rooms, rooms_lock, room_counter

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