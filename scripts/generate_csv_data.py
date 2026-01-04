#!/usr/bin/env python3
"""
Script para generar archivos CSV con datos coherentes desde OroCommerce y OroCRM
"""
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'orocommerce',
    'user': 'sa',
    'password': 'IngDatos123*'
}

OUTPUT_DIR = '/root/PuntaFina_DW_Oro/data/inputs'

def get_connection():
    """Crear conexión a PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def generate_inventory_movements():
    """Generar movimientos de inventario basados en órdenes reales"""
    print("📦 Generando movimientos de inventario...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener productos y órdenes
    cursor.execute("""
        SELECT 
            p.id as product_id,
            p.sku,
            p.name,
            oli.quantity,
            oli.value as price,
            o.id as order_id,
            o.created_at,
            o.internal_status_id
        FROM oro_order o
        JOIN oro_order_line_item oli ON o.id = oli.order_id
        JOIN oro_product p ON oli.product_id = p.id
        WHERE o.created_at >= '2020-01-01'
        ORDER BY o.created_at
        LIMIT 50000
    """)
    
    orders = cursor.fetchall()
    
    movements = []
    almacenes = ['ALM001', 'ALM002', 'ALM003', 'ALM004', 'ALM005', 'ALM006']
    proveedores = ['PROV001', 'PROV002', 'PROV003', 'PROV004', 'PROV005', 'PROV006', 'PROV007', 'PROV008']
    tipos_entrada = ['ENTRADA_COMPRA', 'AJUSTE_POSITIVO', 'DEVOLUCION_CLIENTE', 'TRANSFERENCIA_ENTRADA']
    tipos_salida = ['SALIDA_VENTA', 'AJUSTE_NEGATIVO', 'DEVOLUCION_PROVEEDOR', 'TRANSFERENCIA_SALIDA']
    
    movement_id = 1
    product_stock = {}  # Mantener track del stock por producto y almacén
    
    for order in orders:
        product_id, sku, name, quantity, price, order_id, created_at, status = order
        
        # Inicializar stock si es primera vez que vemos el producto
        if product_id not in product_stock:
            product_stock[product_id] = {}
            # Crear entrada inicial de compra para cada almacén
            for almacen in almacenes[:3]:  # Solo 3 almacenes principales
                fecha_compra = created_at - timedelta(days=random.randint(30, 90))
                cantidad_compra = random.randint(500, 2000)
                costo_unitario = float(price) * 0.6 if price else 50.0  # 60% del precio de venta
                proveedor = random.choice(proveedores)
                
                movements.append({
                    'id': movement_id,
                    'product_id': product_id,
                    'sku': sku,
                    'product_name': name,
                    'almacen_id': almacen,
                    'proveedor_id': proveedor,
                    'tipo_movimiento_id': 'ENTRADA_COMPRA',
                    'fecha': fecha_compra.strftime('%Y-%m-%d'),
                    'cantidad': cantidad_compra,
                    'costo_unitario': round(costo_unitario, 2),
                    'costo_total': round(cantidad_compra * costo_unitario, 2),
                    'stock_anterior': 0,
                    'stock_resultante': cantidad_compra,
                    'documento': f'COMP-{movement_id:06d}',
                    'observaciones': f'Compra inicial de {name}'
                })
                
                product_stock[product_id][almacen] = cantidad_compra
                movement_id += 1
        
        # Crear movimiento de salida por venta
        almacen = random.choice(list(product_stock[product_id].keys()))
        stock_anterior = product_stock[product_id].get(almacen, 0)
        
        # Si no hay suficiente stock, hacer una entrada primero
        if stock_anterior < quantity:
            cantidad_entrada = max(quantity * 10, 100)
            costo_unitario = float(price) * 0.6 if price else 50.0
            fecha_entrada = created_at - timedelta(days=random.randint(5, 15))
            
            movements.append({
                'id': movement_id,
                'product_id': product_id,
                'sku': sku,
                'product_name': name,
                'almacen_id': almacen,
                'proveedor_id': random.choice(proveedores),
                'tipo_movimiento_id': 'ENTRADA_COMPRA',
                'fecha': fecha_entrada.strftime('%Y-%m-%d'),
                'cantidad': cantidad_entrada,
                'costo_unitario': round(costo_unitario, 2),
                'costo_total': round(cantidad_entrada * costo_unitario, 2),
                'stock_anterior': stock_anterior,
                'stock_resultante': stock_anterior + cantidad_entrada,
                'documento': f'COMP-{movement_id:06d}',
                'observaciones': f'Reabastecimiento de {name}'
            })
            
            product_stock[product_id][almacen] = stock_anterior + cantidad_entrada
            stock_anterior = product_stock[product_id][almacen]
            movement_id += 1
        
        # Crear salida por venta
        costo_unitario = float(price) * 0.6 if price else 50.0
        stock_resultante = stock_anterior - quantity
        
        movements.append({
            'id': movement_id,
            'product_id': product_id,
            'sku': sku,
            'product_name': name,
            'almacen_id': almacen,
            'proveedor_id': None,
            'tipo_movimiento_id': 'SALIDA_VENTA',
            'fecha': created_at.strftime('%Y-%m-%d'),
            'cantidad': quantity,
            'costo_unitario': round(costo_unitario, 2),
            'costo_total': round(quantity * costo_unitario, 2),
            'stock_anterior': stock_anterior,
            'stock_resultante': stock_resultante,
            'documento': f'ORDEN-{order_id}',
            'observaciones': f'Venta orden #{order_id}'
        })
        
        product_stock[product_id][almacen] = stock_resultante
        movement_id += 1
    
    # Crear DataFrame y guardar
    df = pd.DataFrame(movements)
    output_file = f'{OUTPUT_DIR}/inventario/movimientos_inventario.csv'
    df.to_csv(output_file, index=False)
    print(f"✓ Generados {len(movements):,} movimientos de inventario en {output_file}")
    
    cursor.close()
    conn.close()
    
    return len(movements)

def generate_accounting_transactions():
    """Generar transacciones contables basadas en órdenes reales"""
    print("💰 Generando transacciones contables...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener órdenes con sus totales
    cursor.execute("""
        SELECT 
            o.id,
            o.identifier,
            o.created_at,
            o.subtotal_value as subtotal,
            o.total_value as total,
            o.currency,
            o.internal_status_id,
            o.customer_id
        FROM oro_order o
        WHERE o.created_at >= '2020-01-01'
        AND o.total_value > 0
        ORDER BY o.created_at
        LIMIT 30000
    """)
    
    orders = cursor.fetchall()
    
    transactions = []
    asiento_id = 1
    centros_costo = ['CC001', 'CC002', 'CC003', 'CC004', 'CC005']
    
    for order in orders:
        order_id, identifier, created_at, subtotal, total, currency, status, customer_id = order
        
        # Convertir a float
        subtotal = float(subtotal) if subtotal else 0
        total = float(total) if total else 0
        iva = total - subtotal
        costo_ventas = subtotal * 0.6  # Aproximadamente 60% del subtotal
        
        if total <= 0:
            continue
        
        fecha = created_at.strftime('%Y-%m-%d')
        centro_costo = random.choice(centros_costo)
        doc_ref = identifier or f'ORD-{order_id}'
        
        # Asiento de venta (reconocimiento de ingreso)
        # Débito: Clientes (1120)
        transactions.append({
            'id': len(transactions) + 1,
            'numero_asiento': f'AST-{asiento_id:08d}',
            'fecha': fecha,
            'cuenta_id': 4,  # 1120 - CLIENTES
            'centro_costo_id': centro_costo,
            'tipo_transaccion_id': 1,  # VENTA
            'tipo_movimiento': 'debe',
            'monto': round(total, 2),
            'documento_referencia': doc_ref,
            'descripcion': f'Venta orden {doc_ref}',
            'orden_id': order_id,
            'observaciones': f'Cliente {customer_id}'
        })
        
        # Crédito: Ventas (4100)
        transactions.append({
            'id': len(transactions) + 1,
            'numero_asiento': f'AST-{asiento_id:08d}',
            'fecha': fecha,
            'cuenta_id': 17,  # 4100 - VENTAS
            'centro_costo_id': centro_costo,
            'tipo_transaccion_id': 1,  # VENTA
            'tipo_movimiento': 'haber',
            'monto': round(subtotal, 2),
            'documento_referencia': doc_ref,
            'descripcion': f'Ingreso por venta {doc_ref}',
            'orden_id': order_id,
            'observaciones': 'Ingreso por ventas'
        })
        
        # Crédito: IVA por pagar (si hay IVA)
        if iva > 0:
            transactions.append({
                'id': len(transactions) + 1,
                'numero_asiento': f'AST-{asiento_id:08d}',
                'fecha': fecha,
                'cuenta_id': 12,  # 2120 - ACREEDORES (IVA por pagar)
                'centro_costo_id': centro_costo,
                'tipo_transaccion_id': 1,  # VENTA
                'tipo_movimiento': 'haber',
                'monto': round(iva, 2),
                'documento_referencia': doc_ref,
                'descripcion': f'IVA cobrado {doc_ref}',
                'orden_id': order_id,
                'observaciones': 'IVA por pagar'
            })
        
        asiento_id += 1
        
        # Asiento de costo de ventas
        # Débito: Costo de Ventas (5100)
        transactions.append({
            'id': len(transactions) + 1,
            'numero_asiento': f'AST-{asiento_id:08d}',
            'fecha': fecha,
            'cuenta_id': 20,  # 5100 - COSTO DE VENTAS
            'centro_costo_id': centro_costo,
            'tipo_transaccion_id': 1,  # VENTA
            'tipo_movimiento': 'debe',
            'monto': round(costo_ventas, 2),
            'documento_referencia': doc_ref,
            'descripcion': f'Costo de ventas {doc_ref}',
            'orden_id': order_id,
            'observaciones': 'Costo de mercancía vendida'
        })
        
        # Crédito: Inventarios (1130)
        transactions.append({
            'id': len(transactions) + 1,
            'numero_asiento': f'AST-{asiento_id:08d}',
            'fecha': fecha,
            'cuenta_id': 5,  # 1130 - INVENTARIOS
            'centro_costo_id': centro_costo,
            'tipo_transaccion_id': 1,  # VENTA
            'tipo_movimiento': 'haber',
            'monto': round(costo_ventas, 2),
            'documento_referencia': doc_ref,
            'descripcion': f'Salida de inventario {doc_ref}',
            'orden_id': order_id,
            'observaciones': 'Reducción de inventario'
        })
        
        asiento_id += 1
        
        # Si la orden está pagada, crear asiento de cobro
        if status in ['closed', 'shipped']:
            # Débito: Bancos (1110)
            transactions.append({
                'id': len(transactions) + 1,
                'numero_asiento': f'AST-{asiento_id:08d}',
                'fecha': (created_at + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
                'cuenta_id': 3,  # 1110 - BANCOS
                'centro_costo_id': centro_costo,
                'tipo_transaccion_id': 4,  # COBRO_CLIENTE
                'tipo_movimiento': 'debe',
                'monto': round(total, 2),
                'documento_referencia': f'PAG-{doc_ref}',
                'descripcion': f'Cobro orden {doc_ref}',
                'orden_id': order_id,
                'observaciones': 'Depósito bancario'
            })
            
            # Crédito: Clientes (1120)
            transactions.append({
                'id': len(transactions) + 1,
                'numero_asiento': f'AST-{asiento_id:08d}',
                'fecha': (created_at + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
                'cuenta_id': 4,  # 1120 - CLIENTES
                'centro_costo_id': centro_costo,
                'tipo_transaccion_id': 4,  # COBRO_CLIENTE
                'tipo_movimiento': 'haber',
                'monto': round(total, 2),
                'documento_referencia': f'PAG-{doc_ref}',
                'descripcion': f'Cobro orden {doc_ref}',
                'orden_id': order_id,
                'observaciones': 'Cancelación de cuenta por cobrar'
            })
            
            asiento_id += 1
    
    # Crear DataFrame y guardar
    df = pd.DataFrame(transactions)
    output_file = f'{OUTPUT_DIR}/finanzas/transacciones_contables.csv'
    df.to_csv(output_file, index=False)
    print(f"✓ Generadas {len(transactions):,} transacciones contables en {output_file}")
    
    cursor.close()
    conn.close()
    
    return len(transactions)

def main():
    """Función principal"""
    print("=" * 80)
    print("🏪 GENERADOR DE DATOS CSV COHERENTES - PUNTAFINA")
    print("=" * 80)
    print()
    
    try:
        # Crear directorios si no existen
        os.makedirs(f'{OUTPUT_DIR}/inventario', exist_ok=True)
        os.makedirs(f'{OUTPUT_DIR}/finanzas', exist_ok=True)
        
        # Generar datos
        inv_count = generate_inventory_movements()
        acc_count = generate_accounting_transactions()
        
        print()
        print("=" * 80)
        print("✅ GENERACIÓN COMPLETADA")
        print("=" * 80)
        print(f"📦 Movimientos de inventario: {inv_count:,}")
        print(f"💰 Transacciones contables: {acc_count:,}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
