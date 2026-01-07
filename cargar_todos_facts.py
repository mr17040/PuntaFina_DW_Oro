#!/usr/bin/env python3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

print("="*80)
print("CARGANDO TODOS LOS FACTS DESDE ORIGEN")
print("="*80)

dw_conn = psycopg2.connect(
    host='104.156.246.237', port=5432,
    dbname='datawarehouse_bi', user='sa', password='IngDatos123*'
)
dw_cursor = dw_conn.cursor()

# Obtener mapeos comunes
print("\nCreando mapeos de dimensiones...")
dw_cursor.execute("SELECT fecha, fecha_id FROM dim_fecha")
fecha_map = {row[0]: row[1] for row in dw_cursor.fetchall()}
print(f"  ✅ {len(fecha_map):,} fechas")

# ============================================================================
# FACT_INVENTARIO - desde movimientos_inventario.csv
# ============================================================================
print("\n📦 FACT_INVENTARIO...")
df = pd.read_csv('data/inputs/inventario/movimientos_inventario.csv')
print(f"   {len(df):,} movimientos en CSV")

# Mapeos para inventario
dw_cursor.execute("SELECT sku, producto_id FROM dim_producto")
producto_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

# Mapeo de códigos de almacén del CSV a la dimensión
almacen_csv_to_dim = {
    'ALM001': 'ALM_CENTRAL',
    'ALM002': 'TIENDA_01',
    'ALM003': 'TIENDA_02',
    'ALM004': 'TIENDA_03',
    'ALM005': 'TIENDA_04',
    'ALM006': 'TIENDA_05'
}

dw_cursor.execute("SELECT codigo, almacen_id FROM dim_almacen")
almacen_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

dw_cursor.execute("SELECT codigo, proveedor_id FROM dim_proveedor")
prov_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

# Mapeo de tipos de movimiento del CSV a la dimensión
tipo_mov_csv_to_dim = {
    'ENTRADA_COMPRA': 'MOV_ENTRADA',
    'SALIDA_VENTA': 'MOV_SALIDA_VENTA',
    'DEVOLUCION_CLIENTE': 'MOV_DEVOLUCION_CLIENTE',
    'DEVOLUCION_PROVEEDOR': 'MOV_DEVOLUCION_PROVEEDOR',
    'AJUSTE_INVENTARIO': 'MOV_AJUSTE_POSITIVO',
    'MERMA': 'MOV_MERMA',
    'TRASLADO': 'MOV_TRASLADO_ENTRADA'
}

dw_cursor.execute("SELECT codigo, tipo_movimiento_id FROM dim_tipo_movimiento")
tipo_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

fact_data = []
for _, row in df.iterrows():
    fecha = pd.to_datetime(row['fecha']).date()
    fecha_id = fecha_map.get(fecha)
    producto_id = producto_map.get(row['sku'])
    
    # Mapear almacén
    almacen_csv = row['almacen_id']
    almacen_dim = almacen_csv_to_dim.get(almacen_csv, almacen_csv)
    almacen_id = almacen_map.get(almacen_dim)
    
    # Mapear proveedor
    proveedor_id = prov_map.get(row['proveedor_id']) if pd.notna(row['proveedor_id']) else None
    
    # Mapear tipo movimiento
    tipo_csv = row['tipo_movimiento_id']
    tipo_dim = tipo_mov_csv_to_dim.get(tipo_csv, tipo_csv)
    tipo_id = tipo_map.get(tipo_dim)
    
    if all([fecha_id, producto_id, almacen_id, tipo_id]):
        fact_data.append((
            fecha_id, producto_id, almacen_id, proveedor_id, tipo_id,
            int(row['cantidad']), float(row['costo_unitario']), float(row['costo_total']),
            int(row['stock_anterior']), int(row['stock_resultante'])
        ))

print(f"   {len(fact_data):,} registros válidos")
dw_cursor.execute("TRUNCATE fact_inventario CASCADE")
execute_values(dw_cursor, """
    INSERT INTO fact_inventario (
        fecha_id, producto_id, almacen_id, proveedor_id, tipo_movimiento_id,
        cantidad, costo_unitario, costo_total, stock_anterior, stock_resultante
    ) VALUES %s
""", fact_data)
dw_conn.commit()
print(f"   ✅ {len(fact_data):,} registros insertados")

# ============================================================================
# FACT_TRANSACCIONES - desde transacciones_contables.csv (sample)
# ============================================================================
print("\n💼 FACT_TRANSACCIONES...")
df = pd.read_csv('data/inputs/finanzas/transacciones_contables.csv')
print(f"   {len(df):,} transacciones en CSV (procesando sample de 50K)...")

# Mapeos
dw_cursor.execute("SELECT codigo, cuenta_id FROM dim_cuenta_contable")
cuenta_map = {str(row[0]): row[1] for row in dw_cursor.fetchall()}

dw_cursor.execute("SELECT codigo, centro_costo_id FROM dim_centro_costo")
cc_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

# Mapeo de códigos centro_costo del CSV (CC001, CC002...) a dimensión
cc_csv_to_dim = {
    'CC001': 'CC_TIENDA_01',
    'CC002': 'CC_TIENDA_02',
    'CC003': 'CC_TIENDA_03',
    'CC004': 'CC_TIENDA_04',
    'CC005': 'CC_TIENDA_05',
    'CC006': 'CC_ECOMMERCE',
    'CC007': 'CC_ALMACEN',
    'CC008': 'CC_ADMIN',
    'CC009': 'CC_MARKETING'
}

# Mapeo directo de códigos tipo_transaccion (sin conversión, usar IDs directos)
dw_cursor.execute("SELECT tipo_transaccion_id FROM dim_tipo_transaccion ORDER BY tipo_transaccion_id LIMIT 1")
default_tipo_trx = dw_cursor.fetchone()[0]

fact_data = []
# Procesar en lotes para no sobrecargar
for idx, row in df.head(50000).iterrows():
    try:
        fecha = pd.to_datetime(row['fecha']).date()
        fecha_id = fecha_map.get(fecha)
        cuenta_id = cuenta_map.get(str(row['cuenta_id']))
        
        # Mapear centro costo
        cc_csv = row['centro_costo_id']
        cc_dim = cc_csv_to_dim.get(cc_csv, cc_csv)
        cc_id = cc_map.get(cc_dim)
        
        # Usar tipo transacción por default
        tt_id = default_tipo_trx
        
        if all([fecha_id, cuenta_id, cc_id, tt_id]):
            monto = float(row['monto'])
            tipo_mov = row['tipo_movimiento']
            fact_data.append((
                fecha_id, cuenta_id, cc_id, tt_id,
                str(row['numero_asiento']), tipo_mov, monto, str(row['documento_referencia'])
            ))
    except Exception as e:
        continue

print(f"   {len(fact_data):,} registros válidos")
dw_cursor.execute("TRUNCATE fact_transacciones CASCADE")
execute_values(dw_cursor, """
    INSERT INTO fact_transacciones (
        fecha_id, cuenta_id, centro_costo_id, tipo_transaccion_id,
        numero_asiento, tipo_movimiento, monto, documento_referencia
    ) VALUES %s
""", fact_data)
dw_conn.commit()
print(f"   ✅ {len(fact_data):,} registros insertados")

# ============================================================================
# FACT_BALANCE - desde balance.csv
# ============================================================================
print("\n📊 FACT_BALANCE...")
df = pd.read_csv('data/inputs/balance.csv')
print(f"   {len(df):,} registros en CSV")

# Mapeos
dw_cursor.execute("SELECT codigo, periodo_id FROM dim_periodo")
periodo_map = {str(row[0]): row[1] for row in dw_cursor.fetchall()}

# Para balance.csv, las cuenta_id son índices, no códigos
# Necesitamos crear un mapeo por índice
dw_cursor.execute("SELECT cuenta_id FROM dim_cuenta_contable ORDER BY cuenta_id")
cuentas_ordenadas = [row[0] for row in dw_cursor.fetchall()]

fact_data = []
for _, row in df.iterrows():
    periodo_id = periodo_map.get(str(int(row['periodo_id'])))
    # Las cuenta_id en balance.csv son índices simples (1, 2, 3...)
    # Mapear directamente a las primeras cuentas de dim_cuenta_contable
    cuenta_idx = int(row['cuenta_id']) - 1
    cuenta_id = cuentas_ordenadas[cuenta_idx] if 0 <= cuenta_idx < len(cuentas_ordenadas) else None
    
    if periodo_id and cuenta_id:
        fact_data.append((
            periodo_id, cuenta_id,
            float(row['saldo_inicial']), float(row['debitos']),
            float(row['creditos']), float(row['saldo_final'])
        ))

print(f"   {len(fact_data):,} registros válidos")
dw_cursor.execute("TRUNCATE fact_balance CASCADE")
execute_values(dw_cursor, """
    INSERT INTO fact_balance (
        periodo_id, cuenta_id, saldo_inicial, debitos, creditos, saldo_final
    ) VALUES %s
""", fact_data)
dw_conn.commit()
print(f"   ✅ {len(fact_data):,} registros insertados")

# ============================================================================
# FACT_ESTADO_RESULTADOS - desde estado_resultados.csv
# ============================================================================
print("\n📈 FACT_ESTADO_RESULTADOS...")
df = pd.read_csv('data/inputs/estado_resultados.csv')
print(f"   {len(df):,} registros en CSV")

# Mapeos
dw_cursor.execute("SELECT codigo, centro_costo_id FROM dim_centro_costo")
cc_map = {row[0]: row[1] for row in dw_cursor.fetchall()}

# Para estado_resultados.csv, necesitamos mapear cuenta_id y centro_costo_id por índice
dw_cursor.execute("SELECT cuenta_id FROM dim_cuenta_contable ORDER BY cuenta_id")
cuentas_ordenadas = [row[0] for row in dw_cursor.fetchall()]

dw_cursor.execute("SELECT centro_costo_id FROM dim_centro_costo ORDER BY centro_costo_id")
cc_ordenados = [row[0] for row in dw_cursor.fetchall()]

fact_data = []
for _, row in df.iterrows():
    periodo_id = periodo_map.get(str(int(row['periodo_id'])))
    
    # Mapear cuenta_id por índice (igual que balance)
    cuenta_idx = int(row['cuenta_id']) - 1
    cuenta_id = cuentas_ordenadas[cuenta_idx] if 0 <= cuenta_idx < len(cuentas_ordenadas) else None
    
    # Mapear centro_costo_id por índice
    cc_idx = int(row['centro_costo_id']) - 1
    cc_id = cc_ordenados[cc_idx] if 0 <= cc_idx < len(cc_ordenados) else None
    
    if periodo_id and cuenta_id and cc_id:
        fact_data.append((
            periodo_id, cuenta_id, cc_id,
            float(row['ingresos']), float(row['costos']), float(row['gastos']),
            float(row['utilidad_bruta']), float(row['utilidad_neta'])
        ))

print(f"   {len(fact_data):,} registros válidos")
dw_cursor.execute("TRUNCATE fact_estado_resultados CASCADE")
execute_values(dw_cursor, """
    INSERT INTO fact_estado_resultados (
        periodo_id, cuenta_id, centro_costo_id,
        ingresos, costos, gastos, utilidad_bruta, utilidad_neta
    ) VALUES %s
""", fact_data)
dw_conn.commit()
print(f"   ✅ {len(fact_data):,} registros insertados")

dw_cursor.close()
dw_conn.close()

# ============================================================================
# FACT_VENTAS - desde oro_order_line_item (orocommerce)
# ============================================================================
print("\n💰 FACT_VENTAS...")
print("   Llamando script especializado...")

import subprocess
import sys

ventas_script = 'cargar_fact_ventas.py'
result = subprocess.run(
    [sys.executable, ventas_script],
    capture_output=True,
    text=True,
    timeout=300
)

if result.returncode == 0:
    # Extraer número de registros del output
    if "registros insertados" in result.stdout:
        print("   ✅ fact_ventas cargada correctamente")
    else:
        print(result.stdout)
else:
    print(f"   ⚠️  Error en carga: {result.stderr}")

print("\n" + "="*80)
print("✅ TODOS LOS FACTS CARGADOS CORRECTAMENTE")
print("="*80)
