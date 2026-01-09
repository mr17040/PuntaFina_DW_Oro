#!/usr/bin/env python3
"""
Script para ejecutar el ETL y verificar los resultados inmediatamente
"""
import subprocess
import psycopg2
import sys


def main():
    print("=" * 60)
    print("EJECUTANDO ETL BATCH")
    print("=" * 60)

    # Ejecutar ETL
    result = subprocess.run(
        ["python3", "etl_batch/main.py", "run"],
        cwd="/Users/elsalvador/project/PuntaFina_DW_Oro",
        capture_output=True,
        text=True,
    )

    # Mostrar salida del ETL (últimas 50 líneas)
    output_lines = result.stdout.split("\n")
    print("\n--- SALIDA ETL (últimas 30 líneas) ---")
    for line in output_lines[-30:]:
        print(line)

    if result.returncode != 0:
        print(f"\n❌ ETL falló con código {result.returncode}")
        print(result.stderr)
        return 1

    print("\n" + "=" * 60)
    print("VERIFICACIÓN INMEDIATA")
    print("=" * 60)

    # Conectar y verificar
    conn = psycopg2.connect(
        host="104.156.246.237",
        port=5432,
        dbname="datawarehouse_bi",
        user="sa",
        password="IngDatos123*",
    )
    cur = conn.cursor()

    # 1. Contar registros en tablas principales
    tables = [
        "dim_fecha",
        "dim_producto",
        "dim_cliente",
        "dim_orden",
        "dim_usuario",
        "dim_cuenta_contable",
        "dim_impuestos",
        "dim_promocion",
        "fact_ventas",
    ]

    print("\n📊 CONTEO DE REGISTROS:")
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            status = "✓" if count > 0 else "✗"
            print(f"   {status} {table}: {count:,}")
        except Exception as e:
            print(f"   ❌ {table}: {e}")

    # 2. Verificar dim_producto con precios/costos
    print("\n📦 DIM_PRODUCTO (precio_base y costo_estandar):")
    cur.execute("SELECT COUNT(*) FROM dim_producto")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dim_producto WHERE precio_base > 0")
    con_precio = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dim_producto WHERE costo_estandar > 0")
    con_costo = cur.fetchone()[0]
    print(f"   Total: {total}")
    print(
        f"   Con precio_base > 0: {con_precio} ({con_precio/total*100 if total > 0 else 0:.1f}%)"
    )
    print(
        f"   Con costo_estandar > 0: {con_costo} ({con_costo/total*100 if total > 0 else 0:.1f}%)"
    )

    cur.execute(
        "SELECT producto_id, sku, precio_base, costo_estandar FROM dim_producto WHERE costo_estandar > 0 LIMIT 5"
    )
    for row in cur.fetchall():
        print(f"      {row}")

    # 3. Verificar fact_ventas con costos
    print("\n💰 FACT_VENTAS (costos y margen):")
    cur.execute("SELECT COUNT(*) FROM fact_ventas")
    total_ventas = cur.fetchone()[0]
    if total_ventas > 0:
        cur.execute("SELECT COUNT(*) FROM fact_ventas WHERE costo_unitario > 0")
        con_costo_v = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM fact_ventas WHERE margen != 0")
        con_margen = cur.fetchone()[0]
        print(f"   Total ventas: {total_ventas:,}")
        print(
            f"   Con costo_unitario > 0: {con_costo_v:,} ({con_costo_v/total_ventas*100:.1f}%)"
        )
        print(
            f"   Con margen calculado: {con_margen:,} ({con_margen/total_ventas*100:.1f}%)"
        )

        cur.execute(
            """SELECT 
            ROUND(AVG(costo_unitario)::numeric, 2),
            ROUND(AVG(costo_total)::numeric, 2),
            ROUND(AVG(margen)::numeric, 2),
            ROUND(AVG(descuento)::numeric, 2)
        FROM fact_ventas"""
        )
        stats = cur.fetchone()
        print(
            f"   Promedios: costo_unitario={stats[0]}, costo_total={stats[1]}, margen={stats[2]}, descuento={stats[3]}"
        )

        cur.execute(
            """SELECT venta_id, cantidad, precio_unitario, subtotal, 
                              costo_unitario, costo_total, margen 
                       FROM fact_ventas WHERE costo_unitario > 0 LIMIT 5"""
        )
        for row in cur.fetchall():
            print(f"      {row}")
    else:
        print("   ⚠️ Sin datos en fact_ventas")

    # 4. Verificar dim_cuenta_contable sin nulos
    print("\n📊 DIM_CUENTA_CONTABLE (sin nulos):")
    cur.execute("SELECT COUNT(*) FROM dim_cuenta_contable")
    total_cuentas = cur.fetchone()[0]
    print(f"   Total: {total_cuentas}")
    if total_cuentas > 0:
        cur.execute(
            """SELECT COUNT(*) FROM dim_cuenta_contable 
                       WHERE codigo IS NULL OR nombre IS NULL"""
        )
        con_nulos = cur.fetchone()[0]
        print(f"   Con nulos en codigo/nombre: {con_nulos}")

    conn.close()

    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
