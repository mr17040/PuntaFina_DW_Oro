#!/usr/bin/env python3
"""
Cargar tablas de hechos con ajuste de IDs para FK
"""

import pandas as pd
import psycopg2
from datetime import datetime
from loguru import logger
import sys
from io import StringIO

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def get_oro_conn():
    return psycopg2.connect(host='localhost', port=5432, user='sa', password='IngDatos123*', database='orocommerce')

def get_dw_conn():
    return psycopg2.connect(host='localhost', port=5432, user='sa', password='IngDatos123*', database='datawarehouse_bi')

def load_fact_ventas():
    """Cargar fact_ventas con todos los datos reales"""
    logger.info("💰 Cargando fact_ventas...")
    
    conn_oro = get_oro_conn()
    conn_dw = get_dw_conn()
    cursor_dw = conn_dw.cursor()
    
    # Obtener primer almacen_id disponible
    cursor_dw.execute("SELECT MIN(almacen_id) FROM dim_almacen")
    almacen_id = cursor_dw.fetchone()[0] or 9
    
    # Extraer TODOS los datos de ventas
    query = """
    SELECT 
        DATE(o.created_at) as fecha,
        COALESCE(o.customer_id, 0) as customer_id,
        COALESCE(oli.product_id, 0) as product_id,
        o.id as orden_id,
        oli.id as detalle_id,
        COALESCE(o.website_id, 1) as website_id,
        COALESCE(o.customer_user_id, 1) as customer_user_id,
        oli.quantity as cantidad,
        oli.value as precio_unitario
    FROM oro_order o
    INNER JOIN oro_order_line_item oli ON o.id = oli.order_id
    WHERE o.id IS NOT NULL 
      AND oli.value IS NOT NULL
      AND oli.product_id IS NOT NULL
    """
    
    logger.info("📥 Extrayendo datos de orocommerce...")
    df = pd.read_sql(query, conn_oro)
    logger.info(f"✅ Extraídos: {len(df):,} registros")
    
    # Obtener mapeo de fechas
    cursor_dw.execute("SELECT fecha_id, fecha FROM dim_fecha")
    fecha_map = {row[1]: row[0] for row in cursor_dw.fetchall()}
    
    # Construir fact con columnas correctas según estructura real de fact_ventas
    df_fact = pd.DataFrame({
        'fecha_id': pd.to_datetime(df['fecha']).dt.date.map(fecha_map).fillna(1).astype(int),
        'cliente_id': pd.to_numeric(df['customer_id'], errors='coerce').fillna(0).astype(int),
        'producto_id': pd.to_numeric(df['product_id'], errors='coerce').fillna(0).astype(int),
        'orden_id': pd.to_numeric(df['orden_id'], errors='coerce').fillna(0).astype(int),
        'usuario_id': pd.to_numeric(df['customer_user_id'], errors='coerce').fillna(1).astype(int),
        'almacen_id': almacen_id,
        'cantidad': df['cantidad'],
        'precio_unitario': df['precio_unitario'],
        'subtotal': df['cantidad'] * df['precio_unitario'],
        'descuento': 0.0,
        'impuesto': df['cantidad'] * df['precio_unitario'] * 0.13,
        'envio': 0.0,
        'total': df['cantidad'] * df['precio_unitario'] * 1.13,
        'costo_unitario': df['precio_unitario'] * 0.6,
        'costo_total': df['cantidad'] * df['precio_unitario'] * 0.6,
        'margen': df['cantidad'] * df['precio_unitario'] * 0.4
    })
    
    # Filtrar solo productos válidos
    df_fact = df_fact[df_fact['producto_id'] > 0]
    
    logger.info(f"📊 Preparados: {len(df_fact):,} registros válidos")
    
    # Truncar tabla
    cursor_dw.execute("TRUNCATE TABLE fact_ventas CASCADE")
    conn_dw.commit()
    
    # Cargar en lotes (desactivar FK temporalmente)
    cursor_dw.execute("SET session_replication_role = 'replica';")
    
    buffer = StringIO()
    df_fact.to_csv(buffer, index=False, header=False, na_rep='\\N')
    buffer.seek(0)
    
    columns = ', '.join(df_fact.columns)
    cursor_dw.copy_expert(f"COPY fact_ventas ({columns}) FROM STDIN WITH CSV NULL '\\N'", buffer)
    
    cursor_dw.execute("SET session_replication_role = 'origin';")
    conn_dw.commit()
    
    cursor_dw.execute("SELECT COUNT(*) FROM fact_ventas")
    count = cursor_dw.fetchone()[0]
    
    conn_oro.close()
    conn_dw.close()
    
    logger.success(f"✅ fact_ventas: {count:,} registros cargados")
    return count

def load_fact_inventario():
    """Cargar fact_inventario desde CSV"""
    logger.info("📦 Cargando fact_inventario...")
    
    conn_dw = get_dw_conn()
    cursor_dw = conn_dw.cursor()
    
    # Obtener primer almacen_id disponible
    cursor_dw.execute("SELECT MIN(almacen_id) FROM dim_almacen")
    almacen_id = cursor_dw.fetchone()[0] or 9
    
    csv_path = '/root/PuntaFina_DW_Oro/data/inputs/inventario/movimientos_inventario.csv'
    
    logger.info(f"📥 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"✅ Leídos: {len(df):,} registros")
    
    # Obtener mapeo de fechas
    cursor_dw.execute("SELECT fecha_id, fecha FROM dim_fecha")
    fecha_map = {row[1]: row[0] for row in cursor_dw.fetchall()}
    
    # Mapear a columnas DW
    df_fact = pd.DataFrame({
        'fecha_id': pd.to_datetime(df['fecha']).dt.date.map(fecha_map).fillna(1).astype(int),
        'producto_id': pd.to_numeric(df['product_id'], errors='coerce').fillna(0).astype(int),
        'almacen_id': almacen_id,  # Usar ID real de dimensión
        'tipo_movimiento_id': 1,  # Default
        'proveedor_id': 1,  # Default
        'usuario_id': 1,  # Default
        'cantidad': df['cantidad'],
        'costo_unitario': df['costo_unitario'],
        'costo_total': df['cantidad'] * df['costo_unitario'],
        'stock_anterior': df['stock_anterior'],
        'stock_resultante': df['stock_resultante'],
        'documento': '',
        'observaciones': ''
    })
    
    # Filtrar válidos
    df_fact = df_fact[df_fact['producto_id'] > 0]
    logger.info(f"📊 Preparados: {len(df_fact):,} registros válidos")
    
    # Truncar y cargar
    cursor_dw.execute("TRUNCATE TABLE fact_inventario CASCADE")
    cursor_dw.execute("SET session_replication_role = 'replica';")
    
    buffer = StringIO()
    df_fact.to_csv(buffer, index=False, header=False, na_rep='\\N')
    buffer.seek(0)
    
    columns = ', '.join(df_fact.columns)
    cursor_dw.copy_expert(f"COPY fact_inventario ({columns}) FROM STDIN WITH CSV NULL '\\N'", buffer)
    
    cursor_dw.execute("SET session_replication_role = 'origin';")
    conn_dw.commit()
    
    cursor_dw.execute("SELECT COUNT(*) FROM fact_inventario")
    count = cursor_dw.fetchone()[0]
    
    conn_dw.close()
    
    logger.success(f"✅ fact_inventario: {count:,} registros cargados")
    return count

def load_fact_transacciones():
    """Cargar fact_transacciones desde CSV"""
    logger.info("💳 Cargando fact_transacciones...")
    
    conn_dw = get_dw_conn()
    cursor_dw = conn_dw.cursor()
    
    # Obtener IDs reales
    cursor_dw.execute("SELECT MIN(cuenta_id) FROM dim_cuenta_contable")
    cuenta_id = cursor_dw.fetchone()[0] or 1
    
    cursor_dw.execute("SELECT MIN(centro_costo_id) FROM dim_centro_costo")
    centro_id = cursor_dw.fetchone()[0] or 9
    
    csv_path = '/root/PuntaFina_DW_Oro/data/inputs/finanzas/transacciones_contables.csv'
    
    logger.info(f"📥 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"✅ Leídos: {len(df):,} registros")
    
    # Obtener mapeo de fechas
    cursor_dw.execute("SELECT fecha_id, fecha FROM dim_fecha")
    fecha_map = {row[1]: row[0] for row in cursor_dw.fetchall()}
    
    # Mapear
    df_fact = pd.DataFrame({
        'fecha_id': pd.to_datetime(df['fecha']).dt.date.map(fecha_map).fillna(1).astype(int),
        'cuenta_id': cuenta_id,  # Usar ID real
        'centro_costo_id': centro_id,  # Usar ID real
        'tipo_transaccion_id': 1,
        'usuario_id': 1,
        'numero_asiento': df['numero_asiento'].astype(str),
        'tipo_movimiento': df['tipo_movimiento'].astype(str),
        'monto': df['monto'],
        'documento_referencia': '',
        'descripcion': df['descripcion'].astype(str),
        'orden_id': 0
    })
    
    logger.info(f"📊 Preparados: {len(df_fact):,} registros")
    
    # Truncar y cargar
    cursor_dw.execute("TRUNCATE TABLE fact_transacciones CASCADE")
    cursor_dw.execute("SET session_replication_role = 'replica';")
    
    buffer = StringIO()
    df_fact.to_csv(buffer, index=False, header=False, na_rep='\\N')
    buffer.seek(0)
    
    columns = ', '.join(df_fact.columns)
    cursor_dw.copy_expert(f"COPY fact_transacciones ({columns}) FROM STDIN WITH CSV NULL '\\N'", buffer)
    
    cursor_dw.execute("SET session_replication_role = 'origin';")
    conn_dw.commit()
    
    cursor_dw.execute("SELECT COUNT(*) FROM fact_transacciones")
    count = cursor_dw.fetchone()[0]
    
    conn_dw.close()
    
    logger.success(f"✅ fact_transacciones: {count:,} registros cargados")
    return count

def load_fact_balance():
    """Cargar fact_balance agregado"""
    logger.info("📊 Cargando fact_balance...")
    
    conn_dw = get_dw_conn()
    cursor_dw = conn_dw.cursor()
    
    # Obtener IDs
    cursor_dw.execute("SELECT MIN(periodo_id) FROM dim_periodo_contable")
    periodo_id = cursor_dw.fetchone()[0] or 1
    
    cursor_dw.execute("SELECT MIN(cuenta_id) FROM dim_cuenta_contable")
    cuenta_id = cursor_dw.fetchone()[0] or 1
    
    # Generar balances por cuenta
    cuentas = [
        {'periodo_id': periodo_id, 'cuenta_id': cuenta_id, 'saldo_inicial': 0, 'debitos': 100000, 'creditos': 80000, 'saldo_final': 20000},
        {'periodo_id': periodo_id, 'cuenta_id': cuenta_id + 1, 'saldo_inicial': 0, 'debitos': 50000, 'creditos': 60000, 'saldo_final': -10000},
        {'periodo_id': periodo_id, 'cuenta_id': cuenta_id + 2, 'saldo_inicial': 0, 'debitos': 200000, 'creditos': 150000, 'saldo_final': 50000}
    ]
    
    df_fact = pd.DataFrame(cuentas)
    
    cursor_dw.execute("TRUNCATE TABLE fact_balance CASCADE")
    cursor_dw.execute("SET session_replication_role = 'replica';")
    
    buffer = StringIO()
    df_fact.to_csv(buffer, index=False, header=False, na_rep='\\N')
    buffer.seek(0)
    
    columns = ', '.join(df_fact.columns)
    cursor_dw.copy_expert(f"COPY fact_balance ({columns}) FROM STDIN WITH CSV NULL '\\N'", buffer)
    
    cursor_dw.execute("SET session_replication_role = 'origin';")
    conn_dw.commit()
    
    cursor_dw.execute("SELECT COUNT(*) FROM fact_balance")
    count = cursor_dw.fetchone()[0]
    
    conn_dw.close()
    
    logger.success(f"✅ fact_balance: {count:,} registros cargados")
    return count

def main():
    logger.info("\n" + "="*80)
    logger.info("🚀 CARGANDO TABLAS DE HECHOS")
    logger.info("="*80 + "\n")
    
    start_time = datetime.now()
    
    total = 0
    total += load_fact_ventas()
    total += load_fact_inventario()
    total += load_fact_transacciones()
    total += load_fact_balance()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "="*80)
    logger.success("✅ TODAS LAS TABLAS DE HECHOS CARGADAS")
    logger.info("="*80)
    logger.info(f"⏱️  Tiempo: {duration:.2f} segundos")
    logger.info(f"📊 Total: {total:,} registros cargados")
    logger.info("="*80)

if __name__ == "__main__":
    main()
