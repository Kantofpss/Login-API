from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

# Chave de verificação estática. Deve ser idêntica à do cliente para autorizar a comunicação.
CHAVE_VERIFICACAO_ESPERADA = "em-uma-noite-escura-as-corujas-observam-42"

# Banco de dados simulado para armazenar usuários, hashes de chaves e HWIDs registrados.
USUARIOS_DB = {
    "MarinLove": {
        "key_hash": hashlib.sha256("157171".encode()).hexdigest(),
        "hwid": None  # HWID Nulo: O primeiro login bem-sucedido irá registrar o HWID aqui.
    },
    "GDG": {
        "key_hash": hashlib.sha256("1022".encode()).hexdigest(),
        "hwid": None
    },
    "outro_user": {
        "key_hash": hashlib.sha256("senha123".encode()).hexdigest(),
        "hwid": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2" # Exemplo de um usuário com HWID já travado.
    }
}

@app.route('/api/login', methods=['POST'])
def handle_login():
    """
    Endpoint principal que lida com as tentativas de login.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "falha", "mensagem": "Requisição inválida, corpo JSON ausente."}), 400

    # Extrai os dados enviados pelo cliente
    usuario = data.get('usuario')
    key_recebida = data.get('key')
    hwid_cliente = data.get('hwid')
    chave_recebida = data.get('verification_key')

    # 1. Validação da chave de verificação estática
    if not chave_recebida or chave_recebida != CHAVE_VERIFICACAO_ESPERADA:
        return jsonify({"status": "falha", "mensagem": "Cliente não autorizado ou versão inválida."}), 403

    # 2. Validação dos dados recebidos
    if not all([usuario, key_recebida, hwid_cliente]):
        return jsonify({"status": "falha", "mensagem": "Dados de login incompletos."}), 400

    # 3. Validação do usuário
    if usuario not in USUARIOS_DB:
        return jsonify({"status": "falha", "mensagem": "Usuário não encontrado."}), 401

    # 4. Validação da key (senha)
    key_hash_cliente = hashlib.sha256(key_recebida.encode()).hexdigest()
    if key_hash_cliente != USUARIOS_DB[usuario]["key_hash"]:
        return jsonify({"status": "falha", "mensagem": "Key (senha) incorreta."}), 401

    # 5. Lógica de bloqueio de HWID (MODIFICADA)
    hwid_servidor = USUARIOS_DB[usuario]["hwid"]

    # Verifica se é o primeiro login ou um login de uma máquina já registrada.
    if hwid_servidor is None or hwid_servidor == hwid_cliente:
        
        # Se for o primeiro login (HWID nulo), registra o novo HWID silenciosamente.
        if hwid_servidor is None:
            USUARIOS_DB[usuario]["hwid"] = hwid_cliente
        
        # Para ambos os casos, retorna a mesma mensagem de sucesso padrão.
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido!"}), 200
    else:
        # Se o HWID recebido for diferente do registrado, o acesso é negado.
        return jsonify({"status": "falha", "mensagem": "Falha de Hardware (HWID). Acesso negado."}), 403

@app.route('/')
def index():
    """
    Página inicial simples para verificar se a API está online.
    """
    return "API de Autenticação v3.0 - Online (Static Key Auth)"

if __name__ == '__main__':
    # Roda o servidor, acessível por qualquer IP na porta 8080.
    app.run(host='0.0.0.0', port=8080)