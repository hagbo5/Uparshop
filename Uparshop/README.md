# Uparshop - E-commerce Platform

Sistema de comercio electrónico especializado en productos tecnológicos (computadoras, componentes, periféricos y juegos) construido con Flask.

## 🚀 Características

### Funcionalidades Principales
- **Catálogo de Productos**: Navegación por categorías (Torres, Laptops, Procesadores, Tarjetas Gráficas, Periféricos, Memorias, Fuentes, Juegos)
- **Sistema de Usuarios**: Registro, login, roles (admin/cliente)
- **Carrito de Compras**: Agregar productos, actualizar cantidades, eliminar items
- **Búsqueda Avanzada**: Búsqueda por nombre y descripción de productos
- **Panel de Administración**: Gestión completa de productos y usuarios

### Sistema de Mensajes de Contacto
- **Formulario de Contacto**: Los usuarios pueden enviar consultas y mensajes
- **Panel Admin Avanzado**: 
  - Vista modal para leer mensajes completos
  - Filtros server-side (búsqueda, estado, rango de fechas)
  - Filtros client-side (búsqueda rápida, solo no leídos, vista compacta)
  - Acciones masivas (marcar todos los visibles como leídos)
  - Exportación CSV de mensajes filtrados
  - Sistema de notificaciones con badges dinámicos
  - Marcado AJAX sin recarga de página

## 🛠️ Tecnologías

- **Backend**: Flask, SQLAlchemy, PyMySQL
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Base de Datos**: MySQL
- **Autenticación**: Werkzeug Security
- **Gestión de Variables**: python-dotenv
- **Procesamiento de Imágenes**: Pillow

## 📋 Requisitos

- Python 3.8+
- MySQL Server
- Dependencias en `requirements.txt`

## ⚡ Instalación Rápida

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd Uparshop
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**:
   - Crear base de datos MySQL llamada `uparshop_bd`
   - Configurar credenciales en `.env` (opcional):
   ```env
   DB_USER=root
   DB_PASS=tu_password
   DB_HOST=localhost
   DB_NAME=uparshop_bd
   SECRET_KEY=tu_clave_secreta
   ```

5. **Ejecutar aplicación**:
   ```bash
   python app.py
   ```

6. **Acceder**:
   - Aplicación: http://localhost:5000
   - Panel Admin: http://localhost:5000/admin (requiere login como admin)

## 🗂️ Estructura del Proyecto

```
Uparshop/
├── app.py                  # Aplicación principal Flask
├── models.py              # Modelos SQLAlchemy (Producto, User, ContactMessage, etc.)
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── static/
│   ├── style.css         # Estilos centralizados
│   └── images/
│       └── Uparshop-logo.png
└── templates/
    ├── base.html         # Template base
    ├── base_admin.html   # Base para panel admin
    ├── index.html        # Página principal
    ├── admin_mensajes.html  # Panel mensajes (avanzado)
    ├── carrito.html      # Carrito de compras
    ├── contactanos.html  # Formulario contacto
    ├── search_results.html  # Resultados búsqueda
    └── [categoría].html  # Templates por categoría
```

## 🎯 Rutas Principales

### Públicas
- `/` - Página principal
- `/laptops`, `/torres`, `/procesadores`, etc. - Páginas de categorías
- `/buscar` - Búsqueda de productos
- `/carrito` - Ver carrito de compras
- `/contactanos` - Formulario de contacto

### Administración
- `/admin` - Panel principal admin
- `/admin/mensajes` - Gestión mensajes de contacto
- `/admin/productos` - Gestión de productos
- `/admin/usuarios` - Gestión de usuarios

### API
- `/admin/mensajes/<id>/json` - Detalles de mensaje (JSON)
- `/admin/mensajes/marcar` - Marcar leído/no leído (AJAX)

## 🔧 Características Técnicas

### Base de Datos
- **Productos**: Catálogo con categorías, precios, stock, imágenes
- **Usuarios**: Sistema de roles, autenticación segura
- **Mensajes**: Sistema completo de contacto con timestamps
- **Auto-creación**: Las tablas se crean automáticamente si no existen

### Funcionalidades Avanzadas
- **Paginación**: Para listas grandes de mensajes
- **Filtrado Híbrido**: Server-side + client-side para mejor UX
- **AJAX Progresivo**: Con fallback HTML para compatibilidad
- **Responsive**: Diseño adaptable a móviles y tablets
- **Accesibilidad**: Focus trap en modales, ARIA labels

### Seguridad
- Hashing de contraseñas con Werkzeug
- Validación de sesiones para rutas admin
- Sanitización de inputs en filtros
- Protección contra inyecciones SQL via SQLAlchemy

## 📈 Mejoras Futuras

- [ ] Sistema de pedidos completo
- [ ] Integración de pagos
- [ ] Panel de reportes y analytics
- [ ] Notificaciones push
- [ ] API REST completa
- [ ] Sistema de inventario avanzado
- [ ] Multi-idioma
- [ ] Integración con CRM

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es de uso educativo/personal. Consulta con el autor para uso comercial.

## 👨‍💻 Desarrollo

Desarrollado como sistema de gestión e-commerce con enfoque en experiencia de usuario y panel administrativo robusto.

**Última actualización**: Septiembre 2025
**Versión**: 1.0.0

---

Para soporte técnico o consultas, utiliza el formulario de contacto en la aplicación.