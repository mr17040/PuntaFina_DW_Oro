#!/usr/bin/env python3
"""
Debug: Verificar todas las dimensiones individualmente
"""
import os
import sys

os.chdir("/Users/elsalvador/project/PuntaFina_DW_Oro")
sys.path.insert(0, "/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch")

from dotenv import load_dotenv

load_dotenv("/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/.env")

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

from transformers.complete_dimension_builder import CompleteDimensionBuilder

DW_CONFIG = {
    "host": os.getenv("DW_DB_HOST"),
    "port": int(os.getenv("DW_DB_PORT", 5432)),
    "dbname": os.getenv("DW_DB_NAME"),
    "user": os.getenv("DW_DB_USER"),
    "password": os.getenv("DW_DB_PASS"),
}


def get_db_columns(table_name):
    """Obtener columnas de la base de datos"""
    conn = psycopg2.connect(**DW_CONFIG)
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """,
        (table_name,),
    )
    cols = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return cols


def test_dimension(dim_name, builder_method):
    """Probar una dimensión"""
    print(f"\n{'='*60}")
    print(f"TEST: {dim_name}")
    print("=" * 60)

    try:
        # Obtener DataFrame
        df = builder_method()
        if df is None or len(df) == 0:
            print(f"  ⚠️  Sin datos generados")
            return False, "Sin datos"

        builder_cols = df.columns.tolist()
        db_cols = get_db_columns(dim_name)

        print(f"  Builder genera: {builder_cols}")
        print(f"  DB espera:      {db_cols}")

        # Verificar columnas extras en builder
        extras = set(builder_cols) - set(db_cols)
        if extras:
            print(f"  ❌ Columnas NO existen en DB: {extras}")

        # Verificar columnas faltantes
        missing = (
            set(db_cols)
            - set(builder_cols)
            - {dim_name.replace("dim_", "") + "_id", "updated_at"}
        )  # Ignorar IDs auto y updated_at
        # Para dim_producto el ID es producto_id, pero el serial es automático
        if missing:
            print(f"  ⚠️  Columnas faltantes (pueden ser opcionales): {missing}")

        # Intentar insert
        conn = psycopg2.connect(**DW_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        # Truncar
        cursor.execute(f"TRUNCATE TABLE {dim_name} CASCADE")

        # Preparar datos
        columns = df.columns.tolist()
        values = [tuple(row) for row in df.values]

        insert_query = f"""
            INSERT INTO {dim_name} ({', '.join(columns)})
            VALUES %s
        """

        execute_values(cursor, insert_query, values, page_size=1000)

        # Verificar
        cursor.execute(f"SELECT COUNT(*) FROM {dim_name}")
        count = cursor.fetchone()[0]
        print(f"  ✅ INSERT exitoso: {count:,} registros")

        cursor.close()
        conn.close()
        return True, count

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False, str(e)


# Probar cada dimensión
builder = CompleteDimensionBuilder()

dimensions = [
    ("dim_fecha", builder.build_dim_fecha),
    ("dim_producto", builder.build_dim_producto),
    ("dim_cliente", builder.build_dim_cliente),
    ("dim_orden", builder.build_dim_orden),
    ("dim_usuario", builder.build_dim_usuario),
    ("dim_cuenta_contable", builder.build_dim_cuenta_contable),
    ("dim_impuestos", builder.build_dim_impuestos),
    ("dim_promocion", builder.build_dim_promocion),
    ("dim_almacen", builder.build_dim_almacen),
    ("dim_proveedor", builder.build_dim_proveedor),
    ("dim_tipo_movimiento", builder.build_dim_tipo_movimiento),
    ("dim_centro_costo", builder.build_dim_centro_costo),
    ("dim_tipo_transaccion", builder.build_dim_tipo_transaccion),
]

results = {}
for dim_name, method in dimensions:
    success, info = test_dimension(dim_name, method)
    results[dim_name] = (success, info)

# Resumen
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
for dim, (success, info) in results.items():
    status = "✅" if success else "❌"
    print(f"  {status} {dim}: {info}")
