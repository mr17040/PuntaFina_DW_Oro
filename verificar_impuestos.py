#!/usr/bin/env python3
"""
Script para verificar la integración de impuesto_id en fact_ventas
"""
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime

def verificar_integracion():
    """Verificar que la relación con dim_impuestos funciona correctamente"""
    
    print("=" * 70)
    print("VERIFICACIÓN DE INTEGRACIÓN: dim_impuestos → fact_ventas")
    print("=" * 70)
    print()
    
    # Conectar a la base de datos
    conn = psycopg2.connect(
        host="localhost",
        database="datawarehouse_bi",
        user="sa",
        password="IngDatos123*"
    )
    
    cursor = conn.cursor()
    
    # 1. Verificar estructura de fact_ventas
    print("1️⃣ Verificando estructura de fact_ventas...")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'fact_ventas' AND column_name = 'impuesto_id';
    """)
    result = cursor.fetchone()
    if result:
        print(f"   ✅ Columna impuesto_id encontrada: {result[1]} (nullable: {result[2]})")
    else:
        print("   ❌ Columna impuesto_id NO encontrada")
        return
    
    print()
    
    # 2. Verificar Foreign Key
    print("2️⃣ Verificando Foreign Key...")
    cursor.execute("""
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        WHERE tc.table_name = 'fact_ventas'
          AND tc.constraint_type = 'FOREIGN KEY'
          AND tc.constraint_name LIKE '%impuesto%';
    """)
    fk = cursor.fetchone()
    if fk:
        print(f"   ✅ Foreign Key encontrado: {fk[0]}")
    else:
        print("   ❌ Foreign Key NO encontrado")
    
    print()
    
    # 3. Verificar índice
    print("3️⃣ Verificando índice...")
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'fact_ventas'
          AND indexname LIKE '%impuesto%';
    """)
    idx = cursor.fetchone()
    if idx:
        print(f"   ✅ Índice encontrado: {idx[0]}")
    else:
        print("   ⚠️  Índice NO encontrado")
    
    print()
    
    # 4. Verificar datos
    print("4️⃣ Verificando distribución de datos...")
    query = """
    SELECT 
        i.impuesto_id,
        i.nombre,
        i.tasa,
        COUNT(*) as cantidad_ventas,
        SUM(v.impuesto) as total_impuestos,
        ROUND(AVG(v.impuesto), 2) as promedio_impuesto
    FROM fact_ventas v
    LEFT JOIN dim_impuestos i ON v.impuesto_id = i.impuesto_id
    GROUP BY i.impuesto_id, i.nombre, i.tasa
    ORDER BY cantidad_ventas DESC;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print()
    
    # 5. Verificar consistencia
    print("5️⃣ Verificando consistencia...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM fact_ventas 
        WHERE impuesto_id IS NULL;
    """)
    null_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fact_ventas;")
    total_count = cursor.fetchone()[0]
    
    if null_count == 0:
        print(f"   ✅ Todos los registros tienen impuesto_id asignado ({total_count:,} registros)")
    else:
        print(f"   ⚠️  {null_count:,} registros sin impuesto_id de {total_count:,} totales")
    
    print()
    
    # 6. Ejemplo de consulta JOIN
    print("6️⃣ Ejemplo de consulta con JOIN...")
    query_ejemplo = """
    SELECT 
        TO_CHAR(f.fecha::DATE, 'YYYY-MM') as mes,
        i.nombre as tipo_impuesto,
        COUNT(*) as num_ventas,
        SUM(v.subtotal) as subtotal,
        SUM(v.impuesto) as impuesto,
        SUM(v.total) as total
    FROM fact_ventas v
    JOIN dim_fecha f ON v.fecha_id = f.fecha_id
    JOIN dim_impuestos i ON v.impuesto_id = i.impuesto_id
    WHERE f.anio = 2024
    GROUP BY TO_CHAR(f.fecha::DATE, 'YYYY-MM'), i.impuesto_id, i.nombre
    ORDER BY mes DESC, num_ventas DESC
    LIMIT 10;
    """
    df_ejemplo = pd.read_sql_query(query_ejemplo, conn)
    print("\n📊 Ventas por mes y tipo de impuesto (2024):")
    print(df_ejemplo.to_string(index=False))
    
    print()
    print("=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_integracion()
