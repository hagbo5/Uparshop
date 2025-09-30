from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Instancia de la BD. Se inicializa con db.init_app(app) desde app.py
db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20))

    def __repr__(self):
        return f"<Categoria {self.nombre}>"



class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    descripcion_detallada = db.Column(db.Text)
    precio_unitario = db.Column(db.Numeric(10, 2))
    cantidad_stock = db.Column(db.Integer)
    stock_minimo = db.Column(db.Integer)
    stock_maximo = db.Column(db.Integer)
    imagen_url = db.Column(db.String(255))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    estado = db.Column(db.String(20))
    garantia_fecha = db.Column(db.Date)
    unidad = db.Column(db.String(50))
    categoria = db.relationship('Categoria', backref='productos')

    def __repr__(self):
        return f"<Producto {self.nombre}>"

    # Compatibilidad con plantillas existentes
    @property
    def imagen(self):
        return self.imagen_url or ''

    @property
    def descripcion(self):
        return self.descripcion_detallada or ''


class User(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # Cambiado aquí
    rol = db.Column(db.String(50), default='cliente')
    estado = db.Column(db.String(20), default='activo')

    def __repr__(self):
        return f"<User {self.correo}>"


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False)
    asunto = db.Column(db.String(255))
    mensaje = db.Column(db.Text, nullable=False)
    creado_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ContactMessage {self.id} {self.correo}>"
