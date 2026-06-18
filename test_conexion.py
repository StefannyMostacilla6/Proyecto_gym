# test_conexion.py
import sys
import os

# Agregar la ruta del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.conexion import conectar

def test_conexion():
    print("=" * 50)
    print("🔍 PROBANDO CONEXIÓN A PostgreSQL")
    print("=" * 50)
    
    try:
        # Intentar conectar
        print("📡 Conectando a la base de datos...")
        conexion = conectar()
        print("✅ ¡Conexión exitosa!")
        
        # Crear cursor
        cursor = conexion.cursor()
        
        # 1. Probar versión de PostgreSQL
        print("\n📊 Información de la base de datos:")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   PostgreSQL: {version[0][:50]}...")
        
        # 2. Mostrar tablas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tablas = cursor.fetchall()
        if tablas:
            print(f"\n📋 Tablas encontradas ({len(tablas)}):")
            for tabla in tablas:
                print(f"   ✅ {tabla[0]}")
        else:
            print("\n⚠️ No hay tablas en la base de datos")
            
        # 3. Contar registros en algunas tablas
        print("\n📈 Estadísticas:")
        tablas_importantes = ['miembros', 'usuarios', 'membresias', 'clases', 'entrenadores']
        for tabla in tablas_importantes:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
                count = cursor.fetchone()[0]
                print(f"   {tabla}: {count} registros")
            except:
                print(f"   {tabla}: No existe o no accesible")
        
        # 4. Probar consulta con fecha
        cursor.execute("SELECT CURRENT_DATE as fecha_actual;")
        fecha = cursor.fetchone()
        print(f"\n📅 Fecha del sistema: {fecha[0]}")
        
        # Cerrar conexión
        cursor.close()
        conexion.close()
        
        print("\n" + "=" * 50)
        print("✅ ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("=" * 50)
        return True
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("📌 Verifica que el archivo 'database/conexion.py' existe")
        print("📌 Verifica que 'config.py' está en la raíz")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR AL CONECTAR: {e}")
        print("\n🔍 POSIBLES CAUSAS:")
        print("   1. PostgreSQL no está corriendo")
        print("   2. La base de datos 'gimnasio_db' no existe")
        print("   3. Credenciales incorrectas")
        print("   4. Puerto 5432 bloqueado o en uso")
        
        print("\n💡 SOLUCIONES:")
        print("   • Windows: Abre Services.msc y busca 'postgres'")
        print("   • Verifica que la base de datos existe:")
        print("     psql -U postgres -c 'CREATE DATABASE gimnasio_db;'")
        
        return False

if __name__ == '__main__':
    test_conexion()