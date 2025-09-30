#!/usr/bin/env python3
"""
Aplicación Flask simplificada para testear imports en DigitalOcean
"""

import os
from flask import Flask
from models import db

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos DigitalOcean
DB_USER = os.getenv('DB_USER', 'doadmin')
DB_PASS = os.getenv('DB_PASS', 'AVNS_vpW0rR3lfKCIZfRnYqt')
DB_HOST = os.getenv('DB_HOST', 'uparshop-bd-do-user-26734553-0.k.db.ondigitalocean.com')
DB_PORT = os.getenv('DB_PORT', '25060')
DB_NAME = os.getenv('DB_NAME', 'uparshop_bd')

# URI para MySQL usando PyMySQL con puerto y SSL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de conexión SSL para DigitalOcean MySQL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "ssl": {"ssl_mode": "REQUIRED"}
    }
}

# Inicializar extensión con la app
db.init_app(app)

@app.route('/')
def home():
    return "¡Hola desde Uparshop! La aplicación está funcionando correctamente."

@app.route('/health')
def health():
    return {"status": "OK", "message": "Aplicación funcionando"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)