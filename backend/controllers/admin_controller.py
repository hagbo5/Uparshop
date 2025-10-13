from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def admin_index():
    if not session.get('user_rol') == 'admin':
        flash('Acceso restringido solo para administradores.', 'error')
        return redirect(url_for('main.home'))
    return render_template('admin.html')
