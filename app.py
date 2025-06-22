# app.py - O CÓDIGO COMPLETO DA SUA API DE LOGIN (COM PROTEÇÃO CHALLENGE-RESPONSE)

from flask import Flask, request, jsonify
import hashlib
import os
import time

# Cria a aplicação Flask
app = Flask(__name__)

# --- BANCO DE DADOS SIMULADO ---
# Em um projeto real, isso seria um banco de dados de verdade (SQLite, PostgreSQL, etc.)
USUARIOS_DB = {
    "MarinLove": {
        "key_hash": hashlib.sha256("157171".encode()).hexdigest(),
        "hwid": None
    },
    "GDG": {
        "key_hash": hashlib.sha256("1022".encode()).hexdigest(),
        "hwid": None
    },
    "outro_user": {
        "key_hash": hashlib.sha256("senha123".encode()).hexdigest(),
        "hwid": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    }
}

# --- ARMAZENAMENTO TEMPORÁRIO DE DESAFIOS ---
# Guarda o desafio enviado para cada usuário por um curto período.
CHALLENGES = {}
CHALLENGE_EXPIRATION = 60 # Segundos

# ---------------------------------------------

@app.route('/api/request-challenge', methods=['POST'])
def request_challenge():
    """
    PRIMEIRA ETAPA DO LOGIN:
    Valida usuário e key, e se estiverem corretos, gera e retorna um desafio (challenge).
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"status": "falha", "mensagem": "Formato de requisição inválido"}), 400

    usuario = data.get('usuario')
    key_recebida = data.get('key')

    if not all([usuario, key_recebida]):
        return jsonify({"status": "falha", "mensagem": "Dados incompletos."}), 400

    # Validação de usuário e key
    if usuario not in USUARIOS_DB:
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado."}), 401

    key_hash_cliente = hashlib.sha256(key_recebida.encode()).hexdigest()
    if key_hash_cliente != USUARIOS_DB[usuario]["key_hash"]:
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta."}), 401

    # Gera um desafio único e o armazena
    challenge = os.urandom(16).hex()
    CHALLENGES[usuario] = {"challenge": challenge, "timestamp": time.time()}

    # Retorna o desafio para o cliente
    return jsonify({"status": "sucesso", "challenge": challenge}), 200


@app.route('/api/validate-response', methods=['POST'])
def validate_response():
    """
    SEGUNDA ETAPA DO LOGIN:
    Recebe a resposta do cliente (cálculo com o challenge e HWID) e valida o acesso.
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"status": "falha", "mensagem": "Formato de requisição inválido"}), 400

    usuario = data.get('usuario')
    hwid_cliente = data.get('hwid')
    response_cliente = data.get('response') # Resposta calculada pelo cliente

    if not all([usuario, hwid_cliente, response_cliente]):
        return jsonify({"status": "falha", "mensagem": "Dados incompletos."}), 400

    # Verifica se existe um desafio ativo para o usuário
    if usuario not in CHALLENGES or (time.time() - CHALLENGES[usuario]["timestamp"]) > CHALLENGE_EXPIRATION:
        return jsonify({"status": "falha", "mensagem": "Sessão inválida ou expirada. Tente logar novamente."}), 408 # Request Timeout

    challenge_servidor = CHALLENGES[usuario]["challenge"]

    # O SERVIDOR FAZ O MESMO CÁLCULO QUE O CLIENTE DEVERIA FAZER
    # Se o cracker não replicar isso, a validação falha.
    resposta_esperada = hashlib.sha256(f"{challenge_servidor}-{hwid_cliente}".encode()).hexdigest()

    if response_cliente != resposta_esperada:
        return jsonify({"status": "falha", "mensagem": "Falha na validação de segurança (challenge)."}), 403

    # Limpa o desafio para que não possa ser reutilizado
    del CHALLENGES[usuario]

    # Lógica de verificação e registro de HWID (movida para a etapa final)
    hwid_servidor = USUARIOS_DB[usuario]["hwid"]
    if hwid_servidor is None:
        USUARIOS_DB[usuario]["hwid"] = hwid_cliente
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido! Seu hardware foi registrado."}), 200
    elif hwid_servidor == hwid_cliente:
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido!"}), 200
    else:
        return jsonify({"status": "falha", "mensagem": "Falha de Hardware (HWID). A licença está vinculada a outro computador."}), 403

@app.route('/')
def index():
    """ Rota inicial apenas para verificar se a API está online. """
    return "API de Autenticação v2.0 - Online (Challenge-Response Ativado)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)