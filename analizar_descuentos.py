#!/usr/bin/env python3
"""Analizar descuentos y promociones en oro_order"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("etl_batch/.env")

conn = psycopg2.connect(
    host=os.getenv("ORO_DB_HOST"),
    port=os.getenv("ORO_DB_PORT", 5432),
    database=os.getenv("ORO_DB_NAME"),
    user=os.getenv("ORO_DB_USER"),
    password=os.getenv("ORO_DB_PASS"),
)

cur = conn.cursor()

print("\n" + "=" * 70)
print("ANÁLISIS DE DESCUENTOS EN ORO_ORDER")
print("=" * 70)

cur.execute(
    """
    SELECT 
        COALESCE(total_discounts_amount, 0) as descuento,
        COUNT(*) as cantidad,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as porcentaje
    FROM oro_order 
    GROUP BY COALESCE(total_discounts_amount, 0)
    ORDER BY COUNT(*) DESC
    LIMIT 10
"""
)

print("\nDistribución de descuentos:")
print("-" * 70)
print(f"{'Descuento':>15} | {'Órdenes':>10} | {'% del total':>12}")
print("-" * 70)
for row in cur.fetchall():
    print(f"${row[0]:>14.2f} | {row[1]:>10,} | {row[2]:>11.2f}%")

print("\n" + "=" * 70)
print("RESUMEN GENERAL")
print("=" * 70)

cur.execute(
    """
    SELECT 
        COUNT(*) as total_ordenes,
        SUM(CASE WHEN total_discounts_amount > 0 THEN 1 ELSE 0 END) as con_descuento,
        SUM(CASE WHEN total_discounts_amount IS NULL OR total_discounts_amount = 0 THEN 1 ELSE 0 END) as sin_descuento,
        ROUND(100.0 * SUM(CASE WHEN total_discounts_amount > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as porcentaje_con_descuento
    FROM oro_order
"""
)

row = cur.fetchone()
print(f"\nTotal de órdenes:         {row[0]:>10,}")
print(f"Con descuento:            {row[1]:>10,} ({row[3]:>5.2f}%)")
print(f"Sin descuento:            {row[2]:>10,} ({100-row[3]:>5.2f}%)")

cur.close()
conn.close()

print("\n" + "=" * 70)
