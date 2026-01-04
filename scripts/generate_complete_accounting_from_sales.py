#!/usr/bin/env python3
"""
Generar transacciones contables COMPLETAS desde las ventas de OroCommerce
Mantiene simetría total: cada venta genera asientos contables con cuentas de resultados
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno
env_path = project_root / '.env'
load_dotenv(env_path)

print("=" * 80)
print("🔄 GENERANDO TRANSACCIONES CONTABLES COMPLETAS DESDE OROCOMMERCE")
print("=" * 80)

# Conectar a OroCommerce
print("\n📊 Conectando a OroCommerce...")
oro_conn = psycopg2.connect(
    host=os.getenv('ORO_DB_HOST', 'localhost'),
    port=os.getenv('ORO_DB_PORT', 5432),
    database=os.getenv('ORO_DB_NAME', 'orocommerce'),
    user=os.getenv('ORO_DB_USER', 'sa'),
    password=os.getenv('ORO_DB_PASS', 'IngDatos123*')
)

# Extraer ventas reales con detalles
query = """
SELECT 
    o.id as orden_id,
    o.created_at::date as fecha,
    oli.id as line_item_id,
    oli.product_id,
    oli.quantity as cantidad,
    oli.value as precio_unitario,
    (oli.quantity * oli.value) as subtotal,
    o.currency
FROM oro_order o
INNER JOIN oro_order_line_item oli ON o.id = oli.order_id
WHERE o.created_at >= '2023-01-01'
  AND oli.quantity > 0
  AND oli.value > 0
ORDER BY o.created_at, o.id, oli.id
"""

print("📥 Extrayendo ventas de OroCommerce...")
df_ventas = pd.read_sql_query(query, oro_conn)
oro_conn.close()

print(f"✓ {len(df_ventas):,} líneas de venta extraídas")
print(f"  Órdenes únicas: {df_ventas['orden_id'].nunique():,}")
print(f"  Rango fechas: {df_ventas['fecha'].min()} a {df_ventas['fecha'].max()}")
print(f"  Total ventas: ${df_ventas['subtotal'].sum():,.2f}")

# Cargar plan de cuentas
cuentas_csv = project_root / 'data' / 'inputs' / 'finanzas' / 'cuentas_contables.csv'
df_cuentas = pd.read_csv(cuentas_csv)

# Mapear cuentas por nombre para referencias rápidas
cuentas_map = {
    'bancos': df_cuentas[df_cuentas['nombre_cuenta'] == 'Bancos'].iloc[0]['id_cuenta'],
    'cuentas_cobrar': df_cuentas[df_cuentas['nombre_cuenta'] == 'Cuentas por Cobrar Clientes'].iloc[0]['id_cuenta'],
    'ventas': df_cuentas[df_cuentas['nombre_cuenta'] == 'Ventas'].iloc[0]['id_cuenta'],
    'iva_cobrado': df_cuentas[df_cuentas['nombre_cuenta'] == 'IVA por Pagar'].iloc[0]['id_cuenta'],
    'costo_ventas': df_cuentas[df_cuentas['nombre_cuenta'] == 'Costo de Mercadería Vendida'].iloc[0]['id_cuenta'],
    'inventario': df_cuentas[df_cuentas['nombre_cuenta'] == 'Inventario de Mercadería'].iloc[0]['id_cuenta'],
}

print("\n🧾 Cuentas a utilizar:")
for nombre, cuenta_id in cuentas_map.items():
    cuenta = df_cuentas[df_cuentas['id_cuenta'] == cuenta_id].iloc[0]
    print(f"  {nombre:20} → {cuenta_id} ({cuenta['nombre_cuenta']})")

# Generar transacciones contables por cada venta
print("\n💼 Generando asientos contables...")

transacciones = []
asiento_num = 1

for idx, venta in df_ventas.iterrows():
    orden_id = venta['orden_id']
    fecha = venta['fecha']
    subtotal = venta['subtotal']
    iva = subtotal * 0.13  # IVA 13%
    total = subtotal + iva
    costo = subtotal * 0.60  # Costo 60% del precio
    
    asiento = f"AST-{asiento_num:08d}"
    
    # 1. Débito: Cuentas por Cobrar (o Bancos si es al contado)
    # Asumimos 70% al contado, 30% a crédito
    if idx % 10 < 7:  # 70% al contado
        cuenta_debito = cuentas_map['bancos']
        desc_debito = f"Cobro venta orden ORD-{orden_id:08d}"
    else:  # 30% a crédito
        cuenta_debito = cuentas_map['cuentas_cobrar']
        desc_debito = f"Venta a crédito orden ORD-{orden_id:08d}"
    
    transacciones.append({
        'id': len(transacciones) + 1,
        'numero_asiento': asiento,
        'fecha': fecha,
        'cuenta_id': cuenta_debito,
        'centro_costo_id': 'CC001',  # Centro de costo por defecto
        'tipo_transaccion_id': 1,  # Venta
        'tipo_movimiento': 'debe',
        'monto': total,
        'documento_referencia': f'ORD-{orden_id:08d}',
        'descripcion': desc_debito,
        'orden_id': orden_id,
        'observaciones': f'Línea de pedido {venta["line_item_id"]}'
    })
    
    # 2. Crédito: Ingresos por Ventas
    transacciones.append({
        'id': len(transacciones) + 1,
        'numero_asiento': asiento,
        'fecha': fecha,
        'cuenta_id': cuentas_map['ventas'],
        'centro_costo_id': 'CC001',
        'tipo_transaccion_id': 1,
        'tipo_movimiento': 'haber',
        'monto': subtotal,
        'documento_referencia': f'ORD-{orden_id:08d}',
        'descripcion': f'Ingreso por venta orden ORD-{orden_id:08d}',
        'orden_id': orden_id,
        'observaciones': f'Producto {venta["product_id"]}, cantidad {venta["cantidad"]}'
    })
    
    # 3. Crédito: IVA por Pagar
    transacciones.append({
        'id': len(transacciones) + 1,
        'numero_asiento': asiento,
        'fecha': fecha,
        'cuenta_id': cuentas_map['iva_cobrado'],
        'centro_costo_id': 'CC001',
        'tipo_transaccion_id': 1,
        'tipo_movimiento': 'haber',
        'monto': iva,
        'documento_referencia': f'ORD-{orden_id:08d}',
        'descripcion': f'IVA cobrado orden ORD-{orden_id:08d}',
        'orden_id': orden_id,
        'observaciones': 'IVA 13%'
    })
    
    # 4. Débito: Costo de Ventas
    transacciones.append({
        'id': len(transacciones) + 1,
        'numero_asiento': asiento,
        'fecha': fecha,
        'cuenta_id': cuentas_map['costo_ventas'],
        'centro_costo_id': 'CC001',
        'tipo_transaccion_id': 1,
        'tipo_movimiento': 'debe',
        'monto': costo,
        'documento_referencia': f'ORD-{orden_id:08d}',
        'descripcion': f'Costo de ventas orden ORD-{orden_id:08d}',
        'orden_id': orden_id,
        'observaciones': f'Costo unitario estimado'
    })
    
    # 5. Crédito: Inventario
    transacciones.append({
        'id': len(transacciones) + 1,
        'numero_asiento': asiento,
        'fecha': fecha,
        'cuenta_id': cuentas_map['inventario'],
        'centro_costo_id': 'CC001',
        'tipo_transaccion_id': 1,
        'tipo_movimiento': 'haber',
        'monto': costo,
        'documento_referencia': f'ORD-{orden_id:08d}',
        'descripcion': f'Salida inventario orden ORD-{orden_id:08d}',
        'orden_id': orden_id,
        'observaciones': f'Producto {venta["product_id"]}'
    })
    
    asiento_num += 1
    
    if (idx + 1) % 10000 == 0:
        print(f"  Procesadas {idx + 1:,} líneas de venta...")

# Crear DataFrame
df_transacciones = pd.DataFrame(transacciones)

print(f"\n✓ Generadas {len(df_transacciones):,} transacciones contables")
print(f"  Asientos contables: {asiento_num - 1:,}")
print(f"  Movimientos debe: {len(df_transacciones[df_transacciones['tipo_movimiento']=='debe']):,}")
print(f"  Movimientos haber: {len(df_transacciones[df_transacciones['tipo_movimiento']=='haber']):,}")

# Verificar balance (debe = haber)
total_debe = df_transacciones[df_transacciones['tipo_movimiento']=='debe']['monto'].sum()
total_haber = df_transacciones[df_transacciones['tipo_movimiento']=='haber']['monto'].sum()
print(f"\n📊 Balance:")
print(f"  Total Debe:  ${total_debe:,.2f}")
print(f"  Total Haber: ${total_haber:,.2f}")
print(f"  Diferencia:  ${abs(total_debe - total_haber):,.2f}")

if abs(total_debe - total_haber) < 0.01:
    print("  ✅ Balance cuadrado")
else:
    print("  ⚠️  Balance no cuadra!")

# Mostrar resumen por cuenta
print("\n📋 Resumen por cuenta:")
resumen = df_transacciones.groupby(['cuenta_id', 'tipo_movimiento'])['monto'].agg(['count', 'sum']).round(2)
print(resumen)

# Guardar CSV
output_path = project_root / 'data' / 'inputs' / 'finanzas' / 'transacciones_contables.csv'
df_transacciones.to_csv(output_path, index=False)
print(f"\n💾 Guardado: {output_path}")
print(f"   {len(df_transacciones):,} transacciones")

# Hacer backup del anterior si existe
backup_path = project_root / 'data' / 'inputs' / 'finanzas' / f'transacciones_contables_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
if output_path.exists():
    import shutil
    shutil.copy2(output_path, backup_path)
    print(f"   Backup guardado: {backup_path.name}")

print("\n" + "=" * 80)
print("✅ TRANSACCIONES CONTABLES COMPLETAS GENERADAS")
print("=" * 80)
print("\n💡 Próximos pasos:")
print("   1. Ejecutar ETL completo: python scripts/run_complete_etl.py")
print("   2. Verificar fact_transacciones: ~577,640 registros esperados (115,528 ventas × 5 asientos)")
print("   3. Verificar fact_estado_resultados: debe tener datos de ingresos, costos y utilidades")
print("=" * 80)
