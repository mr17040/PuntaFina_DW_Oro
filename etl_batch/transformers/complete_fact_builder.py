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

logger = logging.getLogger(__name__)

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
    
    def build_fact_ventas(self) -> pd.DataFrame:
        """Construir fact_ventas desde oro_order + oro_order_line_item"""
        logger.info("💰 Construyendo fact_ventas...")
        
        query = """
        SELECT 
            o.id as orden_id,
            o.customer_id as cliente_id,
            o.website_id as sitio_web_id,
            o.created_at::date as fecha_orden,
            oli.id as line_item_id,
            oli.product_id,
            oli.quantity as cantidad,
            oli.value as precio_unitario,
            (oli.quantity * oli.value) as subtotal,
            COALESCE(o.subtotal_value, oli.quantity * oli.value) as total_orden,
            o.currency,
            o.created_at
        FROM oro_order o
        INNER JOIN oro_order_line_item oli ON o.id = oli.order_id
        WHERE o.created_at >= '2024-01-01'
        ORDER BY o.created_at DESC
        LIMIT 10000
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        
        # Convertir fecha a ID
        df['fecha_id'] = pd.to_datetime(df['fecha_orden']).dt.strftime('%Y%m%d').astype(int)
        
        # IDs por defecto para otras dimensiones
        df['usuario_id'] = 1
        df['canal_id'] = 1
        df['estado_orden_id'] = 1
        df['estado_pago_id'] = 1
        df['metodo_pago_id'] = 1
        df['metodo_envio_id'] = 1
        df['direccion_envio_id'] = 1
        df['direccion_facturacion_id'] = 1
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
        return df
    
    def build_fact_inventario(self) -> pd.DataFrame:
        """Construir fact_inventario desde CSV movimientos_inventario"""
        logger.info("📦 Construyendo fact_inventario...")
        
        csv_path = '../data/inputs/inventario/movimientos_inventario.csv'
        df = pd.read_csv(csv_path, parse_dates=['fecha_movimiento'])
        
        # Convertir fecha a ID
        df['fecha_id'] = pd.to_datetime(df['fecha_movimiento']).dt.strftime('%Y%m%d').astype(int)
        
        # Renombrar columnas
        column_mapping = {
            'tipo_movimiento_id': 'tipo_movimiento_id',
            'almacen_id': 'almacen_id',
            'producto_id': 'producto_id',
            'proveedor_id': 'proveedor_id',
            'cantidad': 'cantidad',
            'costo_unitario': 'costo_unitario',
            'costo_total': 'costo_total',
            'stock_anterior': 'stock_anterior',
            'stock_posterior': 'stock_posterior',
            'documento_referencia': 'documento_referencia',
            'observaciones': 'observaciones'
        }
        
        df = df.rename(columns=column_mapping)
        df['usuario_id'] = 1
        df['lote'] = 'LOTE-' + df.index.astype(str).str.zfill(6)
        df['fecha_vencimiento'] = None
        
        logger.info(f"✓ fact_inventario: {len(df):,} registros desde CSV")
        return df
    
    def build_fact_transacciones(self) -> pd.DataFrame:
        """Construir fact_transacciones desde CSV transacciones_contables"""
        logger.info("💳 Construyendo fact_transacciones...")
        
        csv_path = '../data/inputs/finanzas/transacciones_contables.csv'
        df = pd.read_csv(csv_path, parse_dates=['fecha_transaccion'])
        
        # Convertir fecha a ID
        df['fecha_id'] = pd.to_datetime(df['fecha_transaccion']).dt.strftime('%Y%m%d').astype(int)
        df['periodo_id'] = (pd.to_datetime(df['fecha_transaccion']).dt.year * 100 + 
                           pd.to_datetime(df['fecha_transaccion']).dt.month)
        
        # Campos adicionales
        df['usuario_id'] = 1
        df['descripcion'] = df['descripcion'] if 'descripcion' in df.columns else 'Transacción automática'
        df['documento_referencia'] = df['documento_referencia'] if 'documento_referencia' in df.columns else None
        df['conciliado'] = False
        
        logger.info(f"✓ fact_transacciones: {len(df):,} registros desde CSV")
        return df
    
    def build_fact_balance(self) -> pd.DataFrame:
        """Construir fact_balance agregado por periodo"""
        logger.info("📊 Construyendo fact_balance...")
        
        query = """
        SELECT 
            periodo_id,
            cuenta_id,
            centro_costo_id,
            SUM(CASE WHEN tipo_movimiento = 'Debe' THEN monto ELSE 0 END) as total_debe,
            SUM(CASE WHEN tipo_movimiento = 'Haber' THEN monto ELSE 0 END) as total_haber,
            SUM(CASE WHEN tipo_movimiento = 'Debe' THEN monto ELSE -monto END) as saldo_periodo,
            COUNT(*) as num_transacciones
        FROM fact_transacciones
        GROUP BY periodo_id, cuenta_id, centro_costo_id
        ORDER BY periodo_id, cuenta_id
        """
        
        try:
            df = pd.read_sql_query(query, self.dw_conn)
            df['saldo_anterior'] = 0.0
            df['saldo_acumulado'] = df.groupby('cuenta_id')['saldo_periodo'].cumsum()
            logger.info(f"✓ fact_balance: {len(df):,} registros agregados")
        except Exception as e:
            logger.warning(f"⚠️ fact_balance vacío: {e}")
            df = pd.DataFrame(columns=[
                'periodo_id', 'cuenta_id', 'centro_costo_id',
                'saldo_anterior', 'total_debe', 'total_haber',
                'saldo_periodo', 'saldo_acumulado', 'num_transacciones'
            ])
        
        return df
    
    def build_fact_estado_resultados(self) -> pd.DataFrame:
        """Construir fact_estado_resultados agregado por periodo"""
        logger.info("📈 Construyendo fact_estado_resultados...")
        
        query = """
        SELECT 
            ft.periodo_id,
            ft.centro_costo_id,
            cc.tipo_cuenta,
            SUM(ft.monto) as monto_total,
            COUNT(*) as num_transacciones
        FROM fact_transacciones ft
        INNER JOIN dim_cuenta_contable cc ON ft.cuenta_id = cc.id
        WHERE cc.tipo_cuenta IN ('Ingreso', 'Costo de Ventas', 'Gasto', 'Otro Ingreso', 'Otro Gasto')
        GROUP BY ft.periodo_id, ft.centro_costo_id, cc.tipo_cuenta
        ORDER BY ft.periodo_id, cc.tipo_cuenta
        """
        
        try:
            df = pd.read_sql_query(query, self.dw_conn)
            
            # Pivotar para calcular métricas
            pivot = df.pivot_table(
                index=['periodo_id', 'centro_costo_id'],
                columns='tipo_cuenta',
                values='monto_total',
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            # Calcular componentes del estado de resultados
            pivot['ingresos'] = pivot.get('Ingreso', 0)
            pivot['costo_ventas'] = pivot.get('Costo de Ventas', 0)
            pivot['utilidad_bruta'] = pivot['ingresos'] - pivot['costo_ventas']
            pivot['gastos_operativos'] = pivot.get('Gasto', 0)
            pivot['utilidad_operativa'] = pivot['utilidad_bruta'] - pivot['gastos_operativos']
            pivot['otros_ingresos'] = pivot.get('Otro Ingreso', 0)
            pivot['otros_gastos'] = pivot.get('Otro Gasto', 0)
            pivot['utilidad_neta'] = (pivot['utilidad_operativa'] + 
                                     pivot['otros_ingresos'] - 
                                     pivot['otros_gastos'])
            pivot['margen_bruto'] = (pivot['utilidad_bruta'] / pivot['ingresos'] * 100).fillna(0).round(2)
            pivot['margen_operativo'] = (pivot['utilidad_operativa'] / pivot['ingresos'] * 100).fillna(0).round(2)
            pivot['margen_neto'] = (pivot['utilidad_neta'] / pivot['ingresos'] * 100).fillna(0).round(2)
            
            df = pivot[['periodo_id', 'centro_costo_id', 'ingresos', 'costo_ventas',
                       'utilidad_bruta', 'gastos_operativos', 'utilidad_operativa',
                       'otros_ingresos', 'otros_gastos', 'utilidad_neta',
                       'margen_bruto', 'margen_operativo', 'margen_neto']]
            
            logger.info(f"✓ fact_estado_resultados: {len(df):,} registros agregados")
        except Exception as e:
            logger.warning(f"⚠️ fact_estado_resultados vacío: {e}")
            df = pd.DataFrame(columns=[
                'periodo_id', 'centro_costo_id', 'ingresos', 'costo_ventas',
                'utilidad_bruta', 'gastos_operativos', 'utilidad_operativa',
                'otros_ingresos', 'otros_gastos', 'utilidad_neta',
                'margen_bruto', 'margen_operativo', 'margen_neto'
            ])
        
        return df
    
    def __del__(self):
        """Cerrar conexiones"""
        try:
            self.oro_conn.close()
            self.dw_conn.close()
        except:
            pass
