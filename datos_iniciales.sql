-- Script para poblar la base de datos Uparshop con datos iniciales

-- Insertar categorías
INSERT INTO categorias (nombre, descripcion, estado) VALUES
('Torres', 'Computadoras de escritorio completas', 'activo'),
('Laptops', 'Computadoras portátiles y ultrabooks', 'activo'),
('Procesadores', 'CPUs Intel y AMD', 'activo'),
('Tarjetas Gráficas', 'GPUs para gaming y trabajo profesional', 'activo'),
('Periféricos', 'Teclados, ratones, monitores y más', 'activo'),
('Memorias', 'RAM DDR4 y DDR5', 'activo'),
('Fuentes', 'Fuentes de poder certificadas', 'activo'),
('Juegos', 'Videojuegos para PC', 'activo');

-- Insertar productos de ejemplo
INSERT INTO productos (nombre, descripcion_detallada, precio_unitario, cantidad_stock, stock_minimo, stock_maximo, imagen_url, id_categoria, estado, garantia_fecha, unidad) VALUES
('PC Gamer RTX 4060', 'PC completa para gaming con RTX 4060, Intel i5-12400F, 16GB RAM, SSD 500GB', 2500000.00, 5, 1, 20, '/static/productos/pc_gamer.jpg', 1, 'activo', '2025-12-30', 'unidad'),
('Laptop Lenovo ThinkPad', 'Laptop empresarial Intel i7, 16GB RAM, SSD 512GB', 3200000.00, 3, 1, 15, '/static/productos/laptop_lenovo.jpg', 2, 'activo', '2025-12-30', 'unidad'),
('Procesador Intel i7-13700K', 'CPU de alto rendimiento para gaming y trabajo', 1800000.00, 8, 2, 25, '/static/productos/intel_i7.jpg', 3, 'activo', '2025-12-30', 'unidad'),
('RTX 4070 Super', 'Tarjeta gráfica para gaming 4K y ray tracing', 2800000.00, 4, 1, 12, '/static/productos/rtx_4070.jpg', 4, 'activo', '2025-12-30', 'unidad'),
('Teclado Mecánico RGB', 'Teclado gaming con switches Cherry MX', 450000.00, 15, 5, 50, '/static/productos/teclado_rgb.jpg', 5, 'activo', '2025-12-30', 'unidad'),
('RAM 32GB DDR4', 'Kit de memoria RAM 32GB 3200MHz', 850000.00, 10, 3, 30, '/static/productos/ram_32gb.jpg', 6, 'activo', '2025-12-30', 'unidad'),
('Fuente 850W 80+ Gold', 'Fuente modular certificada 80+ Gold', 650000.00, 6, 2, 20, '/static/productos/fuente_850w.jpg', 7, 'activo', '2025-12-30', 'unidad'),
('Cyberpunk 2077', 'Juego de rol futurista para PC', 180000.00, 20, 5, 100, '/static/productos/cyberpunk.jpg', 8, 'activo', '2025-12-30', 'unidad');

-- Insertar algunos mensajes de contacto de ejemplo
INSERT INTO contact_messages (nombre, correo, asunto, mensaje, fecha_envio, leido) VALUES
('Juan Pérez', 'juan@email.com', 'Consulta sobre PCs gaming', 'Hola, me interesa una PC para gaming. ¿Tienen stock?', NOW(), false),
('María García', 'maria@email.com', 'Garantía de laptop', 'Mi laptop tiene un problema, ¿cómo puedo hacer válida la garantía?', NOW(), false);