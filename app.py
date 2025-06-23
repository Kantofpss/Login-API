from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import mysql.connector
import bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Substitua por uma chave segura
jwt = JWTManager(app)

# Conexão com o banco de dados
db = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="your_database"
)

# Endpoint para login de administrador
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verificar credenciais do administrador (exemplo simplificado)
    # Substitua por sua lógica de autenticação (ex.: consultar tabela de admins)
    if username == 'admin' and password == 'admin123':  # Substitua por verificação real
        access_token = create_access_token(identity=username, additional_claims={'role': 'admin'})
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Credenciais inválidas'}), 401

# Endpoint para listar usuários
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Verificar se o usuário é admin
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password FROM users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users), 200

# Endpoint para excluir usuário
@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Verificar se o usuário é admin
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200

# ... (outros endpoints do seu app.py)