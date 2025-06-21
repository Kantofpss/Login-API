# app.py - O CÓDIGO DA SUA API

from flask import Flask, request, jsonify
import hashlib

# Cria a aplicação Flask
app = Flask(__name__)

# --- BANCO DE DADOS SIMULADO ---
# Em um projeto real, isso seria um banco de dados de verdade (SQLite, PostgreSQL, etc.)
# Para nosso exemplo, um dicionário é perfeito.
# Deixei o campo 'hwid' como None para simular o registro automático no primeiro login.
USUARIOS_DB = {
    "MarinLove": {
        "key_hash": hashlib.sha256("157171".encode()).hexdigest(), # Armazenamos o hash da key, não a key pura
        "hwid": None  # HWID será preenchido no primeiro login
    },
    "outro_user": {
        "key_hash": hashlib.sha256("senha123".encode()).hexdigest(),
        "hwid": "hwid_ja_registrado_como_exemplo"
    }
}
# -----------------------------

@app.route('/api/login', methods=['POST'])
def handle_login():
    """
    Endpoint principal que lida com as tentativas de login.
    """
    # 1. Pega os dados enviados pelo cliente (seu programa .exe)
    data = request.get_json()
    if not data:
        return jsonify({"status": "falha", "mensagem": "Dados não enviados"}), 400

    usuario = data.get('usuario')
    key = data.get('key')
    hwid_cliente = data.get('hwid')

    if not all([usuario, key, hwid_cliente]):
        return jsonify({"status": "falha", "mensagem": "Faltam dados (usuário, key ou hwid)"}), 400

    # 2. Verifica o usuário
    if usuario not in USUARIOS_DB:
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado"}), 401 # 401 Unauthorized

    # 3. Verifica a key (comparando os hashes)
    key_hash_cliente = hashlib.sha256(key.encode()).hexdigest()
    if key_hash_cliente != USUARIOS_DB[usuario]["key_hash"]:
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta"}), 401

    # 4. Verifica o HWID (lógica de registro automático)
    hwid_servidor = USUARIOS_DB[usuario]["hwid"]

    if hwid_servidor is None:
        # PRIMEIRO LOGIN: Registra o HWID do cliente no nosso "banco de dados"
        USUARIOS_DB[usuario]["hwid"] = hwid_cliente
        # Nota: Em um sistema real, você salvaria essa alteração no banco de dados.
        # Como estamos usando um dicionário, essa alteração só dura enquanto a API estiver rodando.
        # Para persistência, precisaríamos de um arquivo ou banco de dados real.
        return jsonify({
            "status": "sucesso",
            "mensagem": "Login bem-sucedido! Hardware registrado com sucesso."
        }), 200
    elif hwid_servidor == hwid_cliente:
        # LOGIN NORMAL: O HWID bate com o que está registrado
        return jsonify({
            "status": "sucesso",
            "mensagem": "Login bem-sucedido!"
        }), 200
    else:
        # FALHA DE HWID: O HWID do cliente não é o mesmo que está registrado
        return jsonify({
            "status": "falha",
            "mensagem": "Falha de autenticação de Hardware (HWID). Esta licença está em uso em outro PC."
        }), 403 # 403 Forbidden

# Rota de teste para ver se a API está no ar
@app.route('/')
def index():
    return "API de Autenticação no ar!"

# (Opcional) Para testar localmente antes de enviar para o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)