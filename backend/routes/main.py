from flask import Blueprint, render_template, request, current_app, redirect, url_for, session, flash
from models.models import Producto, Categoria, ContactMessage, db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    try:
        productos_destacados = Producto.query.order_by(Producto.id_producto.desc()).limit(8).all()
        return render_template('index.html', productos_destacados=productos_destacados)
    except Exception as e:
        current_app.logger.error(f"Error en home: {e}")
        return render_template('index.html', productos_destacados=[])


@main_bp.route('/lista-precios')
def lista_precios():
    return render_template('lista_precios.html')


@main_bp.route('/sobre-nosotros')
def sobre_nosotros():
    return render_template('sobre_nosotros.html')


def _get_products_by_category_name(category_name):
    try:
        cat = Categoria.query.filter(Categoria.nombre.ilike(f"%{category_name}%")).first()
        if not cat:
            return []
        return Producto.query.filter_by(id_categoria=cat.id_categoria).all()
    except Exception as e:
        current_app.logger.error(f"Error consultando productos por categoría '{category_name}': {e}")
        return []


@main_bp.route('/torres')
def torres():
    try:
        desktops = _get_products_by_category_name('Torres')
        return render_template('torres.html', desktops=desktops)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /torres: {e}")
        return render_template('torres.html', desktops=[])


@main_bp.route('/laptops')
def laptops():
    try:
        laptops = _get_products_by_category_name('Laptops')
        return render_template('laptops.html', laptops=laptops)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /laptops: {e}")
        return render_template('laptops.html', laptops=[])


@main_bp.route('/procesadores')
def procesadores():
    try:
        productos = _get_products_by_category_name('Procesadores')
        return render_template('procesadores.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /procesadores: {e}")
        return render_template('procesadores.html', productos=[])


@main_bp.route('/tarjetas-graficas')
def tarjetas_graficas():
    try:
        productos = _get_products_by_category_name('Tarjetas Gráficas')
        if not productos:
            productos = _get_products_by_category_name('Tarjetas Graficas')
        return render_template('tarjetas_graficas.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /tarjetas-graficas: {e}")
        return render_template('tarjetas_graficas.html', productos=[])


@main_bp.route('/perifericos')
def perifericos():
    try:
        productos = _get_products_by_category_name('Periféricos')
        if not productos:
            productos = _get_products_by_category_name('Perifericos')
        return render_template('perifericos.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /perifericos: {e}")
        return render_template('perifericos.html', productos=[])


@main_bp.route('/memorias')
def memorias():
    try:
        productos = _get_products_by_category_name('Memorias')
        return render_template('memorias.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /memorias: {e}")
        return render_template('memorias.html', productos=[])


@main_bp.route('/fuentes')
def fuentes():
    try:
        productos = _get_products_by_category_name('Fuentes')
        return render_template('fuentes.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /fuentes: {e}")
        return render_template('fuentes.html', productos=[])


@main_bp.route('/juegos')
def juegos():
    try:
        productos = _get_products_by_category_name('Juegos')
        return render_template('juegos.html', productos=productos)
    except Exception as e:
        current_app.logger.error(f"Error en ruta /juegos: {e}")
        return render_template('juegos.html', productos=[])


@main_bp.route('/test-simple')
def test_simple():
    return "✅ Aplicación funcionando correctamente - Sin consultas a BD"


@main_bp.route('/test-home')
def test_home():
    try:
        productos_destacados = Producto.query.order_by(Producto.id_producto.desc()).limit(8).all()
        return f"✅ Consulta exitosa - Encontrados {len(productos_destacados)} productos destacados"
    except Exception as e:
        return f"❌ Error en consulta: {e}"


@main_bp.route('/debug-categorias')
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


@main_bp.route('/init-data')
def init_data():
    try:
        if Categoria.query.count() > 0:
            return "❌ La base de datos ya tiene categorías. No se insertan datos para evitar duplicados."
        categorias = [
            Categoria(nombre='Torres', descripcion='Computadoras de escritorio completas', estado='activo'),
            Categoria(nombre='Laptops', descripcion='Computadoras portátiles y ultrabooks', estado='activo'),
            Categoria(nombre='Procesadores', descripcion='CPUs Intel y AMD', estado='activo'),
            Categoria(nombre='Tarjetas Gráficas', descripcion='GPUs para gaming y trabajo profesional', estado='activo'),
            Categoria(nombre='Periféricos', descripcion='Teclados, ratones, monitores y más', estado='activo'),
            Categoria(nombre='Memorias', descripcion='RAM DDR4 y DDR5', estado='activo'),
            Categoria(nombre='Fuentes', descripcion='Fuentes de poder certificadas', estado='activo'),
            Categoria(nombre='Juegos', descripcion='Videojuegos para PC', estado='activo')
        ]
        for cat in categorias:
            db.session.add(cat)
        db.session.commit()
        productos = [
            Producto(nombre='PC Gamer RTX 4060', descripcion_detallada='PC completa para gaming con RTX 4060, Intel i5-12400F, 16GB RAM, SSD 500GB', precio_unitario=2500000.00, cantidad_stock=5, stock_minimo=1, stock_maximo=20, imagen_url='/static/productos/pc_gamer.jpg', id_categoria=1, estado='activo'),
            Producto(nombre='Laptop Lenovo ThinkPad', descripcion_detallada='Laptop empresarial Intel i7, 16GB RAM, SSD 512GB', precio_unitario=3200000.00, cantidad_stock=3, stock_minimo=1, stock_maximo=15, imagen_url='/static/productos/laptop_lenovo.jpg', id_categoria=2, estado='activo'),
            Producto(nombre='Procesador Intel i7-13700K', descripcion_detallada='CPU de alto rendimiento para gaming y trabajo', precio_unitario=1800000.00, cantidad_stock=8, stock_minimo=2, stock_maximo=25, imagen_url='/static/productos/intel_i7.jpg', id_categoria=3, estado='activo'),
            Producto(nombre='RTX 4070 Super', descripcion_detallada='Tarjeta gráfica para gaming 4K y ray tracing', precio_unitario=2800000.00, cantidad_stock=4, stock_minimo=1, stock_maximo=12, imagen_url='/static/productos/rtx_4070.jpg', id_categoria=4, estado='activo'),
            Producto(nombre='Teclado Mecánico RGB', descripcion_detallada='Teclado gaming con switches Cherry MX', precio_unitario=450000.00, cantidad_stock=15, stock_minimo=5, stock_maximo=50, imagen_url='/static/productos/teclado_rgb.jpg', id_categoria=5, estado='activo'),
            Producto(nombre='RAM 32GB DDR4', descripcion_detallada='Kit de memoria RAM 32GB 3200MHz', precio_unitario=850000.00, cantidad_stock=10, stock_minimo=3, stock_maximo=30, imagen_url='/static/productos/ram_32gb.jpg', id_categoria=6, estado='activo'),
            Producto(nombre='Fuente 850W 80+ Gold', descripcion_detallada='Fuente modular certificada 80+ Gold', precio_unitario=650000.00, cantidad_stock=6, stock_minimo=2, stock_maximo=20, imagen_url='/static/productos/fuente_850w.jpg', id_categoria=7, estado='activo'),
            Producto(nombre='Cyberpunk 2077', descripcion_detallada='Juego de rol futurista para PC', precio_unitario=180000.00, cantidad_stock=20, stock_minimo=5, stock_maximo=100, imagen_url='/static/productos/cyberpunk.jpg', id_categoria=8, estado='activo')
        ]
        for prod in productos:
            db.session.add(prod)
        db.session.commit()
        return f"✅ Datos iniciales insertados correctamente:<br>- {len(categorias)} categorías<br>- {len(productos)} productos<br><br><a href='/'>Ver tienda</a> | <a href='/test-db'>Verificar BD</a>"
    except Exception as e:
        return f"❌ Error al insertar datos: {e}"


# --- Búsqueda pública ---
@main_bp.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    productos = []
    try:
        if q:
            like = f"%{q}%"
            productos = Producto.query.filter(
                (Producto.nombre.ilike(like)) | (Producto.descripcion_detallada.ilike(like))
            ).all()
    except Exception as e:
        current_app.logger.error(f"Error en buscar: {e}")
        productos = []
    return render_template('search_results.html', productos=productos, q=q)


# --- Detalle de producto ---
@main_bp.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    try:
        producto = Producto.query.get_or_404(producto_id)
        return render_template('product_detail.html', producto=producto)
    except Exception as e:
        current_app.logger.error(f"Error en producto_detalle {producto_id}: {e}")
        flash('No se encontró el producto.', 'error')
        return redirect(url_for('main.home'))


# --- Carrito mínimo en sesión ---
@main_bp.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', {})
    items = []
    total = 0.0
    try:
        for pid, qty in carrito.items():
            p = Producto.query.get(int(pid))
            if p:
                subtotal = (p.precio_unitario or 0) * int(qty)
                items.append({'producto': p, 'cantidad': int(qty), 'subtotal': subtotal})
                total += subtotal
    except Exception as e:
        current_app.logger.error(f"Error calculando carrito: {e}")
    return render_template('carrito.html', items=items, total=total)


@main_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    carrito = session.get('carrito', {})
    qty = int(request.form.get('cantidad', 1)) if request.form.get('cantidad') else 1
    carrito[str(producto_id)] = carrito.get(str(producto_id), 0) + int(qty)
    session['carrito'] = carrito
    # redirigir de vuelta al detalle con animación en la ui
    return redirect(url_for('main.producto_detalle', producto_id=producto_id) + '?carrito_anim=1')


@main_bp.route('/carrito/actualizar', methods=['POST'])
def actualizar_carrito():
    carrito = session.get('carrito', {})
    try:
        # esperar campos como quantity_<producto_id>
        for key, val in request.form.items():
            if key.startswith('quantity_'):
                pid = key.split('quantity_')[1]
                try:
                    qty = int(val)
                    if qty <= 0:
                        carrito.pop(pid, None)
                    else:
                        carrito[pid] = qty
                except Exception:
                    pass
        session['carrito'] = carrito
    except Exception as e:
        current_app.logger.error(f"Error actualizando carrito: {e}")
    return redirect(url_for('main.ver_carrito'))


# --- Contacto (GET muestra formulario, POST guarda mensaje) ---
@main_bp.route('/contactanos', methods=['GET', 'POST'])
def contactanos():
    if request.method == 'GET':
        return render_template('contactanos.html')
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    asunto = request.form.get('asunto')
    mensaje = request.form.get('mensaje')
    if not nombre or not correo or not asunto or not mensaje:
        flash('Todos los campos son obligatorios para enviar el mensaje.', 'error')
        return redirect(url_for('main.contactanos'))
    try:
        cm = ContactMessage(nombre=nombre, correo=correo, asunto=asunto, mensaje=mensaje, leido=False)
        db.session.add(cm)
        db.session.commit()
        flash('Mensaje enviado. Gracias por contactarnos.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error guardando mensaje de contacto: {e}")
        flash('No se pudo enviar el mensaje. Intente más tarde.', 'error')
    return redirect(url_for('main.home'))
