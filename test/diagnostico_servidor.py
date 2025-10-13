#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas en el servidor DigitalOcean
Ejecutar en el servidor: python diagnostico_servidor.py
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 DIAGNÓSTICO DE SERVIDOR DIGITALOCEAN")
print("="*50)

# Test 1: Importaciones básicas
print("\n1️⃣ Probando importaciones básicas...")
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Error importando Flask: {e}")

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ Error importando SQLAlchemy: {e}")

try:
    import pymysql
    print(f"✅ PyMySQL disponible")
except ImportError as e:
    print(f"❌ Error importando PyMySQL: {e}")

# Test 2: Variables de entorno
print("\n2️⃣ Verificando variables de entorno...")
env_vars = ['DB_USER', 'DB_PASS', 'DB_HOST', 'DB_PORT', 'DB_NAME']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'PASS' in var:
            print(f"✅ {var}: [OCULTA]")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"⚠️ {var}: No configurada (usando default)")

# Test 3: Crear app básica
print("\n3️⃣ Creando aplicación Flask básica...")
try:
    from flask import Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    print("✅ App Flask creada")
except Exception as e:
    print(f"❌ Error creando app Flask: {e}")
    traceback.print_exc()

# Test 4: Configuración de BD
print("\n4️⃣ Probando configuración de base de datos...")
try:
    DB_USER = os.getenv('DB_USER', 'doadmin')
    DB_PASS = os.getenv('DB_PASS', 'AVNS_vpW0rR3lfKCIZfRnYqt')
    DB_HOST = os.getenv('DB_HOST', 'uparshop-bd-do-user-26734553-0.k.db.ondigitalocean.com')
    DB_PORT = os.getenv('DB_PORT', '25060')
    DB_NAME = os.getenv('DB_NAME', 'uparshop_bd')
    
    database_uri = f"mysql+pymysql://{DB_USER}:{DB_PASS[:5]}...@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"✅ URI de BD construida: {database_uri}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "ssl": {"ssl_mode": "REQUIRED"}
        }
    }
    print("✅ Configuración de BD aplicada")
except Exception as e:
    print(f"❌ Error en configuración de BD: {e}")
    traceback.print_exc()

# Test 5: Inicializar SQLAlchemy
print("\n5️⃣ Inicializando SQLAlchemy...")
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    db.init_app(app)
    print("✅ SQLAlchemy inicializado")
except Exception as e:
    print(f"❌ Error inicializando SQLAlchemy: {e}")
    traceback.print_exc()

# Test 6: Conexión a BD
print("\n6️⃣ Probando conexión a base de datos...")
try:
    with app.app_context():
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1')).scalar()
        if result == 1:
            print("✅ Conexión a BD exitosa")
        else:
            print("❌ Conexión establecida pero query falló")
except Exception as e:
    print(f"❌ Error de conexión a BD: {e}")
    traceback.print_exc()

# Test 7: Importar modelos actuales
print("\n7️⃣ Probando modelos actuales...")
try:
    from models.models import User, Producto, Categoria, ContactMessage
    print("✅ Modelos importados exitosamente")
    
    # Probar crear instancia de cada modelo (sin guardar)
    with app.app_context():
        try:
            user = User(nombre_completo="Test", correo="test@test.com", contrasena="test")
            print("✅ Modelo User funciona")
        except Exception as e:
            print(f"❌ Error en modelo User: {e}")
        
        try:
            cat = Categoria(nombre="Test Cat", estado="activo")
            print("✅ Modelo Categoria funciona")
        except Exception as e:
            print(f"❌ Error en modelo Categoria: {e}")
        
        try:
            prod = Producto(nombre="Test Prod", descripcion_detallada="Test", precio_unitario=100, cantidad_stock=1, stock_minimo=0, stock_maximo=10, estado="activo")
            print("✅ Modelo Producto funciona")
        except Exception as e:
            print(f"❌ Error en modelo Producto: {e}")
        
        try:
            msg = ContactMessage(nombre="Test", correo="test@test.com", mensaje="Test")
            print("✅ Modelo ContactMessage funciona")
        except Exception as e:
            print(f"❌ Error en modelo ContactMessage: {e}")

except Exception as e:
    print(f"❌ Error importando modelos: {e}")
    traceback.print_exc()

# Test 8: Probar ruta básica
print("\n8️⃣ Probando ruta básica...")
try:
    @app.route('/test')
    def test_route():
        return "Test OK"
    
    with app.test_client() as client:
        response = client.get('/test')
        if response.status_code == 200:
            print("✅ Ruta de test funciona")
        else:
            print(f"❌ Ruta de test falló: {response.status_code}")
except Exception as e:
    print(f"❌ Error en ruta de test: {e}")
    traceback.print_exc()

# Test 9: Verificar estructura de tablas
print("\n9️⃣ Verificando estructura actual de tablas...")
try:
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        tables = ['usuarios', 'productos', 'categorias']
        for table_name in tables:
            if table_name in inspector.get_table_names():
                print(f"\n✅ Tabla '{table_name}' existe:")
                columns = inspector.get_columns(table_name)
                for col in columns:
                    col_type = str(col['type'])
                    print(f"   {col['name']}: {col_type}")
            else:
                print(f"❌ Tabla '{table_name}' NO existe")
                
except Exception as e:
    print(f"❌ Error verificando estructura: {e}")
    traceback.print_exc()

print("\n" + "="*50)
print("🏁 DIAGNÓSTICO COMPLETADO")
print("="*50)
print("\n💡 Si hay errores:")
print("   1. Revisa los logs de tu servidor web (nginx/apache)")
print("   2. Revisa los logs de tu aplicación Flask")
print("   3. Verifica que las dependencias estén instaladas")
print("   4. Considera usar models_safe.py temporalmente")