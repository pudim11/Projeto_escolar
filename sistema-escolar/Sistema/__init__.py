from flask import Flask, g
import sqlite3
import os


# Defina a função get_db_connection
DATABASE = 'database.db'  # Substitua pelo caminho do seu banco de dados

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Agora podemos criar o objeto app
app = Flask(__name__)
app.secret_key = os.urandom(24)
# Mova a atribuição de configuração para dentro do contexto de aplicativo
with app.app_context():
    app.config['db_connection'] = get_db_connection()

# Agora podemos importar as rotas
from Sistema import routes