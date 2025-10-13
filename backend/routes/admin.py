from flask import (
    Blueprint, render_template, session, redirect, url_for, request, flash, jsonify, current_app
)
import os
from datetime import datetime, timedelta
from models.models import db, Producto, Categoria, User, ContactMessage
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def admin_index():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))
    return render_template('admin.html')


@admin_bp.route('/mensajes')
def admin_mensajes():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))

    q = request.args.get('q', '').strip()
    estado = request.args.get('estado', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ContactMessage.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (ContactMessage.nombre.ilike(like)) |
            (ContactMessage.correo.ilike(like)) |
            (ContactMessage.asunto.ilike(like)) |
            (ContactMessage.mensaje.ilike(like))
        )
    if estado == 'noleidos':
        query = query.filter(ContactMessage.leido.is_(False))
    elif estado == 'leidos':
        query = query.filter(ContactMessage.leido.is_(True))

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
        query = query.filter(ContactMessage.creado_at < (dt_hasta + timedelta(days=1)))

    try:
        pagination = query.order_by(ContactMessage.creado_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        mensajes = pagination.items
        total = pagination.total
    except Exception as e:
        current_app.logger.error(f"Error al listar mensajes de contacto: {e}")
        mensajes = query.order_by(ContactMessage.creado_at.desc()).all()
        total = len(mensajes)
        pagination = None
    return render_template(
        'admin_mensajes.html', mensajes=mensajes, pagination=pagination, total=total,
        q=q, estado=estado, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, per_page=per_page
    )


@admin_bp.route('/mensajes/marcar', methods=['POST'])
def admin_mensajes_marcar():
    if not session.get('user_rol') == 'admin':
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'Acceso denegado'}), 403
        flash('Acceso denegado.', 'error')
        return redirect(url_for('admin.admin_mensajes'))

    message_id = request.form.get('id') or (request.json and request.json.get('id'))
    mark = request.form.get('mark') or (request.json and request.json.get('mark'))
    if not message_id:
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'ID faltante'}), 400
        flash('ID faltante.', 'error')
        return redirect(url_for('admin.admin_mensajes'))
    try:
        msg = ContactMessage.query.get(int(message_id))
        if not msg:
            if request.headers.get('Accept','').startswith('application/json'):
                return jsonify({'ok': False, 'error': 'Mensaje no encontrado'}), 404
            flash('Mensaje no encontrado.', 'error')
            return redirect(url_for('admin.admin_mensajes'))
        if mark == 'read':
            msg.leido = True
        elif mark == 'unread':
            msg.leido = False
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': True})
        flash('Mensaje actualizado.', 'success')
        return redirect(url_for('admin.admin_mensajes'))
    except Exception as e:
        current_app.logger.error(f"Error al marcar mensaje: {e}")
        if request.headers.get('Accept','').startswith('application/json'):
            return jsonify({'ok': False, 'error': 'Error interno'}), 500
        flash('Error interno al actualizar mensaje.', 'error')
        return redirect(url_for('admin.admin_mensajes'))


@admin_bp.route('/mensajes/<int:message_id>/json')
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


@admin_bp.route('/usuarios')
def admin_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))

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
        current_app.logger.error(f"Error al listar usuarios en admin: {e}")
        usuarios = query.order_by(User.id_usuario.asc()).all()
        total = len(usuarios)
        pagination = None

    return render_template('admin_usuario.html', usuarios=usuarios, q=q, pagination=pagination, total=total, per_page=per_page)


@admin_bp.route('/usuarios/cambiar-rol', methods=['POST'])
def cambiar_rol_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario_id = request.form.get('usuario_id')
    nuevo_rol = request.form.get('rol')
    if not usuario_id or not nuevo_rol:
        flash('Datos incompletos para cambiar el rol.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1 and usuario.rol != nuevo_rol:
        usuario.rol = nuevo_rol
        db.session.commit()
        flash(f'Rol actualizado para {usuario.nombre_completo}.', 'success')
    else:
        flash('No se pudo actualizar el rol o el usuario está protegido.', 'info')
    return redirect(url_for('admin.admin_usuario'))


@admin_bp.route('/usuarios/cambiar-estado', methods=['POST'])
def cambiar_estado_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario_id = request.form.get('usuario_id')
    nuevo_estado = request.form.get('estado')
    if not usuario_id or not nuevo_estado:
        flash('Datos incompletos para cambiar el estado.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1 and usuario.estado != nuevo_estado:
        usuario.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado actualizado para {usuario.nombre_completo}.', 'success')
    else:
        flash('No se pudo actualizar el estado o el usuario está protegido.', 'info')
    return redirect(url_for('admin.admin_usuario'))


@admin_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    if usuario_id == 1:
        flash('El usuario 1 no puede ser editado.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario = User.query.get_or_404(usuario_id)
    if request.method == 'GET':
        return render_template('editar_usuario.html', usuario=usuario)
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    identificacion = request.form.get('identificacion')
    direccion = request.form.get('direccion')
    telefono_contacto = request.form.get('telefono_contacto')
    if not nombre or not email:
        flash('Nombre y correo son obligatorios.', 'error')
        return redirect(url_for('admin.editar_usuario', usuario_id=usuario_id))
    if User.query.filter(User.correo == email, User.id_usuario != usuario_id).first():
        flash('El correo ya está registrado por otro usuario.', 'error')
        return redirect(url_for('admin.editar_usuario', usuario_id=usuario_id))
    usuario.nombre_completo = nombre
    usuario.correo = email
    usuario.identificacion = identificacion
    usuario.direccion = direccion
    usuario.telefono_contacto = telefono_contacto
    db.session.commit()
    flash('Usuario actualizado correctamente.', 'success')
    return redirect(url_for('admin.admin_usuario'))


@admin_bp.route('/usuarios/eliminar', methods=['POST'])
def eliminar_usuario():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario_id = request.form.get('usuario_id')
    if not usuario_id:
        flash('ID de usuario no proporcionado.', 'error')
        return redirect(url_for('admin.admin_usuario'))
    usuario = User.query.get(int(usuario_id))
    if usuario and usuario.id_usuario != 1:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'success')
    else:
        flash('No se puede eliminar el usuario seleccionado.', 'error')
    return redirect(url_for('admin.admin_usuario'))


@admin_bp.route('/productos')
def admin_productos():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))

    q = request.args.get('q', '').strip()
    id_categoria = request.args.get('id_categoria', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

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
        current_app.logger.error(f"Error al listar productos en admin: {e}")
        productos = query.order_by(Producto.id_producto.desc()).all()
        total = len(productos)
        pagination = None

    categorias = Categoria.query.all()

    return render_template(
        'admin_productos.html', productos=productos, q=q,
        id_categoria=id_categoria, min_price=min_price, max_price=max_price,
        pagination=pagination, total=total, categorias=categorias, per_page=per_page
    )


@admin_bp.route('/productos/autocomplete')
def autocomplete_admin_productos():
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
        current_app.logger.error(f"Error en autocomplete admin productos: {e}")
        return jsonify([])


@admin_bp.route('/productos/registrar', methods=['GET', 'POST'])
def registrar_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_productos'))
    try:
        if request.method == 'GET':
            categorias = Categoria.query.all()
            return render_template('registrar_producto.html', categorias=categorias)

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

        if garantia_fecha:
            try:
                garantia_fecha = datetime.strptime(garantia_fecha, '%Y-%m-%d').date()
            except ValueError:
                garantia_fecha = None
        else:
            garantia_fecha = None

        unidad_map = {
            'unidad': 1,
            'pieza': 1,
            'caja': 2,
            'paquete': 3,
            'set': 4,
            'kit': 5
        }
        if not unidad or unidad.strip() == '':
            unidad = 1
        elif unidad.isdigit():
            unidad = int(unidad)
        elif unidad.lower() in unidad_map:
            unidad = unidad_map[unidad.lower()]
        else:
            unidad = 1

        try:
            precio_unitario = float(precio_unitario) if precio_unitario else 0.0
            cantidad_stock = int(cantidad_stock) if cantidad_stock else 0
            stock_minimo = int(stock_minimo) if stock_minimo else 0
            stock_maximo = int(stock_maximo) if stock_maximo else 1000
            id_categoria = int(id_categoria) if id_categoria else None
        except (ValueError, TypeError):
            flash('Error en los valores numéricos. Verifica que los campos de precio y cantidades tengan valores válidos.', 'error')
            return redirect(url_for('admin.registrar_producto'))

        imagen_file = request.files.get('imagen')
        imagen_url = None
        if imagen_file and imagen_file.filename:
            from werkzeug.utils import secure_filename
            # Guardar SIEMPRE bajo el static_folder real de Flask
            productos_dir = os.path.join(current_app.static_folder, 'productos')
            if not os.path.exists(productos_dir):
                os.makedirs(productos_dir)
            filename = secure_filename(imagen_file.filename)
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
            return redirect(url_for('admin.registrar_producto'))

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
        return redirect(url_for('admin.admin_productos'))
    except Exception as e:
        flash(f'Error al registrar producto: {str(e)}', 'error')
        current_app.logger.error(f"Error en registrar_producto: {e}")
        return redirect(url_for('admin.registrar_producto'))


@admin_bp.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))
    try:
        producto = Producto.query.get_or_404(producto_id)
        if request.method == 'GET':
            categorias = Categoria.query.all()
            return render_template('editar_producto.html', producto=producto, categorias=categorias)

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

        if garantia_fecha:
            try:
                garantia_fecha = datetime.strptime(garantia_fecha, '%Y-%m-%d').date()
            except ValueError:
                garantia_fecha = None
        else:
            garantia_fecha = None

        unidad_map = {
            'unidad': 1,
            'pieza': 1,
            'caja': 2,
            'paquete': 3,
            'set': 4,
            'kit': 5
        }
        if not unidad or unidad.strip() == '':
            unidad = 1
        elif unidad.isdigit():
            unidad = int(unidad)
        elif unidad.lower() in unidad_map:
            unidad = unidad_map[unidad.lower()]
        else:
            unidad = 1

        try:
            precio_unitario = float(precio_unitario) if precio_unitario else 0.0
            cantidad_stock = int(cantidad_stock) if cantidad_stock else 0
            stock_minimo = int(stock_minimo) if stock_minimo else 0
            stock_maximo = int(stock_maximo) if stock_maximo else 1000
            id_categoria = int(id_categoria) if id_categoria else None
        except (ValueError, TypeError):
            flash('Error en los valores numéricos. Verifica que los campos de precio y cantidades tengan valores válidos.', 'error')
            return redirect(url_for('admin.editar_producto', producto_id=producto_id))

        imagen_file = request.files.get('imagen')
        eliminar_imagen_flag = request.form.get('eliminar_imagen')

        if eliminar_imagen_flag:
            producto.imagen_url = None

        if imagen_file and imagen_file.filename:
            from werkzeug.utils import secure_filename
            productos_dir = os.path.join(current_app.static_folder, 'productos')
            if not os.path.exists(productos_dir):
                os.makedirs(productos_dir)
            filename = secure_filename(imagen_file.filename)
            base, ext = os.path.splitext(filename)
            i = 1
            save_path = os.path.join(productos_dir, filename)
            while os.path.exists(save_path):
                filename = f"{base}_{i}{ext}"
                save_path = os.path.join(productos_dir, filename)
                i += 1
            imagen_file.save(save_path)
            producto.imagen_url = f"/static/productos/{filename}"

        if not nombre or not precio_unitario or not cantidad_stock or not id_categoria or not estado:
            flash('Todos los campos obligatorios deben ser completados.', 'error')
            return redirect(url_for('admin.editar_producto', producto_id=producto_id))

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
        return redirect(url_for('admin.admin_productos'))
    except Exception as e:
        flash(f'Error al editar producto: {str(e)}', 'error')
        current_app.logger.error(f"Error en editar_producto: {e}")
        return redirect(url_for('admin.admin_productos'))


@admin_bp.route('/productos/eliminar', methods=['POST'])
def eliminar_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_productos'))
    id_producto = request.form.get('id_producto')
    if not id_producto:
        flash('ID de producto no proporcionado.', 'error')
        return redirect(url_for('admin.admin_productos'))
    producto = Producto.query.get(int(id_producto))
    if producto:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado correctamente.', 'success')
    else:
        flash('No se encontró el producto.', 'error')
    return redirect(url_for('admin.admin_productos'))


@admin_bp.route('/productos/eliminar-imagen', methods=['POST'])
def eliminar_imagen_producto():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('admin.admin_productos'))
    id_producto = request.form.get('id_producto')
    if not id_producto:
        flash('ID de producto no proporcionado.', 'error')
        return redirect(url_for('admin.admin_productos'))
    producto = Producto.query.get(int(id_producto))
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('admin.admin_productos'))
    try:
        rel = producto.imagen_url.lstrip('/') if producto.imagen_url else ''
        if rel.startswith('static/'):
            rel = rel.split('static/', 1)[1]
        # Usar el static_folder real configurado en la app
        path = os.path.join(current_app.static_folder, rel)
        if rel and os.path.isfile(path):
            os.remove(path)
        producto.imagen_url = None
        db.session.commit()
        flash('Imagen eliminada correctamente.', 'success')
    except Exception as e:
        current_app.logger.debug(f'Error eliminando imagen: {e}')
        flash('No se pudo eliminar la imagen.', 'error')
    return redirect(url_for('admin.editar_producto', producto_id=id_producto))


@admin_bp.route('/usuarios/autocomplete')
def autocomplete_admin_usuarios():
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
        current_app.logger.error(f"Error en autocomplete admin usuarios: {e}")
        return jsonify([])
