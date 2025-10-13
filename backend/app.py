import os
import sys
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort, current_app
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
try:
    # when running from backend/ as the app root
    from models.models import db, Producto, Categoria, User, ContactMessage
except ModuleNotFoundError:
    # when running as a package (e.g., from project root)
    from backend.models.models import db, Producto, Categoria, User, ContactMessage
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

print("🚀 Iniciando aplicación Uparshop - configuración cargada")

# Inicializar la aplicación Flask con rutas dinámicas para assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegurar rutas de importación consistentes en DO App Platform y local
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
for p in [BASE_DIR, PROJECT_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

def first_existing(paths, fallback=None, ensure_dir=False):
    for p in paths:
        if os.path.exists(p):
            return p
    target = fallback or paths[-1]
    if ensure_dir:
        try:
            os.makedirs(target, exist_ok=True)
        except Exception:
            pass
    return target

TEMPLATE_DIR = first_existing([
    os.path.join(BASE_DIR, "../frontend/templates"),
    os.path.join(BASE_DIR, "frontend/templates"),
    os.path.join(BASE_DIR, "templates"),
], fallback=os.path.join(BASE_DIR, "../frontend/templates"), ensure_dir=False)
STATIC_DIR = first_existing([
    os.path.join(BASE_DIR, "../frontend/static"),
    os.path.join(BASE_DIR, "frontend/static"),
    os.path.join(BASE_DIR, "static"),
], fallback=os.path.join(BASE_DIR, "../frontend/static"), ensure_dir=False)

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)

# Logging configuration
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Configuración de la base de datos (valores por defecto si no están en env)
DB_USER = os.getenv('DB_USER') or 'doadmin'
DB_PASS = os.getenv('DB_PASS') or 'AVNS_vpW0rR3lfKCIZfRnYqt'
DB_HOST = os.getenv('DB_HOST') or 'uparshop-bd-do-user-26734553-0.k.db.ondigitalocean.com'
DB_PORT = os.getenv('DB_PORT') or '25060'
DB_NAME = os.getenv('DB_NAME') or 'uparshop_bd'

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    # Enable TLS for PyMySQL; empty dict enables SSL without strict verification
    'connect_args': {
        'ssl': {}
    },
    # Avoid stale connections on DO
    'pool_pre_ping': True
}

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uparshop-secret-key-2024-secure-flask-sessions')

db.init_app(app)

# Registrar blueprints
try:
    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)
except Exception as e:
    app.logger.warning(f"No se pudo registrar controllers.auth: {e}")

try:
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp)
except Exception as e:
    app.logger.warning(f"No se pudo registrar controllers.admin: {e}")

try:
    from routes.main import main_bp
    app.register_blueprint(main_bp)
except Exception as e:
    app.logger.warning(f"No se pudo registrar routes.main: {e}")

# Crear tablas faltantes (idempotente; solo crea las que no existen)
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Verificación de tablas completada (create_all ejecutado)")
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


@app.context_processor
def inject_cart_count():
    try:
        carrito = session.get('carrito', {}) or {}
        total = 0
        for v in carrito.values():
            try:
                total += int(v)
            except Exception:
                pass
        return {'cart_count': total}
    except Exception:
        return {'cart_count': 0}


# Global error handler to capture stacktraces in logs
@app.errorhandler(Exception)
def _handle_exception(e):
    # Don't hijack standard HTTP exceptions (404, 400, etc.)
    if isinstance(e, HTTPException):
        return e
    try:
        app.logger.exception(f"Unhandled exception: {e}")
    finally:
        return "Internal Server Error", 500


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


@app.route('/__db_health')
def __db_health():
    try:
        ok = db.session.execute(text('SELECT 1')).scalar() == 1
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tablas = inspector.get_table_names()
        return jsonify({
            'ok': ok,
            'tables': tablas,
            'has_categorias': 'categorias' in tablas,
            'has_productos': 'productos' in tablas,
            'has_usuarios': 'usuarios' in tablas,
            'has_contact_messages': 'contact_messages' in tablas
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


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


## Rutas duplicadas movidas a blueprint 'main' (ver backend/routes/main.py)


# Permite ejecutar la aplicación directamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Aplicación Uparshop iniciando en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

# Confirmar que el módulo se carga correctamente para gunicorn
print("✅ Módulo app.py cargado correctamente - Listo para gunicorn")

# Utilidades de depuración mínimas
@app.route('/__ping')
def __ping():
    return 'pong'

@app.route('/__routes')
def __routes():
    try:
        lines = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted([m for m in rule.methods if m not in ('HEAD','OPTIONS')]))
            lines.append(f"{rule.endpoint} -> {rule.rule} [{methods}]")
        return '<br>'.join(sorted(lines))
    except Exception as e:
        return f'error: {e}', 500
