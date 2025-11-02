import threading
from questions import questionsC1, questionsC2

# Dicionário com os quizzes disponíveis
QUIZZES = {
    "REDES_C1": questionsC1,
    "REDES_C2": questionsC2
}

# CONTROLE DE USUÁRIOS LOGADOS
logged_users = set()
users_lock = threading.Lock()

# CONTROLE DE SALAS MULTIPLAYER
rooms = {}  
rooms_lock = threading.Lock()
room_counter = 0

ranking_lock = threading.Lock()