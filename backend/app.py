import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort, current_app
from dotenv import load_dotenv
from models.models import db, Producto, Categoria, User, ContactMessage
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

print("🚀 Iniciando aplicación Uparshop - configuración cargada")

# Inicializar la aplicación Flask
app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")

# Configuración de la base de datos (valores por defecto si no están en env)
DB_USER = os.getenv('DB_USER') or 'doadmin'
DB_PASS = os.getenv('DB_PASS') or 'AVNS_vpW0rR3lfKCIZfRnYqt'
DB_HOST = os.getenv('DB_HOST') or 'uparshop-bd-do-user-26734553-0.k.db.ondigitalocean.com'
DB_PORT = os.getenv('DB_PORT') or '25060'
DB_NAME = os.getenv('DB_NAME') or 'uparshop_bd'

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl': {'ssl_mode': 'REQUIRED'}
    }
}

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uparshop-secret-key-2024-secure-flask-sessions')

db.init_app(app)

# Registrar blueprints
try:
    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)
except Exception as e:
    app.logger.debug(f"No se pudo registrar controllers.auth: {e}")

try:
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp)
except Exception as e:
    app.logger.debug(f"No se pudo registrar controllers.admin: {e}")

try:
    from routes.main import main_bp
    app.register_blueprint(main_bp)
except Exception as e:
    app.logger.debug(f"No se pudo registrar routes.main: {e}")

# Crear tablas faltantes (solo crea las que no existen)
with app.app_context():
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'contact_messages' not in inspector.get_table_names():
            db.create_all()
    except Exception as e:
        app.logger.warning(f"No se pudo verificar/crear tablas: {e}")


# ----------------------
# Context processors (datos comunes en templates)
# ----------------------
@app.context_processor
def inject_admin_counts():
    try:
        if session.get('user_rol') == 'admin':
            return {
                'admin_counts': {
                    'productos': Producto.query.count(),
                    'usuarios': User.query.count(),
                    'mensajes': ContactMessage.query.filter_by(leido=False).count()
                }
            }
    except Exception:
        pass
    return {'admin_counts': None}


# ----------------------
# Helpers
# ----------------------
def get_products_by_category_name(category_name):
    try:
        cat = Categoria.query.filter(Categoria.nombre.ilike(f"%{category_name}%")).first()
        if not cat:
            return []
        return Producto.query.filter_by(id_categoria=cat.id_categoria).all()
    except Exception as e:
        app.logger.error(f"Error consultando productos por categoría '{category_name}': {e}")
        return []


@app.route('/test-db')
def test_db():
    diagnostico = []
    try:
        diagnostico.append(f"🔧 DB_HOST: {DB_HOST}")
        diagnostico.append(f"🔧 DB_NAME: {DB_NAME}")
        diagnostico.append(f"🔧 DB_USER: {DB_USER}")
        diagnostico.append(f"🔧 DB_PORT: {DB_PORT}")
        diagnostico.append("<br>")
        result = db.session.execute(text('SELECT 1')).scalar()
        if result == 1:
            diagnostico.append("✅ Conexión básica a MySQL exitosa")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tablas = inspector.get_table_names()
        diagnostico.append(f"✅ Tablas encontradas: {', '.join(tablas) if tablas else 'Ninguna'}")
        try:
            categorias_count = Categoria.query.count()
            productos_count = Producto.query.count()
            usuarios_count = User.query.count()
            diagnostico.append(f"✅ Conteos: {categorias_count} categorías, {productos_count} productos, {usuarios_count} usuarios")
        except Exception as model_error:
            diagnostico.append(f"❌ Error en modelos: {model_error}")
        return "<br>".join(diagnostico)
    except Exception as e:
        return f'❌ Error de conexión a la base de datos: {e}<br><br>Configuración:<br>DB_HOST: {DB_HOST}<br>DB_NAME: {DB_NAME}<br>DB_USER: {DB_USER}'


@app.route('/debug-imagenes')
def debug_imagenes():
    if not session.get('user_rol') == 'admin':
        return "Acceso denegado", 403
    try:
        productos = Producto.query.limit(10).all()
        html = "<h2>Debug: URLs de imágenes</h2><table border='1'>"
        html += "<tr><th>Producto</th><th>imagen_url en BD</th><th>Test imagen</th></tr>"
        for producto in productos:
            html += f"<tr><td>{producto.nombre}</td><td>{producto.imagen_url}</td>"
            if producto.imagen_url:
                html += f"<td><img src='{producto.imagen_url}' width='100' onerror=\"this.src='/static/images/product-placeholder.svg'\"></td>"
            else:
                html += "<td>Sin imagen</td>"
            html += "</tr>"
        html += "</table>"
        return html
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/debug-estructura-tabla')
def debug_estructura_tabla():
    if not session.get('user_rol') == 'admin':
        return "Acceso denegado", 403
    try:
        result = db.session.execute(text("DESCRIBE productos"))
        columnas = []
        for row in result:
            columnas.append({
                'campo': row[0],
                'tipo': row[1],
                'nulo': row[2],
                'clave': row[3],
                'default': row[4],
                'extra': row[5]
            })
        html = "<h2>Estructura de la tabla productos</h2><table border='1'>"
        html += "<tr><th>Campo</th><th>Tipo</th><th>Nulo</th><th>Clave</th><th>Default</th><th>Extra</th></tr>"
        for col in columnas:
            html += f"<tr><td>{col['campo']}</td><td>{col['tipo']}</td><td>{col['nulo']}</td><td>{col['clave']}</td><td>{col['default']}</td><td>{col['extra']}</td></tr>"
        html += "</table>"
        return html
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/debug-categorias')
def debug_categorias():
    try:
        categorias = Categoria.query.all()
        if not categorias:
            return "❌ No hay categorías en la base de datos.<br><br><a href='/'>Volver al inicio</a>"
        resultado = ["📋 Categorías existentes en la base de datos:<br><br>"]
        for cat in categorias:
            productos_count = Producto.query.filter_by(id_categoria=cat.id_categoria).count()
            resultado.append(f"• ID: {cat.id_categoria} | Nombre: '{cat.nombre}' | Productos: {productos_count}")
        resultado.append("<br><br><a href='/'>Volver al inicio</a>")
        return "<br>".join(resultado)
    except Exception as e:
        return f"❌ Error al consultar categorías: {e}"


@app.route('/test-simple')
def test_simple():
    return "✅ Aplicación funcionando correctamente - Sin consultas a BD"


@app.route('/test-home')
def test_home():
    try:
        productos_destacados = Producto.query.order_by(Producto.id_producto.desc()).limit(8).all()
        return f"✅ Consulta exitosa - Encontrados {len(productos_destacados)} productos destacados"
    except Exception as e:
        return f"❌ Error en consulta: {e}"


# Permite ejecutar la aplicación directamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Aplicación Uparshop iniciando en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

# Confirmar que el módulo se carga correctamente para gunicorn
print("✅ Módulo app.py cargado correctamente - Listo para gunicorn")
