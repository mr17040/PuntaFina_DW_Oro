#!/usr/bin/env python3
"""
Poblar dimensiones faltantes del Data Warehouse
"""

import pandas as pd
import psycopg2
from datetime import datetime
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def get_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        user='sa',
        password='IngDatos123*',
        database='datawarehouse_bi'
    )

def get_oro_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        user='sa',
        password='IngDatos123*',
        database='orocommerce'
    )

def load_dataframe(conn, df, table_name):
    """Cargar DataFrame a tabla DW"""
    try:
        cursor = conn.cursor()
        
        # Obtener columnas de la tabla DW
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND table_schema = 'public'
            AND column_name NOT IN (
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_default LIKE 'nextval%'
            )
            ORDER BY ordinal_position
        """)
        dw_columns = [row[0] for row in cursor.fetchall()]
        
        # Filtrar columnas que existen
        df_filtered = df[[col for col in df.columns if col in dw_columns]]
        
        if df_filtered.empty:
            logger.warning(f"No hay columnas coincidentes para {table_name}")
            return 0
        
        # Truncar tabla
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
        
        # Insertar datos
        from io import StringIO
        buffer = StringIO()
        df_filtered.to_csv(buffer, index=False, header=False, na_rep='\\N')
        buffer.seek(0)
        
        columns_str = ', '.join(df_filtered.columns)
        cursor.copy_expert(
            f"COPY {table_name} ({columns_str}) FROM STDIN WITH CSV NULL '\\N'",
            buffer
        )
        conn.commit()
        
        logger.success(f"✅ {table_name}: {len(df_filtered):,} registros cargados")
        return len(df_filtered)
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error cargando {table_name}: {str(e)}")
        return 0

def populate_dim_direccion():
    """Poblar dim_direccion desde oro_customer_address"""
    logger.info("📍 Poblando dim_direccion...")
    
    conn_oro = get_oro_connection()
    conn_dw = get_connection()
    
    query = """
    SELECT 
        ca.id as direccion_externo_id,
        ca.frontend_owner_id as cliente_id,
        COALESCE(ca.label, 'Principal') as etiqueta,
        COALESCE(ca.street, '') as calle,
        COALESCE(ca.city, '') as ciudad,
        COALESCE(ca.postal_code, '') as codigo_postal,
        COALESCE(ca.country_code, 'SV') as pais,
        COALESCE(ca.region_code, '') as region,
        'envio' as tipo_direccion,
        true as activo,
        ca.created as fecha_creacion
    FROM oro_customer_address ca
    WHERE ca.id IS NOT NULL
    LIMIT 50000
    """
    
    df = pd.read_sql(query, conn_oro)
    rows = load_dataframe(conn_dw, df, 'dim_direccion')
    
    conn_oro.close()
    conn_dw.close()
    return rows

def populate_dim_envio():
    """Poblar dim_envio - Generada"""
    logger.info("🚚 Poblando dim_envio...")
    
    conn_dw = get_connection()
    
    # Generar métodos de envío estándar
    envios = [
        {'codigo_metodo': 'STD', 'nombre_metodo': 'Envío Estándar', 'proveedor': 'DHL', 'costo_base': 5.0, 'dias_entrega': 5, 'activo': True},
        {'codigo_metodo': 'EXP', 'nombre_metodo': 'Envío Express', 'proveedor': 'FedEx', 'costo_base': 15.0, 'dias_entrega': 2, 'activo': True},
        {'codigo_metodo': 'RET', 'nombre_metodo': 'Retiro en Tienda', 'proveedor': 'Punta Fina', 'costo_base': 0.0, 'dias_entrega': 1, 'activo': True}
    ]
    
    df = pd.DataFrame(envios)
    rows = load_dataframe(conn_dw, df, 'dim_envio')
    
    conn_dw.close()
    return rows

def populate_dim_pago():
    """Poblar dim_pago - Generada"""
    logger.info("💳 Poblando dim_pago...")
    
    conn_dw = get_connection()
    
    pagos = [
        {'metodo_pago': 'CASH', 'nombre_metodo': 'Efectivo', 'tipo_pago': 'cash', 'requiere_aprobacion': False, 'activo': True},
        {'metodo_pago': 'CARD', 'nombre_metodo': 'Tarjeta', 'tipo_pago': 'card', 'requiere_aprobacion': True, 'activo': True},
        {'metodo_pago': 'TRANSFER', 'nombre_metodo': 'Transferencia', 'tipo_pago': 'bank', 'requiere_aprobacion': True, 'activo': True}
    ]
    
    df = pd.DataFrame(pagos)
    rows = load_dataframe(conn_dw, df, 'dim_pago')
    
    conn_dw.close()
    return rows

def populate_dim_estado_pago():
    """Poblar dim_estado_pago - Generada"""
    logger.info("💰 Poblando dim_estado_pago...")
    
    conn_dw = get_connection()
    
    estados = [
        {'codigo_estado': 'PENDING', 'nombre_estado': 'Pendiente', 'descripcion': 'Pago pendiente', 'es_final': False},
        {'codigo_estado': 'APPROVED', 'nombre_estado': 'Aprobado', 'descripcion': 'Pago aprobado', 'es_final': True},
        {'codigo_estado': 'REJECTED', 'nombre_estado': 'Rechazado', 'descripcion': 'Pago rechazado', 'es_final': True},
        {'codigo_estado': 'CANCELLED', 'nombre_estado': 'Cancelado', 'descripcion': 'Pago cancelado', 'es_final': True}
    ]
    
    df = pd.DataFrame(estados)
    rows = load_dataframe(conn_dw, df, 'dim_estado_pago')
    
    conn_dw.close()
    return rows

def populate_dim_impuestos():
    """Poblar dim_impuestos - Generada"""
    logger.info("🧾 Poblando dim_impuestos...")
    
    conn_dw = get_connection()
    
    impuestos = [
        {'codigo': 'IVA', 'nombre': 'IVA', 'tasa': 13.0, 'tipo': 'venta', 'descripcion': 'Impuesto al Valor Agregado', 'activo': True},
        {'codigo': 'ISR', 'nombre': 'ISR', 'tasa': 25.0, 'tipo': 'renta', 'descripcion': 'Impuesto Sobre la Renta', 'activo': True},
        {'codigo': 'EXENTO', 'nombre': 'Exento', 'tasa': 0.0, 'tipo': 'exento', 'descripcion': 'Sin impuesto', 'activo': True}
    ]
    
    df = pd.DataFrame(impuestos)
    rows = load_dataframe(conn_dw, df, 'dim_impuestos')
    
    conn_dw.close()
    return rows

def populate_dim_line_item():
    """Poblar dim_line_item desde oro_order_line_item"""
    logger.info("📝 Poblando dim_line_item...")
    
    conn_oro = get_oro_connection()
    conn_dw = get_connection()
    
    query = """
    SELECT 
        oli.id as line_item_externo_id,
        oli.order_id,
        oli.product_id,
        oli.product_sku as sku,
        oli.product_name as nombre_producto,
        oli.quantity as cantidad,
        oli.value as precio_unitario,
        oli.currency as moneda,
        oli.quantity * oli.value as subtotal
    FROM oro_order_line_item oli
    WHERE oli.id IS NOT NULL
    LIMIT 100000
    """
    
    df = pd.read_sql(query, conn_oro)
    
    # Convertir IDs a enteros
    df['line_item_externo_id'] = pd.to_numeric(df['line_item_externo_id'], errors='coerce').fillna(0).astype(int)
    df['order_id'] = pd.to_numeric(df['order_id'], errors='coerce').fillna(0).astype(int)
    df['product_id'] = pd.to_numeric(df['product_id'], errors='coerce').fillna(0).astype(int)
    
    rows = load_dataframe(conn_dw, df, 'dim_line_item')
    
    conn_oro.close()
    conn_dw.close()
    return rows

def main():
    logger.info("\n" + "="*80)
    logger.info("🚀 POBLANDO DIMENSIONES FALTANTES")
    logger.info("="*80 + "\n")
    
    start_time = datetime.now()
    
    # Poblar cada dimensión
    dimensions = [
        ('dim_direccion', populate_dim_direccion),
        ('dim_envio', populate_dim_envio),
        ('dim_pago', populate_dim_pago),
        ('dim_estado_pago', populate_dim_estado_pago),
        ('dim_impuestos', populate_dim_impuestos),
        ('dim_line_item', populate_dim_line_item),
    ]
    
    total_loaded = 0
    for name, func in dimensions:
        try:
            rows = func()
            total_loaded += rows
        except Exception as e:
            logger.error(f"❌ Error en {name}: {str(e)}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "="*80)
    logger.success(f"✅ DIMENSIONES COMPLETADAS")
    logger.info("="*80)
    logger.info(f"⏱️  Tiempo: {duration:.2f} segundos")
    logger.info(f"📊 Total: {total_loaded:,} registros cargados")
    logger.info("="*80)

if __name__ == "__main__":
    main()
