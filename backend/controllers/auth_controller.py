from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        flash('Correo y contraseña son requeridos.', 'error')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(correo=email).first()
    if user:
        if user.estado != 'activo':
            flash('Tu cuenta se encuentra inactiva. Por favor comunícate con soporte técnico.', 'error')
            return redirect(url_for('auth.login'))
        if user.contrasena == password:
            session['user_id'] = user.id_usuario
            session['user_email'] = user.correo
            session['user_rol'] = user.rol
            flash('Sesión iniciada.', 'success')
            return redirect(url_for('main.home'))
    flash('Credenciales inválidas.', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_rol', None)
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/crear-cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'GET':
        return render_template('crear_cuenta.html')
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if not nombre or not email or not password or not password2:
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('auth.crear_cuenta'))
    if password != password2:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('auth.crear_cuenta'))
    if User.query.filter_by(correo=email).first():
        flash('El correo ya está registrado.', 'error')
        return redirect(url_for('auth.crear_cuenta'))
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
    return redirect(url_for('auth.login'))
