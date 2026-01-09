#!/usr/bin/env python3
"""Verificación final del ETL"""

import psycopg2

conn = psycopg2.connect(
    host="104.156.246.237",
    port=5432,
    database="datawarehouse_bi",
    user="sa",
    password="IngDatos123*",
)

cur = conn.cursor()

print("\n" + "=" * 70)
print("VERIFICACIÓN POST-ETL - RESULTADOS FINALES")
print("=" * 70)

print("\n📊 dim_impuestos:")
print("-" * 70)
cur.execute(
    "SELECT impuesto_id, codigo, nombre, tasa, tipo FROM dim_impuestos ORDER BY impuesto_id"
)
for row in cur.fetchall():
    print(
        f"  ID={row[0]:>2} | {row[1]:<10} | {row[2]:<20} | Tasa: {float(row[3])*100:.2f}% | Tipo: {row[4]}"
    )

print("\n📊 dim_promocion:")
print("-" * 70)
cur.execute(
    "SELECT sk_promocion, id_promocion_source, nombre_promocion, tipo_promocion FROM dim_promocion ORDER BY sk_promocion"
)
for row in cur.fetchall():
    print(f"  SK={row[0]:>2} | Src_ID={row[1]:>3} | {row[2]:<35} | Tipo: {row[3]}")

print("\n📊 fact_ventas (distribución de promociones):")
print("-" * 70)
cur.execute(
    "SELECT sk_promocion, COUNT(*), ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(), 2) as pct FROM fact_ventas GROUP BY sk_promocion ORDER BY COUNT(*) DESC"
)
for row in cur.fetchall():
    print(f"  sk_promocion={row[0]:>2} | Registros: {row[1]:>7,} ({row[2]:>5.2f}%)")

print("\n📊 fact_ventas (distribución de impuestos):")
print("-" * 70)
cur.execute(
    "SELECT impuesto_id, COUNT(*), ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(), 2) as pct FROM fact_ventas GROUP BY impuesto_id ORDER BY COUNT(*) DESC"
)
for row in cur.fetchall():
    print(f"  impuesto_id={row[0]:>2} | Registros: {row[1]:>7,} ({row[2]:>5.2f}%)")

print("\n📊 fact_ventas (resumen de descuentos):")
print("-" * 70)
cur.execute(
    """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN descuento > 0 THEN 1 ELSE 0 END) as con_descuento,
        ROUND(AVG(descuento), 2) as promedio_descuento,
        ROUND(SUM(descuento), 2) as total_descuentos
    FROM fact_ventas
"""
)
row = cur.fetchone()
print(f"  Total registros:      {row[0]:>7,}")
print(f"  Con descuento:        {row[1]:>7,} ({100*row[1]/row[0]:.2f}%)")
print(f"  Promedio descuento:   ${float(row[2]):>8.2f}")
print(f"  Total descuentos:     ${float(row[3]):>10,.2f}")

cur.close()
conn.close()

print("\n" + "=" * 70)
