import os
from config import DEBUG

def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')