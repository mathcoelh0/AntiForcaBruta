from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login_attempts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar limitador de requisições
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

db = SQLAlchemy(app)

# Modelo para tentativas de login
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)

# Simular banco de dados de usuários
USERS = {
    'admin': 'senha123',
    'user': 'password'
}

def is_ip_blocked(ip):
    """Verifica se um IP deve ser bloqueado"""
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    failed_attempts = LoginAttempt.query.filter_by(
        ip_address=ip,
        success=False
    ).filter(
        LoginAttempt.timestamp >= fifteen_minutes_ago
    ).count()
    return failed_attempts >= 5

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Rota de login com proteção contra força bruta"""
    data = request.get_json()
    ip_address = request.remote_addr
    
    if is_ip_blocked(ip_address):
        return jsonify({
            'error': 'IP bloqueado por muitas tentativas. Tente novamente em 15 minutos.'
        }), 429

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Credenciais incompletas'}), 400

    success = USERS.get(username) == password
    
    # Registrar tentativa
    attempt = LoginAttempt(
        ip_address=ip_address,
        success=success
    )
    db.session.add(attempt)
    db.session.commit()

    if success:
        return jsonify({'message': 'Login bem-sucedido'}), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)