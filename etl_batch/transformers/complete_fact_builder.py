#!/usr/bin/env python3
"""
FACT TRANSFORMERS - Transformadores completos para todas las tablas de hechos
Puebla facts con datos reales desde OroCommerce y CSVs
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ROOT del proyecto
ROOT = Path(__file__).resolve().parent.parent.parent

class CompleteFactBuilder:
    """Constructor completo de todas las tablas de hechos"""
    
    def __init__(self):
        self.oro_conn = self._get_oro_connection()
        self.dw_conn = self._get_dw_connection()
        
    def _get_oro_connection(self):
        """Conexión a OroCommerce"""
        return psycopg2.connect(
            host=os.getenv('ORO_DB_HOST'),
            port=int(os.getenv('ORO_DB_PORT')),
            dbname=os.getenv('ORO_DB_NAME'),
            user=os.getenv('ORO_DB_USER'),
            password=os.getenv('ORO_DB_PASS')
        )
    
    def _get_dw_connection(self):
        """Conexión al Data Warehouse"""
        return psycopg2.connect(
            host=os.getenv('DW_DB_HOST'),
            port=int(os.getenv('DW_DB_PORT')),
            dbname=os.getenv('DW_DB_NAME'),
            user=os.getenv('DW_DB_USER'),
            password=os.getenv('DW_DB_PASS')
        )
    
    def _resolve_surrogate_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resolver Surrogate Keys de dimensiones desde el DW"""
        
        # Lookup dim_cliente
        query_cliente = "SELECT cliente_id, cliente_externo_id FROM dim_cliente"
        dim_cliente = pd.read_sql_query(query_cliente, self.dw_conn)
        df = df.merge(
            dim_cliente[['cliente_id', 'cliente_externo_id']], 
            on='cliente_externo_id', 
            how='left'
        )
        df['cliente_id'] = df['cliente_id'].fillna(1).astype(int)
        
        # Lookup dim_usuario - convertir ambos a string para el merge
        query_usuario = "SELECT usuario_id, usuario_externo_id FROM dim_usuario"
        dim_usuario = pd.read_sql_query(query_usuario, self.dw_conn)
        df['usuario_id_str'] = df['usuario_id'].astype(str)
        dim_usuario['usuario_externo_id_str'] = dim_usuario['usuario_externo_id'].astype(str)
        
        df = df.merge(
            dim_usuario[['usuario_id', 'usuario_externo_id_str']], 
            left_on='usuario_id_str',
            right_on='usuario_externo_id_str',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['usuario_id'] = df['usuario_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['usuario_id_str', 'usuario_externo_id_str', 'usuario_id_orig', 'usuario_id_sk'], errors='ignore')
        
        # Lookup dim_producto
        query_producto = "SELECT producto_id, producto_externo_id FROM dim_producto"
        dim_producto = pd.read_sql_query(query_producto, self.dw_conn)
        df['product_id'] = df['product_id'].astype(int)
        dim_producto['producto_externo_id'] = dim_producto['producto_externo_id'].astype(int)
        
        df = df.merge(
            dim_producto[['producto_id', 'producto_externo_id']], 
            left_on='product_id',
            right_on='producto_externo_id',
            how='left'
        )
        df['producto_id'] = df['producto_id'].fillna(1).astype(int)
        df = df.drop(columns=['producto_externo_id', 'product_id'], errors='ignore')
        
        # Lookup dim_direccion
        query_direccion = "SELECT direccion_id, direccion_externo_id FROM dim_direccion"
        dim_direccion = pd.read_sql_query(query_direccion, self.dw_conn)
        df['direccion_id'] = df['direccion_id'].astype(int)
        dim_direccion['direccion_externo_id'] = dim_direccion['direccion_externo_id'].astype(int)
        
        df = df.merge(
            dim_direccion[['direccion_id', 'direccion_externo_id']], 
            left_on='direccion_id',
            right_on='direccion_externo_id',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['direccion_id'] = df['direccion_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['direccion_externo_id', 'direccion_id_orig', 'direccion_id_sk'], errors='ignore')
        
        # Lookup dim_orden
        query_orden = "SELECT orden_id, orden_externo_id FROM dim_orden"
        dim_orden = pd.read_sql_query(query_orden, self.dw_conn)
        df['orden_id'] = df['orden_id'].astype(int)
        dim_orden['orden_externo_id'] = dim_orden['orden_externo_id'].astype(int)
        
        df = df.merge(
            dim_orden[['orden_id', 'orden_externo_id']], 
            left_on='orden_id',
            right_on='orden_externo_id',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['orden_id'] = df['orden_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['orden_externo_id', 'orden_id_orig', 'orden_id_sk'], errors='ignore')
        
        # Lookup dim_line_item
        query_line_item = "SELECT line_item_id, line_item_externo_id FROM dim_line_item"
        dim_line_item = pd.read_sql_query(query_line_item, self.dw_conn)
        df['line_item_id'] = df['line_item_id'].astype(int)
        dim_line_item['line_item_externo_id'] = dim_line_item['line_item_externo_id'].astype(int)
        
        df = df.merge(
            dim_line_item[['line_item_id', 'line_item_externo_id']], 
            left_on='line_item_id',
            right_on='line_item_externo_id',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['line_item_id'] = df['line_item_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['line_item_externo_id', 'line_item_id_orig', 'line_item_id_sk'], errors='ignore')
        
        logger.info(f"✓ SKs resueltas: clientes={df['cliente_id'].nunique()}, productos={df['producto_id'].nunique()}, ordenes={df['orden_id'].nunique()}")
        
        return df
    def build_fact_ventas(self) -> pd.DataFrame:
        """Construir fact_ventas desde oro_order + oro_order_line_item"""
        logger.info("💰 Construyendo fact_ventas...")
        
        query = """
        SELECT 
            o.id as orden_id,
            o.customer_id as cliente_externo_id,
            o.website_id as sitio_web_id,
            o.customer_user_id as usuario_id,
            o.created_at::date as fecha_orden,
            oli.id as line_item_id,
            oli.product_id,
            oli.quantity as cantidad,
            oli.value as precio_unitario,
            (oli.quantity * oli.value) as subtotal,
            COALESCE(o.subtotal_value, oli.quantity * oli.value) as total_orden,
            o.currency,
            o.created_at,
            COALESCE(o.internal_status_id, 'pending') as estado_orden_interno,
            COALESCE(o.shipping_address_id, o.billing_address_id, 0) as direccion_id
        FROM oro_order o
        INNER JOIN oro_order_line_item oli ON o.id = oli.order_id
        WHERE o.created_at >= '2023-01-01'
          AND oli.quantity > 0
          AND oli.value > 0
        ORDER BY o.created_at DESC
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        
        # Hacer lookup de SKs desde el DW
        logger.info("🔍 Resolviendo Surrogate Keys desde DW...")
        df = self._resolve_surrogate_keys(df)
        
        # Convertir fecha a ID
        df['fecha_id'] = pd.to_datetime(df['fecha_orden']).dt.strftime('%Y%m%d').astype(int)
        
        # Mapear estados de orden
        estado_orden_map = {
            'open': 'pending',
            'pending': 'pending',
            'processing': 'processing',
            'shipped': 'shipped',
            'delivered': 'delivered',
            'cancelled': 'cancelled',
            'closed': 'completed',
            'completed': 'completed',
        }
        df['id_estado_orden'] = df['estado_orden_interno'].map(lambda x: estado_orden_map.get(x, 'pending'))
        
        # IDs por defecto para otras dimensiones
        df['canal_id'] = 1
        df['estado_pago_id'] = 1
        df['metodo_pago_id'] = 1
        df['metodo_envio_id'] = 1
        df['impuesto_id'] = 1
        df['promocion_id'] = None
        
        # Cálculos financieros
        df['costo_unitario'] = df['precio_unitario'] * 0.6
        df['costo_total'] = df['costo_unitario'] * df['cantidad']
        df['descuento'] = 0.0
        df['impuesto'] = df['subtotal'] * 0.13
        df['total'] = df['subtotal'] + df['impuesto']
        df['margen_bruto'] = df['subtotal'] - df['costo_total']
        df['margen_porcentaje'] = (df['margen_bruto'] / df['subtotal'] * 100).round(2)
        
        # Comisiones
        df['comision'] = df['subtotal'] * 0.05
        
        # Métricas adicionales
        df['peso_total'] = df['cantidad'] * 0.5
        df['volumen_total'] = df['cantidad'] * 0.01
        
        logger.info(f"✓ fact_ventas: {len(df):,} registros desde oro_order")
        logger.info(f"   Estados de orden: {df['id_estado_orden'].value_counts().to_dict()}")
        return df
    
    def build_fact_inventario(self) -> pd.DataFrame:
        """Construir fact_inventario desde CSV movimientos_inventario"""
        logger.info("📦 Construyendo fact_inventario...")
        
        csv_path = ROOT / 'data' / 'inputs' / 'inventario' / 'movimientos_inventario.csv'
        df = pd.read_csv(csv_path)
        
        # Renombrar columnas del CSV a nombres de tabla
        df = df.rename(columns={
            'fecha': 'fecha_movimiento',
            'stock_resultante': 'stock_resultante',
            'documento': 'documento'
        })
        
        # Convertir fecha a ID
        df['fecha_id'] = pd.to_datetime(df['fecha_movimiento']).dt.strftime('%Y%m%d').astype(int)
        
        # Resolver SKs de dimensiones
        logger.info("🔍 Resolviendo SKs para fact_inventario...")
        
        # Lookup dim_producto usando product_id del CSV
        query_producto = "SELECT producto_id, producto_externo_id FROM dim_producto"
        dim_producto = pd.read_sql_query(query_producto, self.dw_conn)
        df['product_id'] = df['product_id'].astype(int)
        dim_producto['producto_externo_id'] = dim_producto['producto_externo_id'].astype(int)
        df = df.merge(
            dim_producto[['producto_id', 'producto_externo_id']], 
            left_on='product_id',
            right_on='producto_externo_id',
            how='left'
        )
        df['producto_id'] = df['producto_id'].fillna(1).astype(int)
        df = df.drop(columns=['producto_externo_id', 'product_id'], errors='ignore')
        
        # Lookup dim_almacen - usar código directamente (ALM001)
        query_almacen = "SELECT almacen_id, codigo FROM dim_almacen"
        dim_almacen = pd.read_sql_query(query_almacen, self.dw_conn)
        df = df.merge(
            dim_almacen,
            left_on='almacen_id',
            right_on='codigo',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['almacen_id'] = df['almacen_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'almacen_id_orig', 'almacen_id_sk'], errors='ignore')
        
        # Lookup dim_proveedor - usar código directamente (PROV001)
        query_proveedor = "SELECT proveedor_id, codigo FROM dim_proveedor"
        dim_proveedor = pd.read_sql_query(query_proveedor, self.dw_conn)
        df = df.merge(
            dim_proveedor,
            left_on='proveedor_id',
            right_on='codigo',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['proveedor_id'] = df['proveedor_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'proveedor_id_orig', 'proveedor_id_sk'], errors='ignore')
        
        # Lookup dim_tipo_movimiento - usar código directamente
        query_tipo_mov = "SELECT tipo_movimiento_id, codigo FROM dim_tipo_movimiento"
        dim_tipo_mov = pd.read_sql_query(query_tipo_mov, self.dw_conn)
        df = df.merge(
            dim_tipo_mov,
            left_on='tipo_movimiento_id',
            right_on='codigo',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['tipo_movimiento_id'] = df['tipo_movimiento_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'tipo_movimiento_id_orig', 'tipo_movimiento_id_sk'], errors='ignore')
        
        # Usuario por defecto
        df['usuario_id'] = 1
        
        logger.info(f"✓ fact_inventario: {len(df):,} registros desde CSV")
        logger.info(f"   Productos únicos: {df['producto_id'].nunique()}, Almacenes: {df['almacen_id'].nunique()}")
        
        return df[['fecha_id', 'producto_id', 'almacen_id', 'tipo_movimiento_id', 'proveedor_id', 
                   'usuario_id', 'cantidad', 'costo_unitario', 'costo_total', 
                   'stock_anterior', 'stock_resultante', 'documento', 'observaciones']]
    
    def build_fact_transacciones(self) -> pd.DataFrame:
        """Construir fact_transacciones desde CSV transacciones_contables"""
        logger.info("💳 Construyendo fact_transacciones...")
        
        csv_path = ROOT / 'data' / 'inputs' / 'finanzas' / 'transacciones_contables.csv'
        df = pd.read_csv(csv_path)
        
        # Convertir fecha a ID y derivar periodo_id
        df['fecha_id'] = pd.to_datetime(df['fecha']).dt.strftime('%Y%m%d').astype(int)
        df['periodo_id'] = pd.to_datetime(df['fecha']).dt.strftime('%Y%m').astype(int)
        
        # Resolver SKs de dimensiones
        logger.info("🔍 Resolviendo SKs para fact_transacciones...")
        
        # Lookup dim_cuenta_contable - el CSV usa códigos directos (1102, 1103, 4101, etc.)
        # Mapear código del CSV → SK de la dimensión
        query_cuenta = "SELECT cuenta_id, codigo FROM dim_cuenta_contable"
        dim_cuenta = pd.read_sql_query(query_cuenta, self.dw_conn)
        dim_cuenta['codigo'] = dim_cuenta['codigo'].astype(str)
        df['cuenta_codigo_csv'] = df['cuenta_id'].astype(str)
        
        df = df.merge(
            dim_cuenta,
            left_on='cuenta_codigo_csv',
            right_on='codigo',
            how='left',
            suffixes=('_csv', '_dim')
        )
        df['cuenta_id'] = df['cuenta_id_dim'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'cuenta_codigo_csv', 'cuenta_id_csv', 'cuenta_id_dim'], errors='ignore')
        
        # Lookup dim_centro_costo - usar código directamente (CC001)
        query_centro = "SELECT centro_costo_id, codigo FROM dim_centro_costo"
        dim_centro = pd.read_sql_query(query_centro, self.dw_conn)
        df = df.merge(
            dim_centro,
            left_on='centro_costo_id',
            right_on='codigo',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['centro_costo_id'] = df['centro_costo_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'centro_costo_id_orig', 'centro_costo_id_sk'], errors='ignore')
        
        # Lookup dim_tipo_transaccion - el CSV tiene ID numérico directo
        df['tipo_transaccion_id'] = df['tipo_transaccion_id'].fillna(1).astype(int)
        
        # Usuario por defecto
        df['usuario_id'] = 1
        
        # Renombrar columnas finales
        df = df.rename(columns={
            'documento_referencia': 'documento_referencia',
            'descripcion': 'descripcion',
            'orden_id': 'orden_id'
        })
        
        # Columna movimiento_inventario_id por defecto
        df['movimiento_inventario_id'] = None
        
        logger.info(f"✓ fact_transacciones: {len(df):,} registros desde CSV")
        logger.info(f"   Tipo movimiento: {df['tipo_movimiento'].value_counts().to_dict()}")
        logger.info(f"   Períodos: {df['periodo_id'].min()} a {df['periodo_id'].max()}")
        logger.info(f"   Cuentas únicas: {df['cuenta_id'].nunique()}")
        
        return df[['fecha_id', 'periodo_id', 'cuenta_id', 'centro_costo_id', 'tipo_transaccion_id', 'usuario_id',
                   'numero_asiento', 'tipo_movimiento', 'monto', 'documento_referencia', 
                   'descripcion', 'orden_id', 'movimiento_inventario_id']]
    
    def build_fact_balance(self) -> pd.DataFrame:
        """Construir fact_balance agregado desde fact_transacciones"""
        logger.info("📊 Construyendo fact_balance desde fact_transacciones...")
        
        query = """
        SELECT 
            periodo_id,
            cuenta_id,
            SUM(CASE WHEN tipo_movimiento = 'debe' THEN monto ELSE 0 END) as debitos,
            SUM(CASE WHEN tipo_movimiento = 'haber' THEN monto ELSE 0 END) as creditos
        FROM fact_transacciones
        WHERE cuenta_id IS NOT NULL AND periodo_id IS NOT NULL
        GROUP BY periodo_id, cuenta_id
        ORDER BY periodo_id, cuenta_id
        """
        
        try:
            df = pd.read_sql_query(query, self.dw_conn)
            
            # Calcular saldos
            # Saldo inicial = saldo final del período anterior
            # Ordenar por cuenta y período
            df = df.sort_values(['cuenta_id', 'periodo_id'])
            
            # Para cada cuenta, calcular el saldo acumulado
            df['saldo_inicial'] = 0.0
            df['saldo_final'] = df['debitos'] - df['creditos']
            
            # Calcular saldo inicial como el saldo final del período anterior
            for cuenta_id in df['cuenta_id'].unique():
                mask = df['cuenta_id'] == cuenta_id
                # Acumular saldo para esta cuenta
                saldos = df.loc[mask, 'saldo_final'].cumsum()
                # El saldo inicial es el saldo acumulado del período anterior
                df.loc[mask, 'saldo_final'] = saldos
                df.loc[mask, 'saldo_inicial'] = saldos.shift(1).fillna(0)
            
            # Convertir tipos numpy a tipos nativos de Python
            for col in ['periodo_id', 'cuenta_id']:
                df[col] = df[col].astype(int)
            for col in ['debitos', 'creditos', 'saldo_inicial', 'saldo_final']:
                df[col] = df[col].astype(float).round(2)
            
            logger.info(f"✓ fact_balance: {len(df):,} registros agregados")
            logger.info(f"   Períodos: {df['periodo_id'].nunique()}, Cuentas: {df['cuenta_id'].nunique()}")
            
        except Exception as e:
            logger.error(f"❌ Error construyendo fact_balance: {e}")
            import traceback
            traceback.print_exc()
            df = pd.DataFrame(columns=[
                'periodo_id', 'cuenta_id', 'saldo_inicial', 
                'debitos', 'creditos', 'saldo_final'
            ])
        
        return df
    
    def build_fact_estado_resultados(self) -> pd.DataFrame:
        """Construir fact_estado_resultados agregado desde fact_transacciones"""
        logger.info("📈 Construyendo fact_estado_resultados desde fact_transacciones...")
        
        query = """
        SELECT 
            ft.periodo_id,
            ft.cuenta_id,
            ft.centro_costo_id,
            dc.tipo as naturaleza_cuenta,
            dc.nombre as nombre_cuenta,
            SUM(CASE WHEN ft.tipo_movimiento = 'debe' THEN ft.monto ELSE 0 END) as debitos,
            SUM(CASE WHEN ft.tipo_movimiento = 'haber' THEN ft.monto ELSE 0 END) as creditos,
            SUM(CASE WHEN ft.tipo_movimiento = 'debe' THEN ft.monto 
                     ELSE -ft.monto END) as monto_neto
        FROM fact_transacciones ft
        INNER JOIN dim_cuenta_contable dc ON ft.cuenta_id = dc.cuenta_id
        WHERE ft.cuenta_id IS NOT NULL 
          AND ft.periodo_id IS NOT NULL
          AND dc.codigo IS NOT NULL
        GROUP BY ft.periodo_id, ft.cuenta_id, ft.centro_costo_id, dc.tipo, dc.nombre
        ORDER BY ft.periodo_id, ft.cuenta_id
        """
        
        try:
            df = pd.read_sql_query(query, self.dw_conn)
            
            # Clasificar cuentas por tipo de estado de resultados
            # Las cuentas 4000-4999 son ingresos, 5000-5999 son costos, 6000-6999 son gastos
            def clasificar_cuenta(row):
                # Aquí clasificamos por nombre o naturaleza
                nombre = str(row['nombre_cuenta']).lower()
                if 'ingreso' in nombre or 'venta' in nombre:
                    return 'ingreso'
                elif 'costo' in nombre or 'compra' in nombre:
                    return 'costo'
                elif 'gasto' in nombre:
                    return 'gasto'
                else:
                    return 'otro'
            
            df['tipo_cuenta'] = df.apply(clasificar_cuenta, axis=1)
            
            # Pivotar para calcular componentes del estado de resultados
            pivot = df.pivot_table(
                index=['periodo_id', 'cuenta_id', 'centro_costo_id'],
                columns='tipo_cuenta',
                values='creditos',  # Ingresos y costos usan créditos generalmente
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            # Calcular métricas financieras
            pivot['ingresos'] = pivot.get('ingreso', 0)
            pivot['costos'] = pivot.get('costo', 0)
            pivot['gastos'] = pivot.get('gasto', 0)
            pivot['utilidad_bruta'] = pivot['ingresos'] - pivot['costos']
            pivot['utilidad_neta'] = pivot['utilidad_bruta'] - pivot['gastos']
            
            # Seleccionar solo las columnas finales
            result = pivot[['periodo_id', 'cuenta_id', 'centro_costo_id', 
                           'ingresos', 'costos', 'gastos', 
                           'utilidad_bruta', 'utilidad_neta']]
            
            # Filtrar filas con al menos un valor no cero
            result = result[
                (result['ingresos'] != 0) | 
                (result['costos'] != 0) | 
                (result['gastos'] != 0)
            ]
            
            # Convertir tipos numpy a tipos nativos de Python
            for col in ['periodo_id', 'cuenta_id', 'centro_costo_id']:
                result[col] = result[col].astype(int)
            for col in ['ingresos', 'costos', 'gastos', 'utilidad_bruta', 'utilidad_neta']:
                result[col] = result[col].astype(float).round(2)
            
            logger.info(f"✓ fact_estado_resultados: {len(result):,} registros agregados")
            logger.info(f"   Períodos: {result['periodo_id'].nunique()}, Cuentas: {result['cuenta_id'].nunique()}")
            
        except Exception as e:
            logger.error(f"❌ Error construyendo fact_estado_resultados: {e}")
            import traceback
            traceback.print_exc()
            result = pd.DataFrame(columns=[
                'periodo_id', 'cuenta_id', 'centro_costo_id',
                'ingresos', 'costos', 'gastos', 
                'utilidad_bruta', 'utilidad_neta'
            ])
        
        return result
    
    def __del__(self):
        """Cerrar conexiones"""
        try:
            self.oro_conn.close()
            self.dw_conn.close()
        except:
            pass
