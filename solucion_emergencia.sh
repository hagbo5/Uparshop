#!/bin/bash
# Script de solución rápida para el error 500
# Ejecutar en tu servidor DigitalOcean

echo "🚨 SOLUCIÓN DE EMERGENCIA PARA ERROR 500"
echo "========================================"

echo "1️⃣ Haciendo backup del models.py actual..."
cp models.py models_with_enum_backup.py

echo "2️⃣ Reemplazando con versión segura..."
cp models_safe.py models.py

echo "3️⃣ Ejecutando diagnóstico..."
python diagnostico_servidor.py

echo "4️⃣ Reiniciando aplicación..."
# Descomenta la línea que corresponda a tu setup:
# sudo systemctl restart your-app-name
# pm2 restart your-app
# sudo systemctl restart nginx
# sudo systemctl restart apache2

echo "✅ Solución aplicada. Prueba tu aplicación ahora."
echo "💡 Si funciona, los ENUMs eran el problema."