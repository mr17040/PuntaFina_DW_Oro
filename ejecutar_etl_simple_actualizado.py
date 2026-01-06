#!/usr/bin/env python3
"""
ETL SIMPLE ACTUALIZADO - SOLO CARGAR DATOS EXISTENTES CON NUEVA ESTRUCTURA
===========================================================================
Carga datos desde las bases de datos origen manteniendo simetría
"""

import psycopg2
import pandas as pd
from datetime import datetime
import sys

# Configuración de bases de datos
DB_CONFIG = {
    'orocommerce': {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'orocommerce',
        'user': 'sa',
        'password': 'IngDatos123*'
    },
    'oro_crm': {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'oro_crm',
        'user': 'sa',
        'password': 'IngDatos123*'
    },
    'datawarehouse_bi': {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'datawarehouse_bi',
        'user': 'sa',
        'password': 'IngDatos123*'
    }
}

def get_connection(db_name):
    """Obtener conexión a base de datos"""
    config = DB_CONFIG[db_name]
    return psycopg2.connect(**config)

def limpiar_fact_ventas():
    """Limpiar fact_ventas antes de recargar"""
    print("🧹 Limpiando fact_ventas...")
    conn = get_connection('datawarehouse_bi')
    cursor = conn.cursor()
    cursor.execute("TRUNCATE fact_ventas CASCADE")
    conn.commit()
    cursor.close()
    conn.close()
    print("   ✅ fact_ventas limpiada")

def cargar_fact_ventas():
    """Cargar fact_ventas desde OroCommerce con impuesto_id correcto"""
    print("\n📊 Cargando fact_ventas...")
    
    # Conectar a origen
    conn_oro = get_connection('orocommerce')
    
    # Query simplificado para extraer ventas (basado en estructura real de OroCommerce)
    query = """
    SELECT 
        o.created_at::date as fecha,
        COALESCE(o.customer_user_id, o.id * 1000) as cliente_oro_id,
        oli.product_id as producto_oro_id,
        o.id as orden_oro_id,
        COALESCE(o.user_owner_id, 1) as usuario_oro_id,
        CAST(oli.quantity AS NUMERIC) as cantidad,
        CAST(oli.value AS NUMERIC) as precio_unitario,
        CAST(oli.quantity * oli.value AS NUMERIC) as subtotal,
        CAST(o.total_value AS NUMERIC) as total
    FROM oro_order o
    JOIN oro_order_line_item oli ON o.id = oli.order_id
    WHERE o.created_at IS NOT NULL
        AND oli.product_id IS NOT NULL
    ORDER BY o.created_at, o.id
    """
    
    print("   📥 Extrayendo datos de OroCommerce...")
    df = pd.read_sql_query(query, conn_oro)
    conn_oro.close()
    print(f"   ✓ {len(df):,} registros extraídos")
    
    # Calcular campos adicionales
    df['descuento'] = 0.0
    df['impuesto'] = (df['subtotal'] * 0.13).round(2)
    df['envio'] = 0.0
    df['costo_unitario'] = (df['precio_unitario'] * 0.6).round(2)
    df['costo_total'] = (df['costo_unitario'] * df['cantidad']).round(2)
    df['margen'] = (df['subtotal'] - df['costo_total']).round(2)
    
    # Conectar al DW
    conn_dw = get_connection('datawarehouse_bi')
    cursor = conn_dw.cursor()
    
    # Obtener mapeos de dimensiones
    print("   🔗 Obteniendo mapeos de dimensiones...")
    
    # Mapeo fecha
    cursor.execute("SELECT fecha_id, fecha FROM dim_fecha")
    fecha_map = {str(row[1]): row[0] for row in cursor.fetchall()}
    
    # Mapeo cliente - por cliente_externo_id
    cursor.execute("SELECT cliente_id, cliente_externo_id FROM dim_cliente WHERE cliente_externo_id IS NOT NULL")
    cliente_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Mapeo producto - por producto_externo_id
    cursor.execute("SELECT producto_id, producto_externo_id FROM dim_producto WHERE producto_externo_id IS NOT NULL")
    producto_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Mapeo orden - por orden_externo_id
    cursor.execute("SELECT orden_id, orden_externo_id FROM dim_orden WHERE orden_externo_id IS NOT NULL")
    orden_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Mapeo usuario - por usuario_externo_id
    cursor.execute("SELECT usuario_id, usuario_externo_id FROM dim_usuario WHERE usuario_externo_id IS NOT NULL")
    usuario_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Para almacen_id: usar distribución aleatoria entre los 6 almacenes (mantener simetría)
    cursor.execute("SELECT almacen_id FROM dim_almacen ORDER BY almacen_id")
    almacenes = [row[0] for row in cursor.fetchall()]
    
    print("   💾 Insertando registros en fact_ventas...")
    
    inserted = 0
    skipped = 0
    
    insert_query = """
    INSERT INTO fact_ventas (
        fecha_id, cliente_id, producto_id, orden_id, usuario_id, almacen_id, impuesto_id,
        cantidad, precio_unitario, subtotal, descuento, impuesto, envio, total,
        costo_unitario, costo_total, margen, created_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, CURRENT_TIMESTAMP
    )
    """
    
    for idx, row in df.iterrows():
        try:
            # Mapear IDs
            fecha_key = str(row['fecha'])
            fecha_id = fecha_map.get(fecha_key)
            cliente_id = cliente_map.get(row['cliente_oro_id'])
            producto_id = producto_map.get(row['producto_oro_id'])
            orden_id = orden_map.get(row['orden_oro_id'])
            usuario_id = usuario_map.get(row['usuario_oro_id']) if pd.notna(row['usuario_oro_id']) else 1
            
            # Asignar almacen de manera cíclica (mantener simetría con datos originales)
            almacen_id = almacenes[idx % len(almacenes)] if almacenes else 1
            
            # Calcular impuesto_id basado en el monto
            impuesto_id = 1 if row['impuesto'] > 0 else 5  # 1=IVA 13%, 5=EXENTO
            
            # Validar que IDs críticos existan
            if all([fecha_id, cliente_id, producto_id, orden_id]):
                cursor.execute(insert_query, (
                    fecha_id, cliente_id, producto_id, orden_id, usuario_id, almacen_id, impuesto_id,
                    float(row['cantidad']), float(row['precio_unitario']), float(row['subtotal']), 
                    float(row['descuento']), float(row['impuesto']), float(row['envio']), float(row['total']),
                    float(row['costo_unitario']), float(row['costo_total']), float(row['margen'])
                ))
                inserted += 1
                
                if inserted % 1000 == 0:
                    conn_dw.commit()
                    print(f"      • {inserted:,} registros insertados...")
            else:
                skipped += 1
                
        except Exception as e:
            if inserted < 5:  # Solo mostrar primeros errores
                print(f"      ⚠️ Error en registro {idx}: {e}")
            skipped += 1
            continue
    
    conn_dw.commit()
    cursor.close()
    conn_dw.close()
    
    print(f"\n   ✅ Carga completada:")
    print(f"      • Insertados: {inserted:,}")
    print(f"      • Omitidos: {skipped:,}")
    
    return inserted

def verificar_resultados():
    """Verificar los resultados de la carga"""
    print("\n🔍 Verificando resultados...")
    
    conn = get_connection('datawarehouse_bi')
    cursor = conn.cursor()
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM fact_ventas")
    total = cursor.fetchone()[0]
    print(f"   📊 Total registros en fact_ventas: {total:,}")
    
    # Verificar impuesto_id
    cursor.execute("""
        SELECT 
            i.nombre,
            COUNT(*) as num_registros,
            SUM(fv.impuesto) as total_impuestos
        FROM fact_ventas fv
        JOIN dim_impuestos i ON fv.impuesto_id = i.impuesto_id
        GROUP BY i.nombre
        ORDER BY num_registros DESC
    """)
    
    print("\n   📈 Distribución por tipo de impuesto:")
    for row in cursor.fetchall():
        print(f"      • {row[0]}: {row[1]:,} registros, ${row[2]:,.2f}")
    
    cursor.close()
    conn.close()

def main():
    """Ejecutar ETL simple actualizado"""
    print("="*80)
    print("ETL SIMPLE ACTUALIZADO - PUNTAFINA DATA WAREHOUSE")
    print("="*80)
    print(f"Inicio: {datetime.now()}\n")
    
    try:
        # 1. Limpiar fact_ventas
        limpiar_fact_ventas()
        
        # 2. Cargar fact_ventas con nueva estructura
        total = cargar_fact_ventas()
        
        # 3. Verificar resultados
        verificar_resultados()
        
        print("\n" + "="*80)
        print("✅ ETL COMPLETADO EXITOSAMENTE")
        print("="*80)
        print(f"Fin: {datetime.now()}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
