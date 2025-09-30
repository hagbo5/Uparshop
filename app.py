
import os
from flask import session, redirect, url_for, request, flash
from flask import abort
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from models import db, Producto, Categoria, User, ContactMessage
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

# Inicializar la aplicación Flask
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

# Crear tablas faltantes (solo crea las que no existen) — solución rápida sin migraciones.
with app.app_context():
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'contact_messages' not in inspector.get_table_names():
            db.create_all()  # crea únicamente tablas que falten
    except Exception as e:
        app.logger.warning(f"No se pudo verificar/crear tablas: {e}")

# ----------------------
# Context processors (datos comunes en templates)
# ----------------------
@app.context_processor
def inject_admin_counts():
    """Proporciona conteos básicos para badges del panel admin.
    Se retornan solo si el usuario es admin para evitar queries innecesarias a usuarios normales.
    """
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
    """Busca productos por el nombre de la categoría. Devuelve lista de Producto.
    Si hay errores o la categoría no existe, devuelve lista vacía.
    """
    try:
        # Buscar categoría parcial (case-insensitive)
        cat = Categoria.query.filter(Categoria.nombre.ilike(f"%{category_name}%")).first()
        if not cat:
            return []
        return Producto.query.filter_by(id_categoria=cat.id_categoria).all()
    except Exception as e:
        app.logger.error(f"Error consultando productos por categoría '{category_name}': {e}")
        return []

# ----------------------
# RUTAS
# ----------------------
@app.route('/')
def home():
    """Página principal"""
    productos_destacados = Producto.query.order_by(Producto.id_producto.desc()).limit(8).all()
    return render_template('index.html', productos_destacados=productos_destacados)

@app.route('/lista-precios')
def lista_precios():
    """Página de lista de precios"""
    return render_template('lista_precios.html')

@app.route('/sobre-nosotros')
def sobre_nosotros():
    """Página sobre nosotros"""
    return render_template('sobre_nosotros.html')
@app.route('/torres')
def torres():
    """Página de categorías 'Torres', muestra los desktops disponibles."""
    desktops = get_products_by_category_name('Torres')
    return render_template('torres.html', desktops=desktops)


@app.route('/laptops')
def laptops():
    """Página de categoría 'Laptops'"""
    laptops = get_products_by_category_name('Laptops')
    return render_template('laptops.html', laptops=laptops)


@app.route('/procesadores')
def procesadores():
    productos = get_products_by_category_name('Procesadores')
    return render_template('procesadores.html', productos=productos)


@app.route('/tarjetas-graficas')
def tarjetas_graficas():
    productos = get_products_by_category_name('Tarjetas Graficas')
    return render_template('tarjetas_graficas.html', productos=productos)


@app.route('/perifericos')
def perifericos():
    productos = get_products_by_category_name('Perifericos')
    return render_template('perifericos.html', productos=productos)


@app.route('/memorias')
def memorias():
    productos = get_products_by_category_name('Memorias')
    return render_template('memorias.html', productos=productos)


@app.route('/fuentes')
def fuentes():
    productos = get_products_by_category_name('Fuentes')
    return render_template('fuentes.html', productos=productos)


@app.route('/juegos')
def juegos():
    productos = get_products_by_category_name('Juegos')
    return render_template('juegos.html', productos=productos)


@app.route('/contactanos', methods=['GET'])
def contactanos():
    """Página de contacto"""
    return render_template('contactanos.html')


@app.route('/contactanos', methods=['POST'])
def contactanos_post():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    asunto = request.form.get('asunto', '').strip()
    mensaje = request.form.get('mensaje', '').strip()
    if not nombre or not correo or not mensaje:
        flash('Por favor completa nombre, correo y mensaje.', 'error')
        return redirect(url_for('contactanos'))
    try:
        cm = ContactMessage(nombre=nombre, correo=correo, asunto=asunto, mensaje=mensaje)
        db.session.add(cm)
        db.session.commit()
        flash('Mensaje enviado. Gracias por contactarnos.', 'success')
    except Exception as e:
        app.logger.error(f"Error al guardar mensaje de contacto: {e}")
        flash('Ocurrió un error al enviar tu mensaje. Intenta más tarde.', 'error')
    return redirect(url_for('contactanos'))


@app.route('/admin/mensajes')
def admin_mensajes():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))

    # Parámetros de filtrado (server-side)
    q = request.args.get('q', '').strip()
    estado = request.args.get('estado', '').strip()  # '', 'noleidos', 'leidos'
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ContactMessage.query
    # Búsqueda textual básica
    if q:
        like = f"%{q}%"
        query = query.filter(
            (ContactMessage.nombre.ilike(like)) |
            (ContactMessage.correo.ilike(like)) |
            (ContactMessage.asunto.ilike(like)) |
            (ContactMessage.mensaje.ilike(like))
        )
    # Estado leído/no leído
    if estado == 'noleidos':
        query = query.filter(ContactMessage.leido.is_(False))
    elif estado == 'leidos':
        query = query.filter(ContactMessage.leido.is_(True))
    # Rango de fechas (inclusive)
    def parse_date(val):
        try:
            return datetime.strptime(val, '%Y-%m-%d')
        except Exception:
            return None
    dt_desde = parse_date(fecha_desde) if fecha_desde else None
    dt_hasta = parse_date(fecha_hasta) if fecha_hasta else None
    if dt_desde:
        query = query.filter(ContactMessage.creado_at >= dt_desde)
    if dt_hasta:
        # sumar un día y usar < próximo día para incluir todo el día seleccionado
        query = query.filter(ContactMessage.creado_at < (dt_hasta + timedelta(days=1)))

    try:
        pagination = query.order_by(ContactMessage.creado_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        mensajes = pagination.items
        total = pagination.total
    except Exception as e:
        app.logger.error(f"Error al listar mensajes de contacto: {e}")
        mensajes = query.order_by(ContactMessage.creado_at.desc()).all()
        total = len(mensajes)
        pagination = None
    return render_template(
        'admin_mensajes.html', mensajes=mensajes, pagination=pagination, total=total,
        q=q, estado=estado, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, per_page=per_page
    )


@app.route('/admin/mensajes/marcar', methods=['POST'])
def admin_mensajes_marcar():
    if not session.get('user_rol') == 'admin':
        # Si no es admin devolver JSON o redirect según cabecera
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'Acceso denegado'}), 403
        flash('Acceso denegado.', 'error')
        return redirect(url_for('admin_mensajes'))

    # Soporta tanto form-data como JSON
    message_id = request.form.get('id') or (request.json and request.json.get('id'))
    mark = request.form.get('mark') or (request.json and request.json.get('mark'))
    if not message_id:
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'ID faltante'}), 400
        flash('ID faltante.', 'error')
        return redirect(url_for('admin_mensajes'))
    try:
        msg = ContactMessage.query.get(int(message_id))
        if not msg:
            if request.headers.get('Accept','').startswith('application/json'):
                return jsonify({'ok': False, 'error': 'Mensaje no encontrado'}), 404
            flash('Mensaje no encontrado.', 'error')
            return redirect(url_for('admin_mensajes'))
        if mark == 'read':
            msg.leido = True
        elif mark == 'unread':
            msg.leido = False
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': True})
        # Fallback HTML
        flash('Mensaje actualizado.', 'success')
        return redirect(url_for('admin_mensajes'))
    except Exception as e:
        app.logger.error(f"Error al marcar mensaje: {e}")
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'Error interno'}), 500
        flash('Error interno al actualizar mensaje.', 'error')
        return redirect(url_for('admin_mensajes'))


@app.route('/admin/mensajes/<int:message_id>/json')
def admin_mensaje_json(message_id):
    if not session.get('user_rol') == 'admin':
        return jsonify({'ok': False, 'error': 'Acceso denegado'}), 403
    msg = ContactMessage.query.get_or_404(message_id)
    return jsonify({
        'ok': True,
        'id': msg.id,
        'nombre': msg.nombre,
        'correo': msg.correo,
        'asunto': msg.asunto,
        'mensaje': msg.mensaje,
        'creado_at': msg.creado_at.strftime('%Y-%m-%d %H:%M'),
        'leido': msg.leido
    })


@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    productos = []
    if q:
        try:
            # buscar por nombre o descripción (case-insensitive)
            productos = Producto.query.filter(
                (Producto.nombre.ilike(f"%{q}%")) | (Producto.descripcion_detallada.ilike(f"%{q}%"))
            ).all()
        except Exception as e:
            app.logger.error(f"Error en búsqueda: {e}")
            productos = []
    # Resolver rutas de imagen para cada producto (comprueba filesystem)
    try:
        static_root = os.path.join(app.root_path, 'static')
        for p in productos:
            img = getattr(p, 'imagen', '') or ''
            # si es URL absoluta
            if img and img.startswith('http'):
                p.imagen_web = img
                continue

            # Normalizar valores que pueden venir con prefijos como '/static/' o 'static/'
            normalized = img.lstrip('/')
            if normalized.startswith('static/'):
                normalized = normalized.split('static/', 1)[1]
            # ahora normalized puede ser 'images/productos/archivo.jpg' o 'productos/archivo.jpg' o 'archivo.jpg'

            # Construir candidatos a comprobar en el filesystem (más específicos primero)
            candidates = []
            if normalized:
                candidates.append(os.path.join(static_root, normalized))
                # if starts with 'productos/' or 'images/productos/' keep, else try images/productos/<basename>
                base = os.path.basename(normalized)
                candidates.append(os.path.join(static_root, 'images', 'productos', base))
                candidates.append(os.path.join(static_root, 'images', base))
            else:
                candidates.append(os.path.join(static_root, 'images', 'Uparshop-logo.png'))

            found = None
            for cand in candidates:
                try:
                    if cand and os.path.isfile(cand):
                        found = cand
                        break
                except Exception:
                    continue

            if found:
                # construir url relativa para url_for
                rel = os.path.relpath(found, static_root).replace('\\', '/')
                p.imagen_web = url_for('static', filename=rel)
            else:
                p.imagen_web = url_for('static', filename='images/Uparshop-logo.png')
    except Exception as e:
        app.logger.debug(f"Error resolviendo imágenes: {e}")
        for p in productos:
            p.imagen_web = url_for('static', filename='images/Uparshop-logo.png')

    return render_template('search_results.html', query=q, productos=productos)


# --- VER CARRITO ---
@app.route('/carrito')
def ver_carrito():
    from models import Producto
    carrito = session.get('carrito', {})
    productos = []
    total = 0
    for id_str, cantidad in carrito.items():
        producto = Producto.query.get(int(id_str))
        if producto:
            productos.append({'producto': producto, 'cantidad': cantidad})
            total += producto.precio_unitario * cantidad
    return render_template('carrito.html', productos=productos, total=total)

# --- ACTUALIZAR CANTIDADES DEL CARRITO ---
@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    carrito = session.get('carrito', {})
    # Si se presionó el botón eliminar
    eliminar_id = request.form.get('eliminar')
    if eliminar_id:
        carrito.pop(str(eliminar_id), None)
        session['carrito'] = carrito
        flash('Producto eliminado del carrito.', 'success')
        return redirect(url_for('ver_carrito'))
    # Si solo se actualizaron cantidades
    for key in request.form:
        if key.startswith('cantidades['):
            producto_id = key.split('[')[1].split(']')[0]
            try:
                cantidad = int(request.form[key])
                if cantidad > 0:
                    carrito[producto_id] = cantidad
                else:
                    carrito.pop(producto_id, None)
            except ValueError:
                continue
    session['carrito'] = carrito
    flash('Carrito actualizado.', 'success')
    return redirect(url_for('ver_carrito'))


# --- ELIMINAR PRODUCTO DEL CARRITO ---
@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    carrito = session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    session['carrito'] = carrito
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('ver_carrito'))


@app.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    from models import Producto
    producto = Producto.query.get(producto_id)
    if not producto:
        abort(404)
    return render_template('product_detail.html', producto=producto)

@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    from models import Producto
    producto = Producto.query.get(producto_id)
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(request.referrer or url_for('index'))
    carrito = session.get('carrito', {})
    cantidad_actual = carrito.get(str(producto_id), 0)
    if cantidad_actual + 1 > producto.cantidad_stock:
        flash('No puedes agregar más de la cantidad disponible en stock.', 'error')
        return redirect(request.referrer or url_for('producto_detalle', producto_id=producto_id))
    carrito[str(producto_id)] = cantidad_actual + 1
    session['carrito'] = carrito
    # Redirigir con parámetro para animación
    ref = request.referrer or url_for('producto_detalle', producto_id=producto_id)
    if '?' in ref:
        ref += '&carrito_anim=1'
    else:
        ref += '?carrito_anim=1'
    flash('Producto agregado al carrito.', 'success')
    return redirect(ref)


# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    # POST: procesar formulario
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        flash('Correo y contraseña son requeridos.', 'error')
        return redirect(url_for('login'))
    user = User.query.filter_by(correo=email).first()
    if user:
        if user.estado != 'activo':
            flash('Tu cuenta se encuentra inactiva. Por favor comunícate con soporte técnico.', 'error')
            return redirect(url_for('login'))
        if user.contrasena == password:
            session['user_id'] = user.id_usuario
            session['user_email'] = user.correo
            session['user_rol'] = user.rol
            flash('Sesión iniciada.', 'success')
            return redirect(url_for('home'))
    flash('Credenciales inválidas.', 'error')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    # Solo permite acceso si el usuario es admin
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    return render_template('admin.html')


@app.route('/admin/usuarios')
def admin_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))

    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = User.query
    if q:
        query = query.filter((User.nombre_completo.ilike(f"%{q}%")) | (User.correo.ilike(f"%{q}%")))

    try:
        pagination = query.order_by(User.id_usuario.asc()).paginate(page=page, per_page=per_page, error_out=False)
        usuarios = pagination.items
        total = pagination.total
    except Exception as e:
        app.logger.error(f"Error al listar usuarios en admin: {e}")
        usuarios = query.order_by(User.id_usuario.asc()).all()
        total = len(usuarios)
        pagination = None

    return render_template('admin_usuario.html', usuarios=usuarios, q=q, pagination=pagination, total=total, per_page=per_page)


@app.route('/admin/productos')
def admin_productos():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))

    # Parámetros de filtrado
    q = request.args.get('q', '').strip()
    id_categoria = request.args.get('id_categoria', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Construir la consulta dinámicamente
    query = Producto.query
    if q:
        query = query.filter((Producto.nombre.ilike(f"%{q}%")) | (Producto.descripcion_detallada.ilike(f"%{q}%")))
    if id_categoria:
        try:
            query = query.filter(Producto.id_categoria == int(id_categoria))
        except Exception:
            pass
    if min_price:
        try:
            query = query.filter(Producto.precio_unitario >= float(min_price))
        except Exception:
            pass
    if max_price:
        try:
            query = query.filter(Producto.precio_unitario <= float(max_price))
        except Exception:
            pass

    try:
        pagination = query.order_by(Producto.id_producto.desc()).paginate(page=page, per_page=per_page, error_out=False)
        productos = pagination.items
        total = pagination.total
    except Exception as e:
        app.logger.error(f"Error al listar productos en admin: {e}")
        productos = query.order_by(Producto.id_producto.desc()).all()
        total = len(productos)
        pagination = None

    # Enviar categorías para el filtro
    categorias = Categoria.query.all()

    return render_template(
        'admin_productos.html', productos=productos, q=q,
        id_categoria=id_categoria, min_price=min_price, max_price=max_price,
        pagination=pagination, total=total, categorias=categorias, per_page=per_page
    )


@app.route('/admin/productos/autocomplete')
def autocomplete_admin_productos():
    """Endpoint AJAX que devuelve sugerencias (JSON) para autocompletar nombres de producto."""
    if not session.get('user_rol') == 'admin':
        return jsonify([])
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        results = Producto.query.filter(Producto.nombre.ilike(f"%{q}%")).limit(10).all()
        suggestions = [{'id': p.id_producto, 'nombre': p.nombre} for p in results]
        return jsonify(suggestions)
    except Exception as e:
        app.logger.error(f"Error en autocomplete admin productos: {e}")
        return jsonify([])


@app.route('/crear-cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'GET':
        return render_template('crear_cuenta.html')
    # POST: procesar formulario
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if not nombre or not email or not password or not password2:
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('crear_cuenta'))
    if password != password2:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('crear_cuenta'))
    if User.query.filter_by(correo=email).first():
        flash('El correo ya está registrado.', 'error')
        return redirect(url_for('crear_cuenta'))
    nuevo_usuario = User(
        nombre_completo=nombre,
        correo=email,
        contrasena=password,
        rol='cliente',
        estado='activo'
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
    return redirect(url_for('login'))


@app.route('/test-db')
def test_db():
    try:
        # Ejecuta una consulta simple para verificar la conexión
        result = db.session.execute(text('SELECT 1')).scalar()
        if result == 1:
            return 'Conexión exitosa a la base de datos MySQL (XAMPP) uparshop_bd.'
        else:
            return 'Conexión establecida, pero la consulta no devolvió el resultado esperado.'
    except Exception as e:
        return f'Error de conexión a la base de datos: {e}'


@app.route('/admin/usuarios/cambiar-rol', methods=['POST'])
def cambiar_rol_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    usuario_id = request.form.get('usuario_id')
    nuevo_rol = request.form.get('rol')
    if not usuario_id or not nuevo_rol:
        flash('Datos incompletos para cambiar el rol.', 'error')
        return redirect(url_for('admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1 and usuario.rol != nuevo_rol:
        usuario.rol = nuevo_rol
        db.session.commit()
        flash(f'Rol actualizado para {usuario.nombre_completo}.', 'success')
    else:
        flash('No se pudo actualizar el rol o el usuario está protegido.', 'info')
    return redirect(url_for('admin_usuario'))


@app.route('/admin/usuarios/cambiar-estado', methods=['POST'])
def cambiar_estado_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    usuario_id = request.form.get('usuario_id')
    nuevo_estado = request.form.get('estado')
    if not usuario_id or not nuevo_estado:
        flash('Datos incompletos para cambiar el estado.', 'error')
        return redirect(url_for('admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1 and usuario.estado != nuevo_estado:
        usuario.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado actualizado para {usuario.nombre_completo}.', 'success')
    else:
        flash('No se pudo actualizar el estado o el usuario está protegido.', 'info')
    return redirect(url_for('admin_usuario'))


@app.route('/admin/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    if usuario_id == 1:
        flash('El usuario 1 no puede ser editado.', 'error')
        return redirect(url_for('admin_usuario'))
    usuario = User.query.get_or_404(usuario_id)
    if request.method == 'GET':
        return render_template('editar_usuario.html', usuario=usuario)
    # POST: procesar edición
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    identificacion = request.form.get('identificacion')
    direccion = request.form.get('direccion')
    telefono_contacto = request.form.get('telefono_contacto')
    if not nombre or not email:
        flash('Nombre y correo son obligatorios.', 'error')
        return redirect(url_for('editar_usuario', usuario_id=usuario_id))
    if User.query.filter(User.correo == email, User.id_usuario != usuario_id).first():
        flash('El correo ya está registrado por otro usuario.', 'error')
        return redirect(url_for('editar_usuario', usuario_id=usuario_id))
    usuario.nombre_completo = nombre
    usuario.correo = email
    usuario.identificacion = identificacion
    usuario.direccion = direccion
    usuario.telefono_contacto = telefono_contacto
    db.session.commit()
    flash('Usuario actualizado correctamente.', 'success')
    return redirect(url_for('admin_usuario'))


@app.route('/admin/usuarios/eliminar', methods=['POST'])
def eliminar_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    usuario_id = request.form.get('usuario_id')
    if not usuario_id:
        flash('ID de usuario no proporcionado.', 'error')
        return redirect(url_for('admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'success')
    else:
        flash('No se puede eliminar el usuario seleccionado.', 'error')
    return redirect(url_for('admin_usuario'))


@app.route('/admin/productos/registrar', methods=['GET', 'POST'])
def registrar_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    from models import Categoria
    if request.method == 'GET':
        categorias = Categoria.query.all()
        return render_template('registrar_producto.html', categorias=categorias)
    # POST: procesar registro
    nombre = request.form.get('nombre')
    descripcion_detallada = request.form.get('descripcion_detallada')
    precio_unitario = request.form.get('precio_unitario')
    cantidad_stock = request.form.get('cantidad_stock')
    stock_minimo = request.form.get('stock_minimo')
    stock_maximo = request.form.get('stock_maximo')
    id_categoria = request.form.get('id_categoria')
    estado = request.form.get('estado')
    garantia_fecha = request.form.get('garantia_fecha')
    unidad = request.form.get('unidad')

    # Manejo de imagen subida
    imagen_file = request.files.get('imagen')
    imagen_url = None
    if imagen_file and imagen_file.filename:
        import os
        from werkzeug.utils import secure_filename
        # Ruta absoluta a la carpeta static/productos dentro del proyecto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        productos_dir = os.path.join(base_dir, 'static', 'productos')
        if not os.path.exists(productos_dir):
            os.makedirs(productos_dir)
        filename = secure_filename(imagen_file.filename)
        # Evitar sobrescribir archivos
        base, ext = os.path.splitext(filename)
        i = 1
        save_path = os.path.join(productos_dir, filename)
        while os.path.exists(save_path):
            filename = f"{base}_{i}{ext}"
            save_path = os.path.join(productos_dir, filename)
            i += 1
        imagen_file.save(save_path)
        imagen_url = f"/static/productos/{filename}"

    if not nombre or not precio_unitario or not cantidad_stock or not id_categoria or not estado:
        flash('Todos los campos obligatorios deben ser completados.', 'error')
        return redirect(url_for('registrar_producto'))
    from models import Producto
    nuevo_producto = Producto(
        nombre=nombre,
        descripcion_detallada=descripcion_detallada,
        precio_unitario=precio_unitario,
        cantidad_stock=cantidad_stock,
        stock_minimo=stock_minimo,
        stock_maximo=stock_maximo,
        imagen_url=imagen_url,
        id_categoria=id_categoria,
        estado=estado,
        garantia_fecha=garantia_fecha,
        unidad=unidad
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    flash('Producto registrado exitosamente.', 'success')
    return redirect(url_for('admin_productos'))



# --- EDITAR PRODUCTO (ADMIN) ---
@app.route('/admin/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    producto = Producto.query.get_or_404(producto_id)
    if request.method == 'GET':
        categorias = Categoria.query.all()
        return render_template('editar_producto.html', producto=producto, categorias=categorias)
    # POST: procesar edición
    nombre = request.form.get('nombre')
    descripcion_detallada = request.form.get('descripcion_detallada')
    precio_unitario = request.form.get('precio_unitario')
    cantidad_stock = request.form.get('cantidad_stock')
    stock_minimo = request.form.get('stock_minimo')
    stock_maximo = request.form.get('stock_maximo')
    id_categoria = request.form.get('id_categoria')
    estado = request.form.get('estado')
    garantia_fecha = request.form.get('garantia_fecha')
    unidad = request.form.get('unidad')

    # Manejo de imagen subida y eliminación opcional
    imagen_file = request.files.get('imagen')
    eliminar_imagen_flag = request.form.get('eliminar_imagen')
    import os
    from werkzeug.utils import secure_filename
    base_dir = os.path.dirname(os.path.abspath(__file__))
    productos_dir = os.path.join(base_dir, 'static', 'images', 'productos')
    if not os.path.exists(productos_dir):
        os.makedirs(productos_dir)

    # Si el admin solicita eliminar la imagen actual
    if eliminar_imagen_flag and producto.imagen_url:
        try:
            rel = producto.imagen_url.lstrip('/')
            if rel.startswith('static/'):
                rel = rel.split('static/', 1)[1]
            old_path = os.path.join(base_dir, 'static', rel)
            if os.path.isfile(old_path):
                os.remove(old_path)
        except Exception as e:
            app.logger.debug(f"No se pudo eliminar imagen anterior: {e}")
        producto.imagen_url = None

    if imagen_file and imagen_file.filename:
        # Validación básica: extensiones y tamaño
        allowed_ext = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        filename = secure_filename(imagen_file.filename)
        base, ext = os.path.splitext(filename)
        if ext.lower() not in allowed_ext:
            flash('Extensión de imagen no permitida.', 'error')
            return redirect(url_for('editar_producto', producto_id=producto_id))
        imagen_file.seek(0, os.SEEK_END)
        size = imagen_file.tell()
        imagen_file.seek(0)
        max_size = 4 * 1024 * 1024  # 4 MB
        if size > max_size:
            flash('La imagen supera el tamaño máximo permitido (4MB).', 'error')
            return redirect(url_for('editar_producto', producto_id=producto_id))

        # Guardar archivo único
        i = 1
        save_path = os.path.join(productos_dir, filename)
        while os.path.exists(save_path):
            filename = f"{base}_{i}{ext}"
            save_path = os.path.join(productos_dir, filename)
            i += 1
        imagen_file.save(save_path)
        producto.imagen_url = f"/static/images/productos/{filename}"

        # Generar miniatura con Pillow
        try:
            from PIL import Image
            thumbs_dir = os.path.join(productos_dir, 'thumbs')
            if not os.path.exists(thumbs_dir):
                os.makedirs(thumbs_dir)
            thumb_path = os.path.join(thumbs_dir, filename)
            with Image.open(save_path) as img_obj:
                img_obj.thumbnail((300, 300))
                img_obj.convert('RGB').save(thumb_path, 'JPEG', quality=85)
            # Guardar ruta relativa si se quiere usar
            producto.imagen_thumb = f"/static/images/productos/thumbs/{filename}"
        except Exception as e:
            app.logger.debug(f"Error creando miniatura: {e}")

    producto.nombre = nombre
    producto.descripcion_detallada = descripcion_detallada
    producto.precio_unitario = precio_unitario
    producto.cantidad_stock = cantidad_stock
    producto.stock_minimo = stock_minimo
    producto.stock_maximo = stock_maximo
    producto.id_categoria = id_categoria
    producto.estado = estado
    producto.garantia_fecha = garantia_fecha
    producto.unidad = unidad
    db.session.commit()
    flash('Producto actualizado correctamente.', 'success')
    return redirect(url_for('admin_productos'))


# --- ELIMINAR PRODUCTO (ADMIN) ---
@app.route('/admin/productos/eliminar', methods=['POST'])
def eliminar_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    id_producto = request.form.get('id_producto')
    if not id_producto:
        flash('ID de producto no proporcionado.', 'error')
        return redirect(url_for('admin_productos'))
    producto = Producto.query.get(int(id_producto))
    if producto:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado correctamente.', 'success')
    else:
        flash('No se encontró el producto.', 'error')
    return redirect(url_for('admin_productos'))


@app.route('/admin/productos/eliminar-imagen', methods=['POST'])
def eliminar_imagen_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('home'))
    id_producto = request.form.get('id_producto')
    if not id_producto:
        flash('ID de producto no proporcionado.', 'error')
        return redirect(url_for('admin_productos'))
    producto = Producto.query.get(int(id_producto))
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('admin_productos'))
    try:
        rel = producto.imagen_url.lstrip('/') if producto.imagen_url else ''
        if rel.startswith('static/'):
            rel = rel.split('static/', 1)[1]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, 'static', rel)
        if rel and os.path.isfile(path):
            os.remove(path)
        producto.imagen_url = None
        db.session.commit()
        flash('Imagen eliminada correctamente.', 'success')
    except Exception as e:
        app.logger.debug(f'Error eliminando imagen: {e}')
        flash('No se pudo eliminar la imagen.', 'error')
    return redirect(url_for('editar_producto', producto_id=id_producto))


@app.route('/admin/usuarios/autocomplete')
def autocomplete_admin_usuarios():
    """Endpoint AJAX que devuelve sugerencias (JSON) para autocompletar usuarios por nombre/correo."""
    if not session.get('user_rol') == 'admin':
        return jsonify([])
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        results = User.query.filter(
            (User.nombre_completo.ilike(f"%{q}%")) | (User.correo.ilike(f"%{q}%"))
        ).limit(10).all()
        suggestions = [{'id': u.id_usuario, 'nombre': u.nombre_completo, 'correo': u.correo} for u in results]
        return jsonify(suggestions)
    except Exception as e:
        app.logger.error(f"Error en autocomplete admin usuarios: {e}")
        return jsonify([])



# Permite ejecutar la aplicación directamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)







