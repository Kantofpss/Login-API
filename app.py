from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import hashlib

app = Flask(__name__)
CORS(app)  # Habilita CORS para suportar requisições de diferentes origens

# Chave de verificação para o cliente de login
CHAVE_VERIFICACAO_ESPERADA = "em-uma-noite-escura-as-corujas-observam-42"
# Senha simples para proteger o painel de admin
SENHA_ADMIN = "admin123"

def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

# --- ROTA DE LOGIN DO CLIENTE ---
@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    usuario = data.get('usuario')
    key_recebida = data.get('key')
    hwid_cliente = data.get('hwid')
    
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE username = ?', (usuario,)).fetchone()
    
    if not user_data:
        conn.close()
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado."}), 401

    key_hash_cliente = hashlib.sha256(key_recebida.encode()).hexdigest()
    if key_hash_cliente != user_data['key_hash']:
        conn.close()
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta."}), 401

    hwid_servidor = user_data['hwid']

    if hwid_servidor is None or hwid_servidor == hwid_cliente:
        if hwid_servidor is None:
            conn.execute('UPDATE users SET hwid = ? WHERE username = ?', (hwid_cliente, usuario))
            conn.commit()
        conn.close()
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido!"}), 200
    else:
        conn.close()
        return jsonify({"status": "falha", "mensagem": "Falha de Hardware (HWID). Acesso negado."}), 403

# --- ROTAS DO PAINEL DE ADMIN ---
@app.route('/admin')
def admin_panel():
    """Serve a página HTML do painel de admin."""
    try:
        return render_template('admin.html')
    except Exception as e:
        return str(e), 500

@app.route('/admin/api/users', methods=['POST'])
def get_all_users():
    """API para listar todos os usuários. Requer senha de admin."""
    data = request.get_json()
    print(f"Requisição recebida: {data}")  # Log para depuração
    if not data or data.get('password') != SENHA_ADMIN:
        return jsonify({"error": "Acesso não autorizado"}), 403
        
    conn = get_db_connection()
    try:
        users_cursor = conn.execute('SELECT username, hwid FROM users').fetchall()
        users_list = [dict(row) for row in users_cursor]
        return jsonify(users_list)
    except sqlite3.OperationalError as e:
        print(f"Erro no banco de dados: {e}")
        return jsonify({"error": "Erro no servidor: tabela 'users' não encontrada. Execute db_setup.py."}), 500
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"error": "Erro inesperado no servidor"}), 500
    finally:
        conn.close()

@app.route('/admin/api/create_user', methods=['POST'])
def create_user():
    """API para criar um novo usuário. Requer senha de admin."""
    data = request.get_json()
    if not data or data.get('password') != SENHA_ADMIN:
        return jsonify({"error": "Acesso não autorizado"}), 403

    username = data.get('username')
    password = data.get('password_user')  # Nova senha do usuário
    if not username or not password:
        return jsonify({"error": "Nome de usuário e senha são obrigatórios"}), 400

    conn = get_db_connection()
    try:
        # Verifica se o usuário já existe
        existing_user = conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            return jsonify({"error": "Usuário já existe"}), 400

        # Hashea a senha do usuário
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        conn.execute('INSERT INTO users (username, key_hash, hwid) VALUES (?, ?, NULL)', (username, key_hash))
        conn.commit()
        return jsonify({"success": f"Usuário '{username}' criado com sucesso!"})
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return jsonify({"error": "Erro ao criar usuário"}), 500
    finally:
        conn.close()

@app.route('/admin/api/reset_hwid', methods=['POST'])
def reset_user_hwid():
    """API para resetar o HWID de um usuário. Requer senha de admin."""
    data = request.get_json()
    if not data or data.get('password') != SENHA_ADMIN:
        return jsonify({"error": "Acesso não autorizado"}), 403

    username_to_reset = data.get('username')
    if not username_to_reset:
        return jsonify({"error": "Nome de usuário não fornecido"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE users SET hwid = NULL WHERE username = ?', (username_to_reset,))
    conn.commit()
    conn.close()

    return jsonify({"success": f"HWID para o usuário '{username_to_reset}' foi resetado."})

@app.route('/')
def index():
    return "API de Autenticação v4.0 - Online (DB + Admin Panel)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)