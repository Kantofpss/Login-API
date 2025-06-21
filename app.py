# app.py - O CÓDIGO COMPLETO DA SUA API DE LOGIN (COM NOVO USUÁRIO)

from flask import Flask, request, jsonify
import hashlib

# Cria a aplicação Flask
app = Flask(__name__)

# --- BANCO DE DADOS SIMULADO ---
# Em um projeto real, isso seria um banco de dados de verdade (SQLite, PostgreSQL, etc.)
#
# O campo 'hwid' como 'None' indica que o usuário é novo e o HWID será
# registrado automaticamente no primeiro login bem-sucedido.
# Para segurança, armazenamos o HASH da key, e não a key em si.
USUARIOS_DB = {
    "MarinLove": {
        "key_hash": hashlib.sha256("157171".encode()).hexdigest(),
        "hwid": None
    },
    # --- NOVO USUÁRIO ADICIONADO AQUI ---
    "GDG": {
        "key_hash": hashlib.sha256("1022".encode()).hexdigest(),
        "hwid": None  # HWID será registrado no primeiro login
    },
    # Exemplo de um segundo usuário que já teria um HWID registrado
    "outro_user": {
        "key_hash": hashlib.sha256("senha123".encode()).hexdigest(),
        "hwid": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2" # HWID de exemplo
    }
}
# -----------------------------

@app.route('/api/login', methods=['POST'])
def handle_login():
    """
    Endpoint principal que lida com as tentativas de login do seu programa cliente.
    Ele espera receber um JSON com 'usuario', 'key' e 'hwid'.
    """
    # 1. Tenta obter os dados JSON enviados na requisição
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "falha", "mensagem": "Requisição sem dados JSON"}), 400
    except Exception:
        return jsonify({"status": "falha", "mensagem": "Formato de requisição inválido"}), 400

    # 2. Extrai as informações do JSON
    usuario = data.get('usuario')
    key_recebida = data.get('key')
    hwid_cliente = data.get('hwid')

    # Verifica se todos os campos necessários foram enviados
    if not all([usuario, key_recebida, hwid_cliente]):
        return jsonify({"status": "falha", "mensagem": "Dados incompletos. É necessário enviar 'usuario', 'key' e 'hwid'."}), 400

    # 3. Lógica de Autenticação
    if usuario not in USUARIOS_DB:
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado."}), 401  # Unauthorized

    # Calcula o hash da key recebida para comparar com o hash no banco de dados
    key_hash_cliente = hashlib.sha256(key_recebida.encode()).hexdigest()

    if key_hash_cliente != USUARIOS_DB[usuario]["key_hash"]:
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta."}), 401  # Unauthorized

    # 4. Lógica de Verificação e Registro de HWID
    hwid_servidor = USUARIOS_DB[usuario]["hwid"]

    if hwid_servidor is None:
        # PRIMEIRO LOGIN: O HWID no "banco de dados" está vazio.
        # Registramos o HWID do cliente e damos acesso.
        USUARIOS_DB[usuario]["hwid"] = hwid_cliente
        # Em um sistema real, você salvaria essa alteração no banco de dados aqui.
        return jsonify({
            "status": "sucesso",
            "mensagem": "Login bem-sucedido! Seu hardware foi registrado."
        }), 200

    elif hwid_servidor == hwid_cliente:
        # LOGIN NORMAL: O HWID enviado pelo cliente é o mesmo que está registrado.
        return jsonify({
            "status": "sucesso",
            "mensagem": "Login bem-sucedido!"
        }), 200

    else:
        # FALHA DE HWID: O cliente está tentando logar de uma máquina não autorizada.
        return jsonify({
            "status": "falha",
            "mensagem": "Falha de Hardware (HWID). A licença está vinculada a outro computador."
        }), 403  # Forbidden

@app.route('/')
def index():
    """ Rota inicial apenas para verificar se a API está online. """
    return "API de Autenticação v1.0 - Online"

# A linha abaixo permite rodar a API localmente para testes com o comando 'python app.py'
# A Render/Gunicorn não usará esta linha, mas é útil para desenvolvimento.
if __name__ == '__main__':
    # Roda o servidor na rede local (0.0.0.0) na porta 8080
    app.run(host='0.0.0.0', port=8080)