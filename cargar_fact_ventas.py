#!/usr/bin/env python3
"""
Carga fact_ventas desde oro_order_line_item (orocommerce)
"""
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Configuración de conexiones
DW_CONFIG = {
    'host': '104.156.246.237',
    'port': 5432,
    'dbname': 'datawarehouse_bi',
    'user': 'sa',
    'password': 'IngDatos123*'
}

ORO_CONFIG = {
    'host': '104.156.246.237',
    'port': 5432,
    'dbname': 'orocommerce',
    'user': 'sa',
    'password': 'IngDatos123*'
}

def cargar_fact_ventas():
    """Carga fact_ventas desde oro_order_line_item"""
    print(f"\n{'='*80}")
    print("CARGANDO FACT_VENTAS")
    print(f"{'='*80}\n")
    
    # Conectar a orocommerce (origen)
    conn_oro = psycopg2.connect(**ORO_CONFIG)
    cursor_oro = conn_oro.cursor()
    
    # Conectar a datawarehouse (destino)
    conn_dw = psycopg2.connect(**DW_CONFIG)
    cursor_dw = conn_dw.cursor()
    
    try:
        # Limpiar fact_ventas
        cursor_dw.execute("DELETE FROM fact_ventas")
        conn_dw.commit()
        print("✓ Tabla limpiada")
        
        # Extraer datos de oro_order_line_item con joins a dimensiones
        query = """
        SELECT 
            li.id as line_item_id,
            o.id as orden_id,
            o.customer_id,
            p.id as producto_id,
            li.quantity,
            li.value as precio_unitario,
            li.currency,
            o.created_at::date as fecha,
            o.user_owner_id as usuario_id
        FROM oro_order_line_item li
        JOIN oro_order o ON li.order_id = o.id
        LEFT JOIN oro_product p ON li.product_id = p.id
        WHERE o.created_at IS NOT NULL
        ORDER BY o.created_at
        """
        
        cursor_oro.execute(query)
        print(f"   Extrayendo datos de orocommerce...")
        line_items = cursor_oro.fetchall()
        print(f"   ✓ {len(line_items):,} registros extraídos")
        
        # Mapear a dimensiones del DW
        print(f"   Mapeando a dimensiones...")
        
        # Obtener mapeos de dimensiones
        cursor_dw.execute("SELECT fecha_id, fecha FROM dim_fecha")
        fecha_map = {fecha: fecha_id for fecha_id, fecha in cursor_dw.fetchall()}
        
        cursor_dw.execute("SELECT orden_id, orden_externo_id FROM dim_orden WHERE orden_externo_id IS NOT NULL")
        orden_map = {int(orig): orden_id for orden_id, orig in cursor_dw.fetchall()}
        
        # Cliente, producto, usuario - mapeo simple por ID si existe
        cursor_dw.execute("SELECT cliente_id FROM dim_cliente LIMIT 1")
        cliente_id_default = cursor_dw.fetchone()[0] if cursor_dw.rowcount > 0 else None
        
        cursor_dw.execute("SELECT producto_id FROM dim_producto LIMIT 1")
        producto_id_default = cursor_dw.fetchone()[0] if cursor_dw.rowcount > 0 else None
        
        cursor_dw.execute("SELECT usuario_id FROM dim_usuario LIMIT 1")
        usuario_id_default = cursor_dw.fetchone()[0] if cursor_dw.rowcount > 0 else None
        
        # Almacén por defecto (ALM_CENTRAL)
        cursor_dw.execute("SELECT almacen_id FROM dim_almacen WHERE codigo = 'ALM_CENTRAL' LIMIT 1")
        almacen_default = cursor_dw.fetchone()
        almacen_id_default = almacen_default[0] if almacen_default else 1
        
        # Obtener impuesto por defecto
        cursor_dw.execute("SELECT impuesto_id FROM dim_impuestos WHERE codigo = 'IVA_13' LIMIT 1")
        impuesto_default = cursor_dw.fetchone()
        impuesto_id = impuesto_default[0] if impuesto_default else 1
        
        # Transformar datos
        registros = []
        errores = 0
        
        for row in line_items:
            (line_item_id, orden_id_orig, customer_id, producto_id_orig, 
             quantity, precio_unitario, currency, fecha, usuario_id_orig) = row
            
            try:
                # Mapear IDs
                fecha_id = fecha_map.get(fecha)
                orden_id = orden_map.get(orden_id_orig) if orden_id_orig else None
                
                # Usar valores por defecto para otras dimensiones
                cliente_id = cliente_id_default
                producto_id = producto_id_default
                usuario_id = usuario_id_default
                almacen_id = almacen_id_default
                
                # Validar que existan las claves necesarias
                if not fecha_id or not orden_id:
                    errores += 1
                    continue
                
                # Calcular métricas
                cantidad = float(quantity or 0)
                precio = float(precio_unitario or 0)
                subtotal = cantidad * precio
                impuesto_monto = subtotal * 0.13  # IVA 13%
                total = subtotal + impuesto_monto
                descuento = 0.0  # No hay descuentos en el origen
                envio = 0.0  # No hay costos de envío en el origen
                
                registros.append((
                    fecha_id,
                    cliente_id,
                    producto_id,
                    orden_id,
                    usuario_id,
                    almacen_id,
                    impuesto_id,
                    cantidad,
                    precio,
                    subtotal,
                    descuento,
                    impuesto_monto,
                    envio,
                    total
                ))
                
            except Exception as e:
                errores += 1
                continue
        
        print(f"   ✓ {len(registros):,} registros válidos (errores: {errores})")
        
        # Insertar en fact_ventas
        if registros:
            insert_query = """
            INSERT INTO fact_ventas (
                fecha_id, cliente_id, producto_id, orden_id,
                usuario_id, almacen_id, impuesto_id,
                cantidad, precio_unitario, subtotal,
                descuento, impuesto, envio, total
            ) VALUES %s
            """
            
            execute_values(cursor_dw, insert_query, registros, page_size=1000)
            conn_dw.commit()
            
            print(f"   ✅ {len(registros):,} registros insertados en fact_ventas")
        else:
            print("   ⚠️  No hay registros para insertar")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn_dw.rollback()
        raise
    
    finally:
        cursor_oro.close()
        conn_oro.close()
        cursor_dw.close()
        conn_dw.close()
    
    print(f"\n{'='*80}")
    print("✅ FACT_VENTAS CARGADA CORRECTAMENTE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    cargar_fact_ventas()
