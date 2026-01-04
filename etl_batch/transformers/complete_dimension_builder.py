#!/usr/bin/env python3
"""
DIMENSION TRANSFORMERS - Transformadores completos para todas las dimensiones
Puebla dimensiones con datos reales desde OroCommerce, OroCRM y CSVs
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CompleteDimensionBuilder:
    """Constructor completo de todas las dimensiones del DW"""
    
    def __init__(self):
        self.oro_conn = self._get_oro_connection()
        self.crm_conn = self._get_crm_connection()
        
    def _get_oro_connection(self):
        """Conexión a OroCommerce"""
        return psycopg2.connect(
            host=os.getenv('ORO_DB_HOST'),
            port=int(os.getenv('ORO_DB_PORT')),
            dbname=os.getenv('ORO_DB_NAME'),
            user=os.getenv('ORO_DB_USER'),
            password=os.getenv('ORO_DB_PASS')
        )
    
    def _get_crm_connection(self):
        """Conexión a OroCRM"""
        return psycopg2.connect(
            host=os.getenv('CRM_DB_HOST'),
            port=int(os.getenv('CRM_DB_PORT')),
            dbname=os.getenv('CRM_DB_NAME'),
            user=os.getenv('CRM_DB_USER'),
            password=os.getenv('CRM_DB_PASS')
        )
    
    # ==================== DIMENSIONES CONFORMADAS ====================
    
    def build_dim_fecha(self) -> pd.DataFrame:
        """Construir dim_fecha completa"""
        logger.info("📅 Construyendo dim_fecha...")
        
        date_range = pd.date_range(start='2020-01-01', end='2030-12-31', freq='D')
        df = pd.DataFrame({'fecha': date_range})
        
        df['fecha_id'] = df['fecha'].apply(lambda x: int(x.strftime('%Y%m%d')))
        df['anio'] = df['fecha'].dt.year
        df['mes'] = df['fecha'].dt.month
        df['dia'] = df['fecha'].dt.day
        df['trimestre'] = df['fecha'].dt.quarter
        df['semana_anio'] = df['fecha'].dt.isocalendar().week
        df['dia_semana'] = df['fecha'].dt.dayofweek + 1
        
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df['dia_semana_nombre'] = df['dia_semana'].apply(lambda x: dias[x-1])
        
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        df['mes_nombre'] = df['mes'].apply(lambda x: meses[x-1])
        
        df['es_fin_semana'] = df['dia_semana'].isin([6, 7])
        df['es_festivo'] = False  # Se puede enriquecer con días festivos reales
        df['nombre_festivo'] = None
        
        logger.info(f"✓ dim_fecha: {len(df):,} registros")
        return df
    
    def build_dim_usuario(self) -> pd.DataFrame:
        """Construir dim_usuario desde oro_user"""
        logger.info("👤 Construyendo dim_usuario...")
        
        query = """
        SELECT 
            id as usuario_externo_id,
            username,
            email,
            first_name as nombre,
            last_name as apellido,
            CONCAT(first_name, ' ', last_name) as nombre_completo,
            enabled as activo,
            created_at
        FROM oro_user
        WHERE enabled = true
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        logger.info(f"✓ dim_usuario: {len(df):,} registros desde oro_user")
        return df
    
    def build_dim_producto(self) -> pd.DataFrame:
        """Construir dim_producto desde oro_product"""
        logger.info("📦 Construyendo dim_producto...")
        
        query = """
        SELECT 
            id as producto_externo_id,
            sku,
            name as nombre,
            type as tipo,
            created_at,
            updated_at,
            CASE WHEN status = 'enabled' THEN true ELSE false END as activo
        FROM oro_product
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['descripcion'] = df['nombre']
        df['categoria'] = 'Calzado'
        df['marca'] = df['nombre'].str.split().str[0]
        df['unidad_medida'] = 'Pieza'
        df['precio_base'] = 0.0
        df['costo_estandar'] = 0.0
        
        logger.info(f"✓ dim_producto: {len(df):,} registros desde oro_product")
        return df
    
    # ==================== DIMENSIONES DE VENTAS ====================
    
    def build_dim_cliente(self) -> pd.DataFrame:
        """Construir dim_cliente desde oro_customer"""
        logger.info("👥 Construyendo dim_cliente...")
        
        query = """
        SELECT 
            id as cliente_externo_id,
            name as nombre,
            website_id as sitio_web_id,
            created_at as fecha_registro
        FROM oro_customer
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['codigo_cliente'] = 'CLI-' + df['cliente_externo_id'].astype(str).str.zfill(6)
        df['tipo_cliente'] = 'B2B'
        df['segmento'] = 'Regular'
        df['email'] = None
        df['telefono'] = None
        df['activo'] = True
        
        logger.info(f"✓ dim_cliente: {len(df):,} registros desde oro_customer")
        return df
    
    def build_dim_sitio_web(self) -> pd.DataFrame:
        """Construir dim_sitio_web desde oro_website"""
        logger.info("🌐 Construyendo dim_sitio_web...")
        
        query = """
        SELECT 
            id as sitio_externo_id,
            name as nombre,
            created_at,
            updated_at
        FROM oro_website
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['url'] = 'https://puntafina.com'
        df['activo'] = True
        
        logger.info(f"✓ dim_sitio_web: {len(df):,} registros desde oro_website")
        return df
    
    def build_dim_canal(self) -> pd.DataFrame:
        """Construir dim_canal desde orocrm_channel"""
        logger.info("📡 Construyendo dim_canal...")
        
        try:
            query = """
            SELECT 
                id as canal_externo_id,
                name as nombre,
                channel_type as tipo,
                status as estado
            FROM orocrm_channel
            ORDER BY id
            """
            df = pd.read_sql_query(query, self.oro_conn)
        except:
            # Si no existe la tabla, crear canales por defecto
            df = pd.DataFrame({
                'canal_externo_id': [1, 2, 3, 4],
                'nombre': ['E-Commerce', 'Tienda Física', 'Mayorista', 'Distribuidores'],
                'tipo': ['b2c', 'retail', 'b2b', 'wholesale'],
                'estado': ['activo', 'activo', 'activo', 'activo']
            })
        
        df['activo'] = df['estado'] == 'activo'
        logger.info(f"✓ dim_canal: {len(df):,} registros")
        return df
    
    def build_dim_direccion(self) -> pd.DataFrame:
        """Construir dim_direccion desde oro_order_address"""
        logger.info("📍 Construyendo dim_direccion...")
        
        query = """
        SELECT DISTINCT
            id as direccion_externo_id,
            street as calle,
            city as ciudad,
            postal_code as codigo_postal,
            region_text as region,
            country_iso2 as pais_codigo,
            CONCAT_WS(', ', street, city, region_text, country_iso2) as direccion_completa
        FROM oro_order_address
        WHERE street IS NOT NULL
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['activo'] = True
        
        logger.info(f"✓ dim_direccion: {len(df):,} registros desde oro_order_address")
        return df
    
    def build_dim_orden(self) -> pd.DataFrame:
        """Construir dim_orden desde oro_order"""
        logger.info("📋 Construyendo dim_orden...")
        
        query = """
        SELECT 
            id as orden_externo_id,
            identifier as numero_orden,
            currency,
            created_at
        FROM oro_order
        ORDER BY id
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['tipo_orden'] = 'Venta'
        df['canal'] = 'E-Commerce'
        df['tasa_cambio'] = 1.0
        
        logger.info(f"✓ dim_orden: {len(df):,} registros desde oro_order")
        return df
    
    def build_dim_line_item(self) -> pd.DataFrame:
        """Construir dim_line_item desde oro_order_line_item"""
        logger.info("📝 Construyendo dim_line_item...")
        
        query = """
        SELECT 
            id as line_item_externo_id,
            order_id,
            product_id
        FROM oro_order_line_item
        ORDER BY id
        LIMIT 5000
        """
        
        df = pd.read_sql_query(query, self.oro_conn)
        df['numero_linea'] = df.groupby('order_id').cumcount() + 1
        df['tipo_linea'] = 'Producto'
        
        logger.info(f"✓ dim_line_item: {len(df):,} registros desde oro_order_line_item")
        return df
    
    # ==================== DIMENSIONES DESDE CSV ====================
    
    def build_dim_envio(self) -> pd.DataFrame:
        """Construir dim_envio desde CSV"""
        logger.info("🚚 Construyendo dim_envio desde CSV...")
        
        csv_path = '../data/inputs/ventas/metodos_envio.csv'
        df = pd.read_csv(csv_path)
        df = df.rename(columns={'id': 'envio_externo_id'})
        df['metodo_envio'] = df['nombre']
        df['tiempo_entrega'] = df['tiempo_entrega_dias'].astype(str) + ' días'
        df['costo'] = df['costo_base']
        
        logger.info(f"✓ dim_envio: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_estado_orden(self) -> pd.DataFrame:
        """Construir dim_estado_orden desde CSV"""
        logger.info("📊 Construyendo dim_estado_orden desde CSV...")
        
        csv_path = '../data/inputs/ventas/estados_orden.csv'
        df = pd.read_csv(csv_path)
        df = df.rename(columns={'id': 'estado_orden_externo_id'})
        df['codigo'] = df['id']
        
        logger.info(f"✓ dim_estado_orden: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_estado_pago(self) -> pd.DataFrame:
        """Construir dim_estado_pago desde CSV"""
        logger.info("💳 Construyendo dim_estado_pago desde CSV...")
        
        csv_path = '../data/inputs/ventas/estados_pago.csv'
        df = pd.read_csv(csv_path)
        df = df.rename(columns={'id': 'estado_pago_externo_id'})
        df['codigo'] = df['id']
        
        logger.info(f"✓ dim_estado_pago: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_pago(self) -> pd.DataFrame:
        """Construir dim_pago con métodos de pago comunes"""
        logger.info("💰 Construyendo dim_pago...")
        
        df = pd.DataFrame({
            'pago_externo_id': range(1, 11),
            'metodo_pago': ['Efectivo', 'Tarjeta Crédito', 'Tarjeta Débito', 'Transferencia',
                           'Cheque', 'PayPal', 'Stripe', 'Bitcoin', 'Crédito 30 días', 'Crédito 60 días'],
            'procesador': ['Manual', 'Visa/MC', 'Visa/MC', 'Banco',
                          'Banco', 'PayPal', 'Stripe', 'Blockchain', 'Interno', 'Interno'],
            'tipo_pago': ['Inmediato', 'Inmediato', 'Inmediato', 'Inmediato',
                         'Diferido', 'Inmediato', 'Inmediato', 'Inmediato', 'Crédito', 'Crédito']
        })
        
        logger.info(f"✓ dim_pago: {len(df):,} registros")
        return df
    
    def build_dim_impuestos(self) -> pd.DataFrame:
        """Construir dim_impuestos"""
        logger.info("📊 Construyendo dim_impuestos...")
        
        df = pd.DataFrame({
            'impuesto_externo_id': range(1, 6),
            'codigo': ['IVA', 'ISR', 'IMPCONS', 'IMPADVAL', 'EXENTO'],
            'nombre': ['IVA 13%', 'ISR', 'Impuesto al Consumo', 'Ad Valorem', 'Exento'],
            'tasa': [0.13, 0.25, 0.15, 0.05, 0.0],
            'tipo': ['ventas', 'renta', 'especial', 'importación', 'exento']
        })
        df['activo'] = True
        
        logger.info(f"✓ dim_impuestos: {len(df):,} registros")
        return df
    
    def build_dim_promocion(self) -> pd.DataFrame:
        """Construir dim_promocion desde oro_promotion"""
        logger.info("🎁 Construyendo dim_promocion...")
        
        try:
            query = """
            SELECT 
                id as promocion_externo_id,
                rule_label as nombre,
                created_at,
                updated_at
            FROM oro_promotion
            ORDER BY id
            """
            df = pd.read_sql_query(query, self.oro_conn)
            df['codigo'] = 'PROMO-' + df['promocion_externo_id'].astype(str).str.zfill(4)
            df['descripcion'] = df['nombre']
            df['tipo_descuento'] = 'Porcentaje'
            df['valor_descuento'] = 10.0
            df['fecha_inicio'] = pd.to_datetime('2024-01-01')
            df['fecha_fin'] = pd.to_datetime('2024-12-31')
        except:
            # Si no hay promociones, crear vacío
            df = pd.DataFrame(columns=['promocion_externo_id', 'codigo', 'nombre', 'descripcion',
                                      'tipo_descuento', 'valor_descuento', 'fecha_inicio', 'fecha_fin'])
        
        logger.info(f"✓ dim_promocion: {len(df):,} registros")
        return df
    
    # ==================== DIMENSIONES DE INVENTARIO ====================
    
    def build_dim_almacen(self) -> pd.DataFrame:
        """Construir dim_almacen desde CSV"""
        logger.info("🏪 Construyendo dim_almacen desde CSV...")
        
        csv_path = '../data/inputs/inventario/almacenes.csv'
        df = pd.read_csv(csv_path)
        df['tipo'] = 'Almacén'
        
        logger.info(f"✓ dim_almacen: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_proveedor(self) -> pd.DataFrame:
        """Construir dim_proveedor desde CSV"""
        logger.info("🏭 Construyendo dim_proveedor desde CSV...")
        
        csv_path = '../data/inputs/inventario/proveedores.csv'
        df = pd.read_csv(csv_path)
        
        logger.info(f"✓ dim_proveedor: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_tipo_movimiento(self) -> pd.DataFrame:
        """Construir dim_tipo_movimiento desde CSV"""
        logger.info("📦 Construyendo dim_tipo_movimiento desde CSV...")
        
        csv_path = '../data/inputs/inventario/tipos_movimiento.csv'
        df = pd.read_csv(csv_path)
        
        logger.info(f"✓ dim_tipo_movimiento: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_categoria_producto(self) -> pd.DataFrame:
        """Construir dim_categoria_producto"""
        logger.info("📂 Construyendo dim_categoria_producto...")
        
        df = pd.DataFrame({
            'categoria_externo_id': range(1, 11),
            'codigo': ['CAT001', 'CAT002', 'CAT003', 'CAT004', 'CAT005',
                      'CAT006', 'CAT007', 'CAT008', 'CAT009', 'CAT010'],
            'nombre': ['Calzado Deportivo', 'Calzado Casual', 'Calzado Formal',
                      'Botas', 'Sandalias', 'Zapatos de Niño', 'Zapatos de Mujer',
                      'Zapatos de Hombre', 'Accesorios', 'Otros'],
            'descripcion': ['Zapatillas deportivas', 'Zapatos casuales', 'Zapatos formales',
                          'Botas diversas', 'Sandalias verano', 'Calzado infantil',
                          'Calzado femenino', 'Calzado masculino', 'Accesorios varios', 'Otros productos'],
            'categoria_padre_id': [None, None, None, None, None, None, None, None, None, None],
            'nivel': [1] * 10,
            'activo': [True] * 10
        })
        
        logger.info(f"✓ dim_categoria_producto: {len(df):,} registros")
        return df
    
    # ==================== DIMENSIONES DE FINANZAS ====================
    
    def build_dim_cuenta_contable(self) -> pd.DataFrame:
        """Construir dim_cuenta_contable desde CSV"""
        logger.info("💼 Construyendo dim_cuenta_contable desde CSV...")
        
        csv_path = '../data/inputs/finanzas/cuentas_contables.csv'
        df = pd.read_csv(csv_path)
        
        logger.info(f"✓ dim_cuenta_contable: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_centro_costo(self) -> pd.DataFrame:
        """Construir dim_centro_costo desde CSV"""
        logger.info("🏢 Construyendo dim_centro_costo desde CSV...")
        
        csv_path = '../data/inputs/finanzas/centros_costo.csv'
        df = pd.read_csv(csv_path)
        
        logger.info(f"✓ dim_centro_costo: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_tipo_transaccion(self) -> pd.DataFrame:
        """Construir dim_tipo_transaccion desde CSV"""
        logger.info("📋 Construyendo dim_tipo_transaccion desde CSV...")
        
        csv_path = '../data/inputs/finanzas/tipos_transaccion.csv'
        df = pd.read_csv(csv_path)
        
        logger.info(f"✓ dim_tipo_transaccion: {len(df):,} registros desde CSV")
        return df
    
    def build_dim_periodo_contable(self) -> pd.DataFrame:
        """Construir dim_periodo_contable"""
        logger.info("📅 Construyendo dim_periodo_contable...")
        
        periodos = []
        for anio in range(2020, 2027):
            for mes in range(1, 13):
                periodo_id = anio * 100 + mes
                trimestre = (mes - 1) // 3 + 1
                nombre = f"{anio}-{mes:02d}"
                fecha_inicio = pd.to_datetime(f"{anio}-{mes:02d}-01")
                
                if mes == 12:
                    fecha_fin = pd.to_datetime(f"{anio}-12-31")
                else:
                    siguiente_mes = fecha_inicio + pd.DateOffset(months=1)
                    fecha_fin = siguiente_mes - pd.DateOffset(days=1)
                
                periodos.append({
                    'periodo_id': periodo_id,
                    'anio': anio,
                    'mes': mes,
                    'trimestre': trimestre,
                    'nombre_periodo': nombre,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'cerrado': False
                })
        
        df = pd.DataFrame(periodos)
        logger.info(f"✓ dim_periodo_contable: {len(df):,} registros")
        return df
    
    def __del__(self):
        """Cerrar conexiones"""
        try:
            self.oro_conn.close()
            self.crm_conn.close()
        except:
            pass
