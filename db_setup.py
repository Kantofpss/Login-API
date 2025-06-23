import sqlite3
import os

def criar_banco():
    db_path = os.path.join('/data', 'users.db')
    if not os.path.exists('/data'):
        os.makedirs('/data')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            key_hash TEXT NOT NULL,
            hwid TEXT
        );
    ''')
    # Adiciona um usuário de teste
    cursor.execute('INSERT OR IGNORE INTO users (username, key_hash, hwid) VALUES (?, ?, ?)', 
                   ('testuser', 'e80b5017098950fc58aad83c8c14978e', 'test_hwid'))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_banco()