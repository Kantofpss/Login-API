from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

app = Flask(__name__)
# A chave secreta para JWT continua sendo necessária
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
jwt = JWTManager(app)

# --- REMOVIDO: Bloco de validação de variáveis de ambiente do banco de dados ---
# --- REMOVIDO: Bloco de conexão com o banco de dados MySQL ---

# ADICIONADO: "Banco de dados" em memória para simulação
# Em um ambiente real, isso seria carregado de um arquivo ou de um banco de dados real.
# ATENÇÃO: Estes dados são perdidos sempre que a aplicação é reiniciada.
users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "password": "hashed_password_1"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "password": "hashed_password_2"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "password": "hashed_password_3"}
]
# Para gerar novos IDs de usuário
next_user_id = 4

# Endpoint para login de administrador (sem alterações, pois não usava o DB)
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Substitua por verificação contra uma tabela de admins no banco
    if username == 'admin' and password == 'admin123':
        access_token = create_access_token(identity=username, additional_claims={'role': 'admin'})
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Credenciais inválidas'}), 401

# Endpoint para listar usuários (MODIFICADO)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    # MODIFICADO: Retorna a lista de usuários em memória diretamente
    return jsonify(users_db), 200

# Endpoint para excluir usuário (MODIFICADO)
@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    # MODIFICADO: Lógica para encontrar e remover o usuário da lista em memória
    user_to_delete = None
    for user in users_db:
        if user['id'] == user_id:
            user_to_delete = user
            break
    
    if user_to_delete:
        users_db.remove(user_to_delete)
        return jsonify({'message': 'Usuário excluído com sucesso'}), 200
    else:
        return jsonify({'message': 'Usuário não encontrado'}), 404

# ... (outros endpoints do seu app.py que você pode adicionar)
# Exemplo: Endpoint para adicionar um novo usuário (sem banco de dados)
@app.route('/admin/users', methods=['POST'])
@jwt_required()
def add_user():
    global next_user_id
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403
        
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Dados incompletos'}), 400

    new_user = {
        "id": next_user_id,
        "name": data['name'],
        "email": data['email'],
        "password": data['password'] # Em um caso real, você deveria usar bcrypt para hashear a senha
    }
    users_db.append(new_user)
    next_user_id += 1
    
    return jsonify({'message': 'Usuário adicionado com sucesso', 'user': new_user}), 201


if __name__ == '__main__':
    # Use host='0.0.0.0' para ser acessível na rede local
    # A porta pode ser definida pelo Render ou usar 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)