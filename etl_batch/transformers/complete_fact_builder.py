#!/usr/bin/env python3
"""
FACT TRANSFORMERS - Transformadores completos para todas las tablas de hechos
Puebla facts con datos reales desde OroCommerce y CSVs
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime
from typing import Dict, Any
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
    
    def build(self, fact_name: str, fact_config: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Método genérico para construir cualquier fact table
        Delegación a métodos específicos
        """
        method_name = f"build_{fact_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method()
        else:
            logger.warning(f"Fact table {fact_name} no implementada en CompleteFactBuilder")
            return pd.DataFrame()    
    def get_schema(self, fact_name: str) -> Dict[str, str]:
        """
        Retorna el esquema de la fact table para el loader
        Este método es requerido por el orchestrator pero no lo usamos
        porque fact_ventas se carga via dblink directamente
        """
        return {}        
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
            password=os.getenv('DW_DB_PASS'),
            connect_timeout=120,
            options='-c statement_timeout=1800000'
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
        """
        Construir fact_ventas desde oro_order + oro_order_line_item
        CORREGIDO: Retorna DataFrame en lugar de insertar directamente
        """
        logger.info("💰 Construyendo fact_ventas...")
        
        # Extraer datos de OroCommerce
        query = """
        SELECT 
            o.created_at::date as fecha,
            o.id as orden_id_externo,
            COALESCE(o.customer_user_id, 1) as cliente_id_externo,
            COALESCE(o.user_owner_id, 1) as usuario_id_externo,
            oli.product_id as producto_id_externo,
            oli.id as line_item_id_externo,
            CAST(oli.quantity AS NUMERIC(10,2)) as cantidad,
            CAST(oli.value AS NUMERIC(10,2)) as precio_unitario,
            CAST(oli.quantity * oli.value AS NUMERIC(10,2)) as subtotal,
            CAST(0.0 AS NUMERIC(10,2)) as descuento,
            CAST((oli.quantity * oli.value) * 0.13 AS NUMERIC(10,2)) as impuesto,
            CAST(0.0 AS NUMERIC(10,2)) as envio,
            CAST((oli.quantity * oli.value) * 1.13 AS NUMERIC(10,2)) as total,
            CAST(oli.value * 0.6 AS NUMERIC(10,2)) as costo_unitario,
            CAST(oli.quantity * oli.value * 0.6 AS NUMERIC(10,2)) as costo_total,
            CAST((oli.quantity * oli.value) * 0.4 AS NUMERIC(10,2)) as margen
        FROM oro_order o
        JOIN oro_order_line_item oli ON o.id = oli.order_id
        WHERE o.created_at IS NOT NULL 
          AND oli.product_id IS NOT NULL
          AND oli.quantity > 0
        """
        
        logger.info("   📥 Extrayendo datos desde OroCommerce...")
        df = pd.read_sql_query(query, self.oro_conn)
        logger.info(f"   ✓ Extraídos {len(df):,} registros")
        
        if df.empty:
            logger.warning("   ⚠️  No hay datos en oro_order/oro_order_line_item")
            return pd.DataFrame()
        
        # Cargar dimensiones en memoria desde archivos parquet
        parquet_dir = ROOT / 'data' / 'outputs' / 'parquet'
        
        dim_fecha = pd.read_parquet(parquet_dir / 'dim_fecha.parquet')
        dim_cliente = pd.read_parquet(parquet_dir / 'dim_cliente.parquet')
        dim_producto = pd.read_parquet(parquet_dir / 'dim_producto.parquet')
        dim_orden = pd.read_parquet(parquet_dir / 'dim_orden.parquet')
        dim_usuario = pd.read_parquet(parquet_dir / 'dim_usuario.parquet')
        dim_impuestos = pd.read_parquet(parquet_dir / 'dim_impuestos.parquet')
        dim_line_item = pd.read_parquet(parquet_dir / 'dim_line_item.parquet')
        
        logger.info("   🔗 Resolviendo surrogate keys...")
        
        # Convertir fechas a mismo tipo para merge
        df['fecha'] = pd.to_datetime(df['fecha'])
        dim_fecha['fecha'] = pd.to_datetime(dim_fecha['fecha'])
        
        # Resolver fecha_id
        df = df.merge(dim_fecha[['fecha_id', 'fecha']], left_on='fecha', right_on='fecha', how='left')
        df['fecha_id'] = df['fecha_id'].fillna(1).astype(int)
        
        # Resolver cliente_id
        df = df.merge(
            dim_cliente[['cliente_id', 'cliente_externo_id']],
            left_on='cliente_id_externo',
            right_on='cliente_externo_id',
            how='left',
            suffixes=('', '_dim')
        )
        df['cliente_id'] = df['cliente_id'].fillna(1).astype(int)
        df = df.drop(columns=['cliente_externo_id'], errors='ignore')
        
        # Resolver producto_id
        df = df.merge(
            dim_producto[['producto_id', 'producto_externo_id']],
            left_on='producto_id_externo',
            right_on='producto_externo_id',
            how='left',
            suffixes=('', '_dim')
        )
        df['producto_id'] = df['producto_id'].fillna(1).astype(int)
        df = df.drop(columns=['producto_externo_id'], errors='ignore')
        
        # Resolver orden_id
        df = df.merge(
            dim_orden[['orden_id', 'orden_externo_id']],
            left_on='orden_id_externo',
            right_on='orden_externo_id',
            how='left',
            suffixes=('', '_dim')
        )
        df['orden_id'] = df['orden_id'].fillna(1).astype(int)
        df = df.drop(columns=['orden_externo_id'], errors='ignore')
        
        # Resolver usuario_id
        df = df.merge(
            dim_usuario[['usuario_id', 'usuario_externo_id']],
            left_on='usuario_id_externo',
            right_on='usuario_externo_id',
            how='left',
            suffixes=('', '_dim')
        )
        df['usuario_id'] = df['usuario_id'].fillna(1).astype(int)
        df = df.drop(columns=['usuario_externo_id'], errors='ignore')
        
        # almacen_id por defecto (no está en oro_order)
        df['almacen_id'] = 1
        
        # Resolver line_item_id
        df = df.merge(
            dim_line_item[['line_item_id', 'line_item_externo_id']],
            left_on='line_item_id_externo',
            right_on='line_item_externo_id',
            how='left',
            suffixes=('', '_dim')
        )
        df['line_item_id'] = df['line_item_id'].fillna(1).astype(int)
        df = df.drop(columns=['line_item_externo_id'], errors='ignore')
        
        # Asignar impuesto_id (1=IVA 13%, 5=Sin Impuesto)
        df['impuesto_id'] = df['impuesto'].apply(lambda x: 1 if x > 0 else 5)
        
        # Seleccionar columnas finales
        fact_cols = [
            'fecha_id', 'cliente_id', 'producto_id', 'orden_id', 'usuario_id', 
            'almacen_id', 'impuesto_id', 'cantidad', 'precio_unitario', 'subtotal',
            'descuento', 'impuesto', 'envio', 'total', 'costo_unitario', 
            'costo_total', 'margen'
        ]
        
        df_final = df[fact_cols].copy()
        df_final['created_at'] = datetime.now()
        
        # Agregar surrogate key (PK)
        df_final.insert(0, 'venta_id', range(1, len(df_final) + 1))
        
        logger.info(f"   ✅ fact_ventas: {len(df_final):,} registros construidos")
        logger.info(f"   📊 IDs únicos: clientes={df_final['cliente_id'].nunique()}, productos={df_final['producto_id'].nunique()}, ordenes={df_final['orden_id'].nunique()}")
        
        return df_final
    
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
        
        # Cargar dimensiones desde parquet
        parquet_dir = ROOT / 'data' / 'outputs' / 'parquet'
        dim_producto = pd.read_parquet(parquet_dir / 'dim_producto.parquet')
        dim_almacen = pd.read_parquet(parquet_dir / 'dim_almacen.parquet')
        dim_proveedor = pd.read_parquet(parquet_dir / 'dim_proveedor.parquet')
        dim_tipo_mov = pd.read_parquet(parquet_dir / 'dim_tipo_movimiento.parquet')
        
        # Lookup dim_producto usando product_id del CSV
        df['product_id'] = df['product_id'].astype(int)
        dim_producto['producto_externo_id'] = dim_producto['producto_externo_id'].astype(int)
        
        # Filtrar solo productos que existen en dim_producto
        productos_validos = dim_producto['producto_externo_id'].unique()
        df_original_count = len(df)
        df = df[df['product_id'].isin(productos_validos)]
        if df_original_count > len(df):
            logger.warning(f"   ⚠️  Filtrados {df_original_count - len(df)} registros con productos inexistentes")
        
        df = df.merge(
            dim_producto[['producto_id', 'producto_externo_id']], 
            left_on='product_id',
            right_on='producto_externo_id',
            how='left'
        )
        df['producto_id'] = df['producto_id'].fillna(1).astype(int)
        df = df.drop(columns=['producto_externo_id', 'product_id'], errors='ignore')
        
        # Lookup dim_almacen - usar id_almacen directamente (ALM_CENTRAL, TIENDA_01...)
        df = df.merge(
            dim_almacen[['almacen_id', 'id_almacen']],
            left_on='almacen_id',
            right_on='id_almacen',
            how='left',
            suffixes=('_orig', '_sk')
        )
        df['almacen_id'] = df['almacen_id_sk'].fillna(1).astype(int)
        df = df.drop(columns=['id_almacen', 'almacen_id_orig', 'almacen_id_sk'], errors='ignore')
        
        # Lookup dim_proveedor - usar id_proveedor
        if 'id_proveedor' in dim_proveedor.columns:
            df = df.merge(
                dim_proveedor[['proveedor_id', 'id_proveedor']],
                left_on='proveedor_id',
                right_on='id_proveedor',
                how='left',
                suffixes=('_orig', '_sk')
            )
            df['proveedor_id'] = df['proveedor_id_sk'].fillna(1).astype(int)
            df = df.drop(columns=['id_proveedor', 'proveedor_id_orig', 'proveedor_id_sk'], errors='ignore')
        else:
            df['proveedor_id'] = 1
        
        # Lookup dim_tipo_movimiento - usar codigo_movimiento o id
        if 'codigo_movimiento' in dim_tipo_mov.columns:
            df = df.merge(
                dim_tipo_mov[['tipo_movimiento_id', 'codigo_movimiento']],
                left_on='tipo_movimiento_id',
                right_on='codigo_movimiento',
                how='left',
                suffixes=('_orig', '_sk')
            )
            df['tipo_movimiento_id'] = df['tipo_movimiento_id_sk'].fillna(1).astype(int)
            df = df.drop(columns=['codigo_movimiento', 'tipo_movimiento_id_orig', 'tipo_movimiento_id_sk'], errors='ignore')
        else:
            df['tipo_movimiento_id'] = 1
        
        # Usuario por defecto
        df['usuario_id'] = 1
        
        # Agregar surrogate key (PK)
        df.insert(0, 'movimiento_id', range(1, len(df) + 1))
        
        logger.info(f"✓ fact_inventario: {len(df):,} registros desde CSV")
        logger.info(f"   Productos únicos: {df['producto_id'].nunique()}, Almacenes: {df['almacen_id'].nunique()}")
        
        return df[['movimiento_id', 'fecha_id', 'producto_id', 'almacen_id', 'tipo_movimiento_id', 'proveedor_id', 
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
        
        # Cargar dimensiones desde parquet
        parquet_dir = ROOT / 'data' / 'outputs' / 'parquet'
        dim_cuenta = pd.read_parquet(parquet_dir / 'dim_cuenta_contable.parquet')
        dim_centro = pd.read_parquet(parquet_dir / 'dim_centro_costo.parquet')
        
        # Filtrar solo cuentas que existen en dim_cuenta_contable
        dim_cuenta['codigo'] = dim_cuenta['codigo'].astype(int)
        df['cuenta_id'] = df['cuenta_id'].astype(int)
        cuentas_validas = dim_cuenta['codigo'].unique()
        df_original_count = len(df)
        df = df[df['cuenta_id'].isin(cuentas_validas)]
        if df_original_count > len(df):
            logger.warning(f"   ⚠️  Filtrados {df_original_count - len(df)} registros con cuentas inexistentes")
        
        # Lookup dim_cuenta_contable - el CSV usa códigos directos (1102, 1103, 4101, etc.)
        # Mapear código del CSV → SK de la dimensión (cuenta_contable_id)
        df = df.merge(
            dim_cuenta[['cuenta_contable_id', 'codigo']],
            left_on='cuenta_id',
            right_on='codigo',
            how='left'
        )
        df['cuenta_id'] = df['cuenta_contable_id'].fillna(1).astype(int)
        df = df.drop(columns=['codigo', 'cuenta_contable_id'], errors='ignore')
        
        # Lookup dim_centro_costo - usar id_centro_costo o codigo
        if 'id_centro_costo' in dim_centro.columns:
            df = df.merge(
                dim_centro[['centro_costo_id', 'id_centro_costo']],
                left_on='centro_costo_id',
                right_on='id_centro_costo',
                how='left',
                suffixes=('_orig', '_sk')
            )
            df['centro_costo_id'] = df['centro_costo_id_sk'].fillna(1).astype(int)
            df = df.drop(columns=['id_centro_costo', 'centro_costo_id_orig', 'centro_costo_id_sk'], errors='ignore')
        else:
            df['centro_costo_id'] = 1
        
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
        
        # Agregar surrogate key (PK)
        df.insert(0, 'transaccion_id', range(1, len(df) + 1))
        
        logger.info(f"✓ fact_transacciones: {len(df):,} registros desde CSV")
        logger.info(f"   Tipo movimiento: {df['tipo_movimiento'].value_counts().to_dict()}")
        logger.info(f"   Períodos: {df['periodo_id'].min()} a {df['periodo_id'].max()}")
        logger.info(f"   Cuentas únicas: {df['cuenta_id'].nunique()}")
        
        return df[['transaccion_id', 'fecha_id', 'periodo_id', 'cuenta_id', 'centro_costo_id', 'tipo_transaccion_id', 'usuario_id',
                   'numero_asiento', 'tipo_movimiento', 'monto', 'documento_referencia', 
                   'descripcion', 'orden_id', 'movimiento_inventario_id']]
    
    def build_fact_balance(self) -> pd.DataFrame:
        """Construir fact_balance desde CSV o fact_transacciones"""
        logger.info("📊 Construyendo fact_balance...")
        
        # Primero intentar cargar desde CSV
        csv_path = ROOT / 'data' / 'inputs' / 'balance.csv'
        if csv_path.exists():
            logger.info(f"   📂 Cargando desde CSV: {csv_path}")
            try:
                df = pd.read_csv(csv_path)
                
                # Eliminar fecha_id del CSV si existe (lo recalcularemos)
                if 'fecha_id' in df.columns:
                    df = df.drop(columns=['fecha_id'])
                
                # Los cuenta_id del CSV ya son surrogate keys (1,2,3...)
                # Solo necesitamos validar que existan en dim_cuenta_contable
                parquet_dir = ROOT / 'data' / 'outputs' / 'parquet'
                dim_cuenta = pd.read_parquet(parquet_dir / 'dim_cuenta_contable.parquet')
                cuentas_validas = dim_cuenta['cuenta_contable_id'].unique()
                
                # Filtrar solo cuentas que existen
                df_original_count = len(df)
                df = df[df['cuenta_id'].isin(cuentas_validas)]
                if df_original_count > len(df):
                    logger.warning(f"   ⚠️  Filtrados {df_original_count - len(df)} registros con cuentas inexistentes")
                
                # Convertir tipos
                for col in ['periodo_id', 'cuenta_id']:
                    df[col] = df[col].astype(int)
                for col in ['saldo_inicial', 'debitos', 'creditos', 'saldo_final']:
                    df[col] = df[col].astype(float).round(2)
                
                # Si periodo_id es secuencial (1,2,3...) convertir a formato YYYYMM
                if df['periodo_id'].min() < 1000:
                    logger.info(f"   🔄 Convirtiendo periodo_id secuencial a formato YYYYMM...")
                    df['periodo_id'] = 202400 + df['periodo_id']
                
                # Generar fecha_id desde periodo_id (YYYYMM → YYYYMM01)
                df['fecha_id'] = (df['periodo_id'] * 100 + 1).astype(int)
                
                # Agregar surrogate key (PK)
                df.insert(0, 'balance_id', range(1, len(df) + 1))
                    
                logger.info(f"   ✓ fact_balance: {len(df):,} registros desde CSV")
                logger.info(f"   Períodos: {sorted(df['periodo_id'].unique())}")
                return df
            except Exception as e:
                logger.warning(f"   ⚠️  Error leyendo CSV: {e}")
        
        # Si no hay CSV, intentar construir desde fact_transacciones
        logger.info("   📊 Construyendo desde fact_transacciones...")
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
            
            # Generar fecha_id desde periodo_id (YYYYMM → YYYYMM01)
            df['fecha_id'] = (df['periodo_id'] * 100 + 1).astype(int)
            
            # Agregar surrogate key (PK)
            df.insert(0, 'balance_id', range(1, len(df) + 1))
            
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
        """Construir fact_estado_resultados desde CSV o fact_transacciones"""
        logger.info("📈 Construyendo fact_estado_resultados...")
        
        # Primero intentar cargar desde CSV
        csv_path = ROOT / 'data' / 'inputs' / 'estado_resultados.csv'
        if csv_path.exists():
            logger.info(f"   📂 Cargando desde CSV: {csv_path}")
            try:
                df = pd.read_csv(csv_path)
                
                # Eliminar fecha_id del CSV si existe (lo recalcularemos)
                if 'fecha_id' in df.columns:
                    df = df.drop(columns=['fecha_id'])
                
                # Los cuenta_id del CSV ya son surrogate keys (7,8,9,10,11...)
                # Solo necesitamos validar que existan en dim_cuenta_contable
                parquet_dir = ROOT / 'data' / 'outputs' / 'parquet'
                dim_cuenta = pd.read_parquet(parquet_dir / 'dim_cuenta_contable.parquet')
                cuentas_validas = dim_cuenta['cuenta_contable_id'].unique()
                
                # Filtrar solo cuentas que existen
                df_original_count = len(df)
                df = df[df['cuenta_id'].isin(cuentas_validas)]
                if df_original_count > len(df):
                    logger.warning(f"   ⚠️  Filtrados {df_original_count - len(df)} registros con cuentas inexistentes")
                
                # Convertir tipos
                for col in ['periodo_id', 'cuenta_id', 'centro_costo_id']:
                    df[col] = df[col].astype(int)
                for col in ['ingresos', 'costos', 'gastos', 'utilidad_bruta', 'utilidad_neta']:
                    df[col] = df[col].astype(float).round(2)
                
                # Si periodo_id es secuencial (1,2,3...) convertir a formato YYYYMM
                if df['periodo_id'].min() < 1000:
                    logger.info(f"   🔄 Convirtiendo periodo_id secuencial a formato YYYYMM...")
                    # Asumir que 1=Ene 2024 (202401), 2=Feb 2024 (202402), etc.
                    df['periodo_id'] = 202400 + df['periodo_id']
                
                # Generar fecha_id desde periodo_id (YYYYMM → YYYYMM01)
                df['fecha_id'] = (df['periodo_id'] * 100 + 1).astype(int)
                
                # Agregar surrogate key (PK)
                df.insert(0, 'estado_resultados_id', range(1, len(df) + 1))
                    
                logger.info(f"   ✓ fact_estado_resultados: {len(df):,} registros desde CSV")
                logger.info(f"   Períodos: {sorted(df['periodo_id'].unique())}")
                return df
            except Exception as e:
                logger.warning(f"   ⚠️  Error leyendo CSV: {e}")
        
        # Si no hay CSV, intentar construir desde fact_transacciones
        logger.info("   📈 Construyendo desde fact_transacciones...")
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
            
            # Generar fecha_id desde periodo_id (YYYYMM → YYYYMM01)
            result['fecha_id'] = (result['periodo_id'] * 100 + 1).astype(int)
            
            # Agregar surrogate key (PK)
            result.insert(0, 'estado_resultados_id', range(1, len(result) + 1))
            
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
