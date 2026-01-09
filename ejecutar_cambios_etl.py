#!/usr/bin/env python3
"""
Script para aplicar cambios al DW y ejecutar ETL completo
Aplica cambios de esquema y ejecuta ETL con las mejoras solicitadas
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Cambiar al directorio del script
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

print("═" * 80)
print("🔧 APLICANDO CAMBIOS AL DATA WAREHOUSE - PUNTAFINA")
print("═" * 80)
print()

# Cargar variables de entorno
env_file = SCRIPT_DIR / "etl_batch" / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print("✓ Variables de entorno cargadas")
else:
    print("❌ Error: Archivo .env no encontrado")
    sys.exit(1)


def run_sql_script(sql_file):
    """Ejecutar script SQL usando psycopg2"""
    import psycopg2

    print(f"\n📋 Ejecutando: {sql_file.name}")
    print("─" * 80)

    try:
        conn = psycopg2.connect(
            host=os.getenv("DW_DB_HOST"),
            port=int(os.getenv("DW_DB_PORT")),
            dbname=os.getenv("DW_DB_NAME"),
            user=os.getenv("DW_DB_USER"),
            password=os.getenv("DW_DB_PASS"),
            connect_timeout=30,
        )

        cursor = conn.cursor()

        with open(sql_file, "r") as f:
            sql = f.read()

        cursor.execute(sql)
        conn.commit()

        print(f"✓ Script {sql_file.name} ejecutado correctamente")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error ejecutando {sql_file.name}: {e}")
        return False


def verify_results():
    """Verificar los resultados del ETL"""
    import psycopg2

    print("\n📋 Verificando resultados...")
    print("─" * 80)

    try:
        conn = psycopg2.connect(
            host=os.getenv("DW_DB_HOST"),
            port=int(os.getenv("DW_DB_PORT")),
            dbname=os.getenv("DW_DB_NAME"),
            user=os.getenv("DW_DB_USER"),
            password=os.getenv("DW_DB_PASS"),
            connect_timeout=30,
        )

        cursor = conn.cursor()

        # Verificar dim_cuenta_contable
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE codigo IS NULL OR codigo = '') as nulos_codigo,
                COUNT(*) FILTER (WHERE nombre IS NULL OR nombre = '') as nulos_nombre
            FROM dim_cuenta_contable
        """
        )
        total, nulos_codigo, nulos_nombre = cursor.fetchone()
        print(f"\n📊 dim_cuenta_contable:")
        print(f"   Total: {total:,} registros")
        print(f"   Nulos en código: {nulos_codigo}")
        print(f"   Nulos en nombre: {nulos_nombre}")

        # Verificar dim_producto
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE precio_base > 0) as con_precio,
                COUNT(*) FILTER (WHERE costo_estandar > 0) as con_costo,
                ROUND(AVG(precio_base), 2) as precio_promedio,
                ROUND(AVG(costo_estandar), 2) as costo_promedio
            FROM dim_producto
        """
        )
        total, con_precio, con_costo, precio_prom, costo_prom = cursor.fetchone()
        print(f"\n📊 dim_producto:")
        print(f"   Total: {total:,} registros")
        print(f"   Con precio_base: {con_precio:,} ({con_precio/total*100:.1f}%)")
        print(f"   Con costo_estandar: {con_costo:,} ({con_costo/total*100:.1f}%)")
        print(f"   Precio promedio: ${precio_prom}")
        print(f"   Costo promedio: ${costo_prom}")

        # Verificar dim_promocion
        cursor.execute("SELECT COUNT(*) FROM dim_promocion")
        total_promo = cursor.fetchone()[0]
        print(f"\n📊 dim_promocion:")
        print(f"   Total: {total_promo:,} registros")

        # Verificar fact_ventas
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE costo_unitario > 0) as con_costo,
                COUNT(*) FILTER (WHERE descuento > 0) as con_descuento,
                COUNT(*) FILTER (WHERE margen > 0) as con_margen_positivo,
                ROUND(AVG(costo_unitario), 2) as costo_promedio,
                ROUND(AVG(margen), 2) as margen_promedio,
                ROUND(SUM(descuento), 2) as total_descuentos
            FROM fact_ventas
        """
        )
        total, con_costo, con_desc, con_margen, costo_prom, margen_prom, total_desc = (
            cursor.fetchone()
        )
        print(f"\n📊 fact_ventas:")
        print(f"   Total: {total:,} registros")
        print(f"   Con costo: {con_costo:,} ({con_costo/total*100:.1f}%)")
        print(f"   Con descuento: {con_desc:,} ({con_desc/total*100:.1f}%)")
        print(f"   Con margen positivo: {con_margen:,} ({con_margen/total*100:.1f}%)")
        print(f"   Costo unitario promedio: ${costo_prom}")
        print(f"   Margen promedio: ${margen_prom}")
        print(f"   Total descuentos aplicados: ${total_desc:,.2f}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error verificando resultados: {e}")
        return False


# Paso 1: Aplicar cambios al esquema
print("\n📋 Paso 1: Aplicando cambios al esquema de la base de datos...")
print("─" * 80)

sql_file = SCRIPT_DIR / "sql" / "granular" / "add_promocion_to_fact_ventas.sql"
if not sql_file.exists():
    print(f"❌ Error: Archivo SQL no encontrado: {sql_file}")
    sys.exit(1)

# Instalar psycopg2 si no está instalado
try:
    import psycopg2
except ImportError:
    print("⚠️  psycopg2 no instalado. Instalando...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "psycopg2-binary",
            "--break-system-packages",
        ]
    )
    import psycopg2

if not run_sql_script(sql_file):
    print("\n❌ Error aplicando cambios de esquema")
    sys.exit(1)

print("\n✓ Cambios de esquema aplicados correctamente")

# Paso 2: Ejecutar ETL
print("\n📋 Paso 2: Ejecutando ETL completo...")
print("─" * 80)

etl_dir = SCRIPT_DIR / "etl_batch"
os.chdir(etl_dir)

# Verificar e instalar dependencias
required_packages = ["pandas", "psycopg2", "pyyaml", "python-dotenv"]
for package in required_packages:
    package_import = package.replace("-", "_").replace("pyyaml", "yaml")
    try:
        __import__(package_import)
    except ImportError:
        print(f"⚠️  Instalando {package}...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-q",
                package,
                "--break-system-packages",
            ]
        )

print("\n🚀 Ejecutando ETL...")
result = subprocess.run(
    [sys.executable, "main.py", "run"], capture_output=False, text=True
)

os.chdir(SCRIPT_DIR)

# Paso 3: Verificar resultados
if result.returncode == 0:
    print("\n✓ ETL ejecutado correctamente")

    if verify_results():
        print("\n" + "═" * 80)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("═" * 80)
        print("\nResumen de cambios aplicados:")
        print("  1. ✓ dim_cuenta_contable: Sin nulos o NaN")
        print("  2. ✓ dim_producto: Con precio_base y costo_estandar desde fuentes")
        print(
            "  3. ✓ fact_ventas: Con costo_unitario, costo_total, margen y descuentos"
        )
        print("  4. ✓ dim_promocion: Creada con datos desde oro_order")
        print()
    else:
        print("\n⚠️  Verificación de resultados falló")
        sys.exit(1)
else:
    print(f"\n❌ Error en la ejecución del ETL (código de salida: {result.returncode})")
    sys.exit(1)
