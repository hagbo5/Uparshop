from flask_sqlalchemy import SQLAlchemy
import datetime

# Instancia de la BD. Se inicializa con db.init_app(app) desde app.py
db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='activo')

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    descripcion_detallada = db.Column(db.Text)
    precio_unitario = db.Column(db.Numeric(10, 2))
    cantidad_stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    stock_maximo = db.Column(db.Integer, default=0)
    imagen_url = db.Column(db.String(255))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    estado = db.Column(db.String(20), default='activo')
    garantia_fecha = db.Column(db.Date)
    unidad = db.Column(db.String(50), default='unidad')
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

    @property
    def web_imagen_url(self) -> str:
        """Devuelve una URL web segura para mostrar la imagen del producto.
        - Si imagen_url es absoluta (http/https) o empieza con '/', se retorna tal cual.
        - Si es un nombre de archivo simple, se sirve desde /static/productos/<archivo>.
        - Si no hay imagen, retorna el placeholder por defecto.
        """
        u = (self.imagen_url or '').strip()
        if not u:
            return '/static/images/product-placeholder.svg'
        low = u.lower()
        if low.startswith('http://') or low.startswith('https://') or u.startswith('/'):
            return u
        return f"/static/productos/{u}"


class User(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255))
    correo = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    contrasena = db.Column(db.String(255))
    rol = db.Column(db.String(50), default='cliente')
    estado = db.Column(db.String(20), default='activo')

    def __repr__(self):
        return f"<User {self.correo}>"
    
    # Propiedades para mantener compatibilidad
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
        return None
    
    @identificacion.setter
    def identificacion(self, value):
        pass


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    correo = db.Column(db.String(255))
    asunto = db.Column(db.String(255))
    mensaje = db.Column(db.Text)
    creado_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ContactMessage {self.id} {self.correo}>"