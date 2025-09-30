from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Instancia de la BD. Se inicializa con db.init_app(app) desde app.py
db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='activo')  # Volvemos a String temporalmente

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion_detallada = db.Column(db.Text, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad_stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    stock_maximo = db.Column(db.Integer, nullable=False, default=0)
    imagen_url = db.Column(db.String(255))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    estado = db.Column(db.String(20), nullable=False, default='activo')  # Volvemos a String temporalmente
    garantia_fecha = db.Column(db.Date)
    unidad = db.Column(db.Integer)  # Mantenemos Integer
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
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='cliente')  # Volvemos a String temporalmente
    estado = db.Column(db.String(20), default='activo')  # Volvemos a String temporalmente

    def __repr__(self):
        return f"<User {self.correo}>"
    
    # Propiedades para mantener compatibilidad con código existente
    @property
    def correo_electronico(self):
        return self.correo
    
    @correo_electronico.setter
    def correo_electronico(self, value):
        self.correo = value

    @property
    def telefono_contacto(self):
        return self.telefono
    
    @telefono_contacto.setter
    def telefono_contacto(self, value):
        self.telefono = value

    @property
    def identificacion(self):
        # Campo para compatibilidad - podrías agregar este campo a la BD si lo necesitas
        return None
    
    @identificacion.setter
    def identificacion(self, value):
        # No hacer nada por ahora
        pass


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