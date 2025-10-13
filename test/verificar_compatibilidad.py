#!/usr/bin/env python3
"""
Script para verificar que los modelos coinciden con la base de datos de DigitalOcean
Ejecutar: python verificar_compatibilidad.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.models import db, User, Producto, Categoria, ContactMessage
from sqlalchemy import text, inspect
import traceback

def create_app():
    """Crear aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    # Usar la misma configuración de BD que tu app
    DB_USER = os.getenv('DB_USER', 'doadmin')
    DB_PASS = os.getenv('DB_PASS', 'AVNS_vpW0rR3lfKCIZfRnYqt')
    DB_HOST = os.getenv('DB_HOST', 'uparshop-bd-do-user-26734553-0.k.db.ondigitalocean.com')
    DB_PORT = os.getenv('DB_PORT', '25060')
    DB_NAME = os.getenv('DB_NAME', 'uparshop_bd')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "ssl": {"ssl_mode": "REQUIRED"}
        }
    }
    
    db.init_app(app)
    return app

def test_connection(app):
    """Test básico de conexión"""
    print("🔍 Probando conexión a DigitalOcean...")
    try:
        with app.app_context():
            result = db.session.execute(text('SELECT 1')).scalar()
            if result == 1:
                print("✅ Conexión exitosa a DigitalOcean MySQL")
                return True
            else:
                print("❌ Conexión establecida pero query falló")
                return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_tables_exist(app):
    """Verificar que las tablas existen"""
    print("\n🔍 Verificando tablas en DigitalOcean...")
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['categorias', 'productos', 'usuarios']
            optional_tables = ['contact_messages']
            
            missing_required = []
            missing_optional = []
            
            for table in required_tables:
                if table in tables:
                    print(f"✅ Tabla '{table}' existe")
                else:
                    print(f"❌ Tabla '{table}' NO existe")
                    missing_required.append(table)
            
            for table in optional_tables:
                if table in tables:
                    print(f"✅ Tabla opcional '{table}' existe")
                else:
                    print(f"⚠️ Tabla opcional '{table}' NO existe")
                    missing_optional.append(table)
            
            if missing_required:
                print(f"\n❌ CRÍTICO: Faltan tablas requeridas: {missing_required}")
                return False
            elif missing_optional:
                print(f"\n⚠️ Faltan tablas opcionales: {missing_optional}")
                print("💡 Ejecuta 'agregar_contact_messages.sql' para agregar la tabla faltante")
                return True
            else:
                print("\n✅ Todas las tablas están presentes")
                return True
                
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def test_models(app):
    """Verificar que los modelos funcionan"""
    print("\n🔍 Probando modelos...")
    try:
        with app.app_context():
            # Test modelo User
            user_count = User.query.count()
            print(f"✅ Usuarios en BD: {user_count}")
            
            # Test modelo Categoria
            cat_count = Categoria.query.count()
            print(f"✅ Categorías en BD: {cat_count}")
            
            # Test modelo Producto
            prod_count = Producto.query.count()
            print(f"✅ Productos en BD: {prod_count}")
            
            # Test modelo ContactMessage (puede fallar si la tabla no existe)
            try:
                msg_count = ContactMessage.query.count()
                print(f"✅ Mensajes de contacto en BD: {msg_count}")
            except Exception as e:
                print(f"⚠️ ContactMessage falló (tabla no existe): {str(e)[:50]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        traceback.print_exc()
        return False

def test_model_compatibility(app):
    """Verificar compatibilidad específica de campos"""
    print("\n🔍 Verificando compatibilidad de campos...")
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # Verificar tabla usuarios
            if 'usuarios' in inspector.get_table_names():
                columns = inspector.get_columns('usuarios')
                column_names = [col['name'] for col in columns]
                
                print("📋 Campos en tabla 'usuarios':")
                for col in columns:
                    print(f"   {col['name']}: {col['type']}")
                
                # Verificar campos críticos
                if 'correo' in column_names:
                    print("✅ Campo 'correo' encontrado (correcto)")
                elif 'correo_electronico' in column_names:
                    print("❌ PROBLEMA: Campo 'correo_electronico' encontrado, pero modelo usa 'correo'")
                    return False
                
                if 'telefono' in column_names:
                    print("✅ Campo 'telefono' encontrado")
                else:
                    print("⚠️ Campo 'telefono' no encontrado (agregado en modelo)")
                    
                if 'direccion' in column_names:
                    print("✅ Campo 'direccion' encontrado")
                else:
                    print("⚠️ Campo 'direccion' no encontrado (agregado en modelo)")
            
            # Verificar tabla productos
            if 'productos' in inspector.get_table_names():
                columns = inspector.get_columns('productos')
                print("\n📋 Campos en tabla 'productos':")
                for col in columns:
                    print(f"   {col['name']}: {col['type']}")
                    
                    # Verificar campo unidad específicamente
                    if col['name'] == 'unidad':
                        if 'INT' in str(col['type']).upper():
                            print("✅ Campo 'unidad' es INTEGER (correcto)")
                        else:
                            print(f"⚠️ Campo 'unidad' es {col['type']} (modelo espera INTEGER)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verificando compatibilidad: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN DE COMPATIBILIDAD UPARSHOP - DIGITALOCEAN")
    print("=" * 60)
    
    app = create_app()
    
    tests = [
        ("Conexión a BD", test_connection),
        ("Existencia de tablas", test_tables_exist),
        ("Funcionamiento de modelos", test_models),
        ("Compatibilidad de campos", test_model_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func(app)
        results.append((test_name, result))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Tu aplicación debería funcionar correctamente con DigitalOcean")
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("📝 Acciones recomendadas:")
        print("   1. Si falta 'contact_messages': ejecuta agregar_contact_messages.sql")
        print("   2. Si hay problemas de campos: verifica el esquema de BD")
        print("   3. Si hay errores de conexión: verifica credenciales")
    
    print("\n🔧 Archivos disponibles:")
    print("   - agregar_contact_messages.sql (para tabla faltante)")
    print("   - models.py (ya actualizado)")
    print("   - app.py (ya actualizado)")

if __name__ == "__main__":
    main()