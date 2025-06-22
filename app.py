from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

# NOVO: Chave de verificação estática. Deve ser idêntica à do cliente.
CHAVE_VERIFICACAO_ESPERADA = "em-uma-noite-escura-as-corujas-observam-42"

# Banco de dados simulado
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

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "falha", "mensagem": "Requisição inválida"}), 400

    usuario = data.get('usuario')
    key_recebida = data.get('key')
    hwid_cliente = data.get('hwid')
    # NOVO: Recebe a chave de verificação do cliente
    chave_recebida = data.get('verification_key')

    # NOVO: Validação da chave de verificação estática
    if not chave_recebida or chave_recebida != CHAVE_VERIFICACAO_ESPERADA:
        return jsonify({"status": "falha", "mensagem": "Cliente não autorizado ou versão inválida."}), 403 # Forbidden

    if not all([usuario, key_recebida, hwid_cliente]):
        return jsonify({"status": "falha", "mensagem": "Dados incompletos"}), 400

    if usuario not in USUARIOS_DB:
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado"}), 401

    key_hash_cliente = hashlib.sha256(key_recebida.encode()).hexdigest()
    if key_hash_cliente != USUARIOS_DB[usuario]["key_hash"]:
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta"}), 401

    hwid_servidor = USUARIOS_DB[usuario]["hwid"]
    if hwid_servidor is None:
        USUARIOS_DB[usuario]["hwid"] = hwid_cliente
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido! Hardware registrado."}), 200
    elif hwid_servidor == hwid_cliente:
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido!"}), 200
    else:
        return jsonify({"status": "falha", "mensagem": "Falha de Hardware (HWID)"}), 403

@app.route('/')
def index():
    return "API de Autenticação v3.0 - Online (Static Key Auth)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)