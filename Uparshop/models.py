from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Instancia de la BD. Se inicializa con db.init_app(app) desde app.py
db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)  # Agregado nullable=False y unique
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Enum('activo', 'inactivo'), nullable=False, default='activo')  # Corregido: ahora es ENUM

    def __repr__(self):
        return f"<Categoria {self.nombre}>"



class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)  # Agregado nullable=False
    descripcion_detallada = db.Column(db.Text, nullable=False)  # Agregado nullable=False
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)  # Agregado nullable=False
    cantidad_stock = db.Column(db.Integer, nullable=False, default=0)  # Agregado nullable=False y default
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)  # Agregado nullable=False y default
    stock_maximo = db.Column(db.Integer, nullable=False, default=0)  # Agregado nullable=False y default
    imagen_url = db.Column(db.String(255))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    estado = db.Column(db.Enum('activo', 'inactivo', 'promocion'), nullable=False, default='activo')  # Corregido: ahora es ENUM
    garantia_fecha = db.Column(db.Date)
    unidad = db.Column(db.Integer)  # Corregido: era String(50), ahora es Integer según tu BD
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
    correo = db.Column(db.String(100), unique=True, nullable=False)  # Corregido: era correo_electronico
    telefono = db.Column(db.String(20))  # Agregado: campo faltante
    direccion = db.Column(db.String(255))  # Agregado: campo faltante
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'vendedor', 'cliente'), default='cliente')  # Corregido: ahora es ENUM
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')  # Corregido: ahora es ENUM

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
