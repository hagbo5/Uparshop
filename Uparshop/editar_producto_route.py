from flask import render_template, request, redirect, url_for, flash, session
from Uparshop.models import db, Producto, Categoria
from flask import current_app as app  # Import the app instance

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

    # Manejo de imagen subida
    imagen_file = request.files.get('imagen')
    if imagen_file and imagen_file.filename:
        import os
        from werkzeug.utils import secure_filename
        base_dir = os.path.dirname(os.path.abspath(__file__))
        productos_dir = os.path.join(base_dir, 'static', 'productos')
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

