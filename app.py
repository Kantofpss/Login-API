from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')  # Fallback para chave padrão
jwt = JWTManager(app)

# Validação das variáveis de ambiente
required_env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    error_msg = f"Erro: Variáveis de ambiente faltando: {', '.join(missing_vars)}. Configure-as no painel do Render ou no arquivo .env."
    app.logger.error(error_msg)
    raise ValueError(error_msg)

# Conexão com o banco de dados
try:
    db = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),  # Converte para inteiro, padrão 3306
        connection_timeout=30  # Timeout de 30 segundos
    )
    app.logger.info("Conexão com o banco de dados MySQL estabelecida com sucesso.")
except mysql.connector.Error as err:
    error_msg = f"Erro de conexão com o MySQL: {err}"
    app.logger.error(error_msg)
    raise

# Endpoint para login de administrador
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verificar credenciais do administrador (exemplo simplificado)
    # Substitua por verificação contra uma tabela de admins no banco
    if username == 'admin' and password == 'admin123':
        access_token = create_access_token(identity=username, additional_claims={'role': 'admin'})
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Credenciais inválidas'}), 401

# Endpoint para listar usuários
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
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

if __name__ == '__main__':
    app.run(debug=True)