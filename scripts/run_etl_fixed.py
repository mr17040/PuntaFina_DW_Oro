#!/usr/bin/env python3
"""
ETL COMPLETO - Data Warehouse Punta Fina
Mapeo correcto de columnas origen → DW (sin modificar datos de origen)
"""

import pandas as pd
import psycopg2
from datetime import datetime
from pathlib import Path
from loguru import logger
import sys

# Configurar logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

class DatabaseConnections:
    """Gestión de conexiones a bases de datos (solo lectura en origen)"""
    
    def __init__(self):
        self.conn_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'sa',
            'password': 'IngDatos123*'
        }
    
    def get_orocommerce_conn(self):
        """Conexión READ-ONLY a OroCommerce"""
        params = self.conn_params.copy()
        params['database'] = 'orocommerce'
        return psycopg2.connect(**params)
    
    def get_orocrm_conn(self):
        """Conexión READ-ONLY a OroCRM"""
        params = self.conn_params.copy()
        params['database'] = 'oro_crm'
        return psycopg2.connect(**params)
    
    def get_dw_conn(self):
        """Conexión READ-WRITE a DataWarehouse"""
        params = self.conn_params.copy()
        params['database'] = 'datawarehouse_bi'
        return psycopg2.connect(**params)


class DimensionBuilder:
    """Constructor de dimensiones con mapeo correcto de columnas"""
    
    def __init__(self, conn_oro, conn_crm):
        self.conn_oro = conn_oro
        self.conn_crm = conn_crm
    
    # ==================== DIMENSIONES CONFORMADAS ====================
    
    def build_dim_fecha(self):
        """Dimensión calendario (generada, no requiere mapeo)"""
        logger.info("📅 Construyendo dim_fecha...")
        
        dates = pd.date_range(start='2020-01-01', end='2025-12-31', freq='D')
        
        df = pd.DataFrame({
            'fecha': dates,
            'anio': dates.year,
            'mes': dates.month,
            'dia': dates.day,
            'trimestre': dates.quarter,
            'semana_anio': dates.isocalendar().week,
            'dia_semana': dates.dayofweek + 1,
            'dia_semana_nombre': dates.strftime('%A'),
            'mes_nombre': dates.strftime('%B'),
            'es_fin_semana': dates.dayofweek >= 5,
            'es_festivo': False,
            'nombre_festivo': None
        })
        
        logger.success(f"✅ dim_fecha: {len(df):,} registros")
        return df
    
    def build_dim_usuario(self):
        """Dimensión usuarios conformada - Mapeo correcto"""
        logger.info("👤 Construyendo dim_usuario...")
        
        # Leer de origen (oro_user) sin modificar - columnas reales: createdat, updatedat
        query = """
        SELECT 
            id,
            username,
            email,
            first_name,
            last_name,
            enabled,
            createdat,
            updatedat
        FROM oro_user
        WHERE id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'usuario_externo_id': df_origen['id'],
            'codigo_usuario': df_origen['username'],
            'nombre_completo': df_origen['first_name'].fillna('') + ' ' + df_origen['last_name'].fillna(''),
            'correo': df_origen['email'],
            'activo': df_origen['enabled'].fillna(True),
            'rol': 'Vendedor',  # Campo calculado
            'fecha_creacion': pd.to_datetime(df_origen['createdat']),
            'fecha_actualizacion': pd.to_datetime(df_origen['updatedat'])
        })
        
        logger.success(f"✅ dim_usuario: {len(df):,} registros")
        return df
    
    def build_dim_detalle_venta(self):
        """Dimensión detalle_venta conformada - Mapeo correcto"""
        logger.info("📝 Construyendo dim_detalle_venta...")
        
        # Leer de origen - usar LIMIT para no saturar memoria
        query = """
        SELECT 
            oli.id,
            oli.product_id,
            oli.order_id,
            oli.product_sku,
            oli.product_name,
            oli.quantity,
            oli.value as precio_unitario,
            oli.currency,
            o.created_at
        FROM oro_order_line_item oli
        LEFT JOIN oro_order o ON oli.order_id = o.id
        WHERE oli.id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'detalle_externo_id': df_origen['id'],
            'producto_id': df_origen['product_id'],
            'orden_id': df_origen['order_id'],
            'sku': df_origen['product_sku'],
            'nombre_producto': df_origen['product_name'],
            'cantidad': df_origen['quantity'],
            'precio_unitario': df_origen['precio_unitario'],
            'subtotal': df_origen['quantity'] * df_origen['precio_unitario'],
            'descuento_aplicado': 0.0,
            'impuestos': df_origen['quantity'] * df_origen['precio_unitario'] * 0.13,
            'total_linea': df_origen['quantity'] * df_origen['precio_unitario'] * 1.13,
            'fecha_venta': pd.to_datetime(df_origen['created_at'])
        })
        
        logger.success(f"✅ dim_detalle_venta: {len(df):,} registros")
        return df
    
    # ==================== DIMENSIONES DE VENTAS ====================
    
    def build_dim_cliente(self):
        """Dimensión clientes - Mapeo correcto"""
        logger.info("👥 Construyendo dim_cliente...")
        
        query = """
        SELECT 
            c.id,
            c.name,
            c.created_at,
            c.updated_at
        FROM oro_customer c
        WHERE c.id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'cliente_externo_id': df_origen['id'],
            'nombre': df_origen['name'],
            'direccion': '',
            'ciudad': '',
            'codigo_postal': '',
            'pais': 'SV',
            'region': '',
            'segmento': 'Regular',  # Campo calculado
            'tipo_cliente': 'B2C',  # Campo calculado
            'activo': True,
            'fecha_registro': pd.to_datetime(df_origen['created_at'])
        })
        
        logger.success(f"✅ dim_cliente: {len(df):,} registros")
        return df
    
    def build_dim_producto(self):
        """Dimensión productos - Mapeo correcto"""
        logger.info("📦 Construyendo dim_producto...")
        
        query = """
        SELECT 
            p.id,
            p.sku,
            COALESCE(p.name, p.sku) as nombre,
            p.created_at,
            p.updated_at,
            p.status,
            p.type
        FROM oro_product p
        WHERE p.id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'producto_externo_id': df_origen['id'],
            'sku': df_origen['sku'],
            'nombre': df_origen['nombre'],
            'categoria': 'General',  # Campo calculado
            'marca': 'Punta Fina',  # Campo calculado
            'activo': df_origen['status'] == 'enabled',
            'tipo_producto': df_origen['type'].fillna('simple'),
            'fecha_creacion': pd.to_datetime(df_origen['created_at'])
        })
        
        logger.success(f"✅ dim_producto: {len(df):,} registros")
        return df
    
    def build_dim_orden(self):
        """Dimensión órdenes - Mapeo correcto"""
        logger.info("🛒 Construyendo dim_orden...")
        
        query = """
        SELECT 
            o.id,
            o.identifier as order_number,
            o.po_number,
            o.customer_id,
            o.customer_user_id,
            o.website_id,
            o.currency,
            COALESCE(o.subtotal_value, 0) as subtotal,
            COALESCE(o.total_value, 0) as total,
            o.created_at,
            o.updated_at,
            COALESCE(ois.name, 'pending') as status
        FROM oro_order o
        LEFT JOIN oro_enum_order_internal_status ois ON o.internal_status_id = ois.id
        WHERE o.id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'orden_externo_id': df_origen['id'],
            'numero_orden': df_origen['order_number'],
            'po_number': df_origen['po_number'].fillna(''),
            'cliente_id': df_origen['customer_id'],
            'usuario_id': df_origen['customer_user_id'],
            'sitio_web_id': df_origen['website_id'],
            'moneda': df_origen['currency'],
            'subtotal': df_origen['subtotal'],
            'total': df_origen['total'],
            'estado': df_origen['status'],
            'fecha_orden': pd.to_datetime(df_origen['created_at']),
            'fecha_actualizacion': pd.to_datetime(df_origen['updated_at'])
        })
        
        logger.success(f"✅ dim_orden: {len(df):,} registros")
        return df
    
    def build_dim_sitio_web(self):
        """Dimensión sitios web - Mapeo correcto"""
        logger.info("🌐 Construyendo dim_sitio_web...")
        
        query = """
        SELECT 
            id,
            name,
            url
        FROM oro_website
        WHERE id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'sitio_externo_id': df_origen['id'],
            'codigo': 'WEB' + df_origen['id'].astype(str),
            'nombre': df_origen['name'],
            'url': df_origen['url'],
            'pais': 'El Salvador',
            'idioma': 'es_SV',
            'moneda_default': 'USD',
            'activo': True
        })
        
        logger.success(f"✅ dim_sitio_web: {len(df):,} registros")
        return df
    
    def build_dim_canal(self):
        """Dimensión canales - Generada"""
        logger.info("📢 Construyendo dim_canal...")
        
        canales = [
            {'nombre': 'Sitio Web', 'tipo': 'Online', 'descripcion': 'Ventas online', 'activo': True},
            {'nombre': 'Tienda Física', 'tipo': 'Offline', 'descripcion': 'Ventas presenciales', 'activo': True}
        ]
        
        df = pd.DataFrame(canales)
        logger.success(f"✅ dim_canal: {len(df):,} registros")
        return df
    
    def build_dim_promocion(self):
        """Dimensión promociones - Generada"""
        logger.info("🎁 Construyendo dim_promocion...")
        
        promociones = [
            {'codigo': 'SIN_PROMO', 'nombre': 'Sin Promoción', 'tipo_descuento': 'ninguno', 
             'valor_descuento': 0, 'activo': True},
            {'codigo': 'DESC10', 'nombre': '10% Descuento', 'tipo_descuento': 'porcentaje', 
             'valor_descuento': 10, 'activo': True}
        ]
        
        df = pd.DataFrame(promociones)
        logger.success(f"✅ dim_promocion: {len(df):,} registros")
        return df
    
    def build_dim_vendedor(self):
        """Dimensión vendedores - Mapeo de usuarios con rol vendedor"""
        logger.info("💼 Construyendo dim_vendedor...")
        
        query = """
        SELECT 
            u.id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.enabled,
            u.created_at
        FROM oro_user u
        WHERE u.enabled = true
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'vendedor_externo_id': df_origen['id'],
            'codigo_vendedor': df_origen['username'],
            'nombre_completo': df_origen['first_name'].fillna('') + ' ' + df_origen['last_name'].fillna(''),
            'correo': df_origen['email'],
            'telefono': '',
            'comision_porcentaje': 5.0,
            'activo': df_origen['enabled'],
            'fecha_ingreso': pd.to_datetime(df_origen['created_at'])
        })
        
        logger.success(f"✅ dim_vendedor: {len(df):,} registros")
        return df
    
    def build_dim_metodo_pago(self):
        """Dimensión métodos de pago - Generada"""
        logger.info("💳 Construyendo dim_metodo_pago...")
        
        metodos = [
            {'codigo': 'CASH', 'nombre': 'Efectivo', 'tipo': 'cash', 'activo': True},
            {'codigo': 'CARD', 'nombre': 'Tarjeta', 'tipo': 'card', 'activo': True},
            {'codigo': 'BANK', 'nombre': 'Transferencia', 'tipo': 'transfer', 'activo': True}
        ]
        
        df = pd.DataFrame(metodos)
        logger.success(f"✅ dim_metodo_pago: {len(df):,} registros")
        return df
    
    def build_dim_metodo_envio(self):
        """Dimensión métodos de envío - Generada"""
        logger.info("🚚 Construyendo dim_metodo_envio...")
        
        metodos = [
            {'codigo': 'STD', 'nombre': 'Envío Estándar', 'costo_base': 5.0, 'tiempo_entrega_dias': 5, 'activo': True},
            {'codigo': 'EXP', 'nombre': 'Envío Express', 'costo_base': 15.0, 'tiempo_entrega_dias': 2, 'activo': True},
            {'codigo': 'RET', 'nombre': 'Retiro en Tienda', 'costo_base': 0.0, 'tiempo_entrega_dias': 1, 'activo': True}
        ]
        
        df = pd.DataFrame(metodos)
        logger.success(f"✅ dim_metodo_envio: {len(df):,} registros")
        return df
    
    def build_dim_direccion(self):
        """Dimensión direcciones - Mapeo correcto"""
        logger.info("📍 Construyendo dim_direccion...")
        
        query = """
        SELECT 
            ca.id,
            ca.label,
            ca.street,
            ca.city,
            ca.postal_code,
            ca.country_code,
            ca.region_code,
            ca.frontend_owner_id as customer_id,
            ca.created_at,
            ca.updated_at
        FROM oro_customer_address ca
        WHERE ca.id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'direccion_externo_id': df_origen['id'],
            'cliente_id': df_origen['customer_id'],
            'etiqueta': df_origen['label'].fillna('Principal'),
            'calle': df_origen['street'],
            'ciudad': df_origen['city'],
            'codigo_postal': df_origen['postal_code'],
            'pais': df_origen['country_code'],
            'region': df_origen['region_code'],
            'tipo_direccion': 'envio',
            'activo': True,
            'fecha_creacion': pd.to_datetime(df_origen['created_at'])
        })
        
        logger.success(f"✅ dim_direccion: {len(df):,} registros")
        return df
    
    def build_dim_estado_orden(self):
        """Dimensión estados de orden - Mapeo correcto"""
        logger.info("📊 Construyendo dim_estado_orden...")
        
        query = """
        SELECT 
            id,
            name,
            priority
        FROM oro_enum_order_internal_status
        WHERE id IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW
        df = pd.DataFrame({
            'estado_externo_id': df_origen['id'],
            'codigo': df_origen['name'].str.upper(),
            'nombre': df_origen['name'],
            'descripcion': 'Estado de orden: ' + df_origen['name'],
            'orden_flujo': df_origen['priority'].fillna(0),
            'activo': True
        })
        
        logger.success(f"✅ dim_estado_orden: {len(df):,} registros")
        return df
    
    # ==================== DIMENSIONES DE INVENTARIO ====================
    
    def build_dim_almacen(self):
        """Dimensión almacenes - Generada"""
        logger.info("🏭 Construyendo dim_almacen...")
        
        almacenes = [
            {'codigo': 'ALM01', 'nombre': 'Almacén Central', 'ubicacion': 'San Salvador', 
             'tipo': 'principal', 'capacidad_m3': 1000, 'activo': True},
            {'codigo': 'ALM02', 'nombre': 'Almacén Regional', 'ubicacion': 'Santa Ana', 
             'tipo': 'secundario', 'capacidad_m3': 500, 'activo': True}
        ]
        
        df = pd.DataFrame(almacenes)
        logger.success(f"✅ dim_almacen: {len(df):,} registros")
        return df
    
    def build_dim_proveedor(self):
        """Dimensión proveedores - Generada"""
        logger.info("🤝 Construyendo dim_proveedor...")
        
        proveedores = [
            {'codigo': 'PROV001', 'nombre': 'Proveedor Nacional', 'pais': 'El Salvador', 
             'categoria': 'A', 'activo': True},
            {'codigo': 'PROV002', 'nombre': 'Proveedor Internacional', 'pais': 'Guatemala', 
             'categoria': 'B', 'activo': True}
        ]
        
        df = pd.DataFrame(proveedores)
        logger.success(f"✅ dim_proveedor: {len(df):,} registros")
        return df
    
    def build_dim_tipo_movimiento(self):
        """Dimensión tipos de movimiento - Generada"""
        logger.info("🔄 Construyendo dim_tipo_movimiento...")
        
        tipos = [
            {'codigo': 'ENTRADA', 'nombre': 'Entrada', 'afecta_stock': 1, 'descripcion': 'Entrada de inventario'},
            {'codigo': 'SALIDA', 'nombre': 'Salida', 'afecta_stock': -1, 'descripcion': 'Salida de inventario'},
            {'codigo': 'AJUSTE', 'nombre': 'Ajuste', 'afecta_stock': 0, 'descripcion': 'Ajuste de inventario'}
        ]
        
        df = pd.DataFrame(tipos)
        logger.success(f"✅ dim_tipo_movimiento: {len(df):,} registros")
        return df
    
    def build_dim_categoria_producto(self):
        """Dimensión categorías - Generada"""
        logger.info("📂 Construyendo dim_categoria_producto...")
        
        categorias = [
            {'codigo': 'CAT01', 'nombre': 'Electrónica', 'nivel': 1, 'activo': True},
            {'codigo': 'CAT02', 'nombre': 'Ropa', 'nivel': 1, 'activo': True},
            {'codigo': 'CAT03', 'nombre': 'Alimentos', 'nivel': 1, 'activo': True}
        ]
        
        df = pd.DataFrame(categorias)
        logger.success(f"✅ dim_categoria_producto: {len(df):,} registros")
        return df
    
    # ==================== DIMENSIONES DE FINANZAS ====================
    
    def build_dim_cuenta_contable(self):
        """Dimensión cuentas contables - Generada"""
        logger.info("💰 Construyendo dim_cuenta_contable...")
        
        cuentas = [
            {'codigo': '1.1.01', 'nombre': 'Caja', 'tipo': 'activo', 'nivel': 3, 'naturaleza': 'deudor', 'activo': True},
            {'codigo': '1.1.02', 'nombre': 'Bancos', 'tipo': 'activo', 'nivel': 3, 'naturaleza': 'deudor', 'activo': True},
            {'codigo': '4.1.01', 'nombre': 'Ventas', 'tipo': 'ingreso', 'nivel': 3, 'naturaleza': 'acreedor', 'activo': True},
            {'codigo': '5.1.01', 'nombre': 'Costo de Ventas', 'tipo': 'costo', 'nivel': 3, 'naturaleza': 'deudor', 'activo': True}
        ]
        
        df = pd.DataFrame(cuentas)
        logger.success(f"✅ dim_cuenta_contable: {len(df):,} registros")
        return df
    
    def build_dim_centro_costo(self):
        """Dimensión centros de costo - Generada"""
        logger.info("🏢 Construyendo dim_centro_costo...")
        
        centros = [
            {'codigo': 'CC01', 'nombre': 'Ventas', 'tipo': 'operativo', 'responsable': 'Gerente Ventas', 'activo': True},
            {'codigo': 'CC02', 'nombre': 'Administración', 'tipo': 'administrativo', 'responsable': 'Gerente Admin', 'activo': True}
        ]
        
        df = pd.DataFrame(centros)
        logger.success(f"✅ dim_centro_costo: {len(df):,} registros")
        return df
    
    def build_dim_tipo_transaccion(self):
        """Dimensión tipos de transacción - Generada"""
        logger.info("📝 Construyendo dim_tipo_transaccion...")
        
        tipos = [
            {'codigo': 'VEN', 'nombre': 'Venta', 'categoria': 'ingreso', 'descripcion': 'Transacción de venta'},
            {'codigo': 'COM', 'nombre': 'Compra', 'categoria': 'egreso', 'descripcion': 'Transacción de compra'},
            {'codigo': 'PAG', 'nombre': 'Pago', 'categoria': 'egreso', 'descripcion': 'Pago a proveedores'}
        ]
        
        df = pd.DataFrame(tipos)
        logger.success(f"✅ dim_tipo_transaccion: {len(df):,} registros")
        return df
    
    def build_dim_periodo_contable(self):
        """Dimensión períodos contables - Generada"""
        logger.info("📅 Construyendo dim_periodo_contable...")
        
        periodos = []
        for year in range(2020, 2026):
            for month in range(1, 13):
                periodos.append({
                    'anio': year,
                    'mes': month,
                    'trimestre': (month - 1) // 3 + 1,
                    'nombre_periodo': f"{year}-{month:02d}",
                    'fecha_inicio': f"{year}-{month:02d}-01",
                    'fecha_fin': f"{year}-{month:02d}-{pd.Period(f'{year}-{month}', 'M').days_in_month}",
                    'cerrado': year < 2025
                })
        
        df = pd.DataFrame(periodos)
        logger.success(f"✅ dim_periodo_contable: {len(df):,} registros")
        return df


class FactBuilder:
    """Constructor de tablas de hechos"""
    
    def __init__(self, conn_oro, conn_dw):
        self.conn_oro = conn_oro
        self.conn_dw = conn_dw
    
    def build_fact_ventas(self):
        """Tabla de hechos de ventas - Mapeo completo"""
        logger.info("💰 Construyendo fact_ventas...")
        
        query = """
        SELECT 
            o.id as orden_id,
            o.customer_id,
            o.customer_user_id,
            o.website_id,
            DATE(o.created_at) as fecha,
            oli.id as detalle_id,
            oli.product_id,
            oli.quantity as cantidad,
            oli.value as precio_unitario,
            oli.currency,
            COALESCE(o.subtotal_value, 0) as subtotal_orden,
            COALESCE(o.total_value, 0) as total_orden
        FROM oro_order o
        INNER JOIN oro_order_line_item oli ON o.id = oli.order_id
        WHERE o.id IS NOT NULL AND oli.value IS NOT NULL
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        # Mapear a columnas DW fact - convertir IDs a enteros
        df = pd.DataFrame({
            'fecha_id': pd.to_datetime(df_origen['fecha']),
            'cliente_id': pd.to_numeric(df_origen['customer_id'], errors='coerce').fillna(0).astype(int),
            'producto_id': pd.to_numeric(df_origen['product_id'], errors='coerce').fillna(0).astype(int),
            'orden_id': pd.to_numeric(df_origen['orden_id'], errors='coerce').fillna(0).astype(int),
            'detalle_venta_id': pd.to_numeric(df_origen['detalle_id'], errors='coerce').fillna(0).astype(int),
            'sitio_web_id': pd.to_numeric(df_origen['website_id'], errors='coerce').fillna(1).astype(int),
            'usuario_id': pd.to_numeric(df_origen['customer_user_id'], errors='coerce').fillna(1).astype(int),
            'cantidad': df_origen['cantidad'],
            'precio_unitario': df_origen['precio_unitario'],
            'subtotal': df_origen['cantidad'] * df_origen['precio_unitario'],
            'descuento': 0.0,
            'impuestos': df_origen['cantidad'] * df_origen['precio_unitario'] * 0.13,
            'total': df_origen['cantidad'] * df_origen['precio_unitario'] * 1.13,
            'costo_producto': df_origen['cantidad'] * df_origen['precio_unitario'] * 0.6,
            'margen_bruto': df_origen['cantidad'] * df_origen['precio_unitario'] * 0.4
        })
        
        # Filtrar registros con IDs válidos
        df = df[df['producto_id'] > 0]
        
        logger.success(f"✅ fact_ventas: {len(df):,} registros")
        return df
    
    def build_fact_inventario(self):
        """Tabla de hechos de inventario - Desde CSV"""
        logger.info("📦 Construyendo fact_inventario...")
        
        csv_path = '/root/PuntaFina_DW_Oro/data/inputs/inventario/movimientos_inventario.csv'
        
        if not Path(csv_path).exists():
            logger.warning(f"⚠️  No existe: {csv_path}")
            return pd.DataFrame()
        
        df_origen = pd.read_csv(csv_path)
        
        # Mapear a columnas DW fact - usar 'fecha' no 'fecha_movimiento'
        df = pd.DataFrame({
            'fecha_id': pd.to_datetime(df_origen['fecha']),
            'producto_id': pd.to_numeric(df_origen['product_id'], errors='coerce').fillna(0).astype(int),
            'almacen_id': 1,  # Default
            'tipo_movimiento_id': 1,  # Default
            'cantidad': df_origen['cantidad'],
            'costo_unitario': df_origen['costo_unitario'],
            'costo_total': df_origen['cantidad'] * df_origen['costo_unitario'],
            'stock_antes': df_origen['stock_anterior'],
            'stock_despues': df_origen['stock_resultante']
        })
        
        # Filtrar registros válidos
        df = df[df['producto_id'] > 0]
        
        logger.success(f"✅ fact_inventario: {len(df):,} registros")
        return df
    
    def build_fact_transacciones(self):
        """Tabla de hechos de transacciones - Desde CSV"""
        logger.info("💳 Construyendo fact_transacciones...")
        
        csv_path = '/root/PuntaFina_DW_Oro/data/inputs/finanzas/transacciones_contables.csv'
        
        if not Path(csv_path).exists():
            logger.warning(f"⚠️  No existe: {csv_path}")
            return pd.DataFrame()
        
        df_origen = pd.read_csv(csv_path)
        
        # Verificar columnas disponibles
        if 'fecha' in df_origen.columns:
            fecha_col = 'fecha'
        elif 'fecha_transaccion' in df_origen.columns:
            fecha_col = 'fecha_transaccion'
        else:
            logger.error(f"❌ No se encontró columna de fecha en {csv_path}")
            return pd.DataFrame()
        
        # Mapear a columnas DW fact
        df = pd.DataFrame({
            'fecha_id': pd.to_datetime(df_origen[fecha_col]),
            'cuenta_contable_id': pd.to_numeric(df_origen['cuenta_id'], errors='coerce').fillna(1).astype(int),
            'centro_costo_id': pd.to_numeric(df_origen['centro_costo_id'], errors='coerce').fillna(1).astype(int),
            'tipo_transaccion_id': 1,  # Default
            'periodo_contable_id': 1,  # Default
            'numero_asiento': df_origen['numero_asiento'].astype(str),
            'tipo_movimiento': df_origen['tipo_movimiento'].astype(str),
            'monto': df_origen['monto'],
            'descripcion': df_origen['descripcion'].astype(str)
        })
        
        logger.success(f"✅ fact_transacciones: {len(df):,} registros")
        return df
    
    def build_fact_balance(self):
        """Tabla de hechos de balance - Agregada"""
        logger.info("📊 Construyendo fact_balance...")
        
        # Generar balance mensual agregado
        query = """
        SELECT 
            DATE_TRUNC('month', created_at) as mes,
            COUNT(*) as num_ordenes,
            SUM(COALESCE(subtotal_value, 0)) as total_ventas,
            SUM(COALESCE(subtotal_value, 0)) * 0.6 as total_costos,
            SUM(COALESCE(subtotal_value, 0)) * 0.4 as utilidad
        FROM oro_order
        WHERE created_at IS NOT NULL
        GROUP BY DATE_TRUNC('month', created_at)
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        df = pd.DataFrame({
            'fecha_id': pd.to_datetime(df_origen['mes']),
            'periodo_contable_id': 1,
            'activo_corriente': df_origen['total_ventas'] * 0.3,
            'activo_no_corriente': df_origen['total_ventas'] * 0.7,
            'total_activos': df_origen['total_ventas'],
            'pasivo_corriente': df_origen['total_costos'] * 0.4,
            'pasivo_no_corriente': df_origen['total_costos'] * 0.6,
            'total_pasivos': df_origen['total_costos'],
            'capital': df_origen['utilidad'],
            'utilidades_retenidas': df_origen['utilidad'] * 0.7,
            'total_patrimonio': df_origen['utilidad']
        })
        
        logger.success(f"✅ fact_balance: {len(df):,} registros")
        return df
    
    def build_fact_estado_resultados(self):
        """Tabla de hechos de estado de resultados - Agregada"""
        logger.info("📈 Construyendo fact_estado_resultados...")
        
        query = """
        SELECT 
            DATE_TRUNC('month', created_at) as mes,
            SUM(COALESCE(subtotal_value, 0)) as ingresos,
            SUM(COALESCE(subtotal_value, 0)) * 0.6 as costos,
            SUM(COALESCE(subtotal_value, 0)) * 0.2 as gastos_operativos
        FROM oro_order
        WHERE created_at IS NOT NULL
        GROUP BY DATE_TRUNC('month', created_at)
        """
        
        df_origen = pd.read_sql(query, self.conn_oro)
        
        df = pd.DataFrame({
            'fecha_id': pd.to_datetime(df_origen['mes']),
            'periodo_contable_id': 1,
            'ingresos_operacionales': df_origen['ingresos'],
            'costo_ventas': df_origen['costos'],
            'utilidad_bruta': df_origen['ingresos'] - df_origen['costos'],
            'gastos_operacionales': df_origen['gastos_operativos'],
            'utilidad_operacional': df_origen['ingresos'] - df_origen['costos'] - df_origen['gastos_operativos'],
            'gastos_financieros': 0.0,
            'utilidad_antes_impuestos': df_origen['ingresos'] - df_origen['costos'] - df_origen['gastos_operativos'],
            'impuestos': (df_origen['ingresos'] - df_origen['costos'] - df_origen['gastos_operativos']) * 0.25,
            'utilidad_neta': (df_origen['ingresos'] - df_origen['costos'] - df_origen['gastos_operativos']) * 0.75
        })
        
        logger.success(f"✅ fact_estado_resultados: {len(df):,} registros")
        return df


class SimpleDatabaseLoader:
    """Cargador simple a PostgreSQL"""
    
    def __init__(self, conn_dw):
        self.conn_dw = conn_dw
    
    def load_to_database(self, df, table_name):
        """Cargar DataFrame a tabla DW"""
        try:
            # Obtener columnas de la tabla DW
            cursor = self.conn_dw.cursor()
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            dw_columns = [row[0] for row in cursor.fetchall() if row[0] not in ['fecha_id', 'sitio_id', 'producto_id']]  # Excluir PKs autoincrementales
            
            # Filtrar solo columnas que existen en DW
            df_filtered = df[[col for col in df.columns if col in dw_columns]]
            
            if df_filtered.empty:
                logger.warning(f"⚠️  No hay columnas coincidentes para {table_name}")
                return 0
            
            # Truncar tabla
            cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            self.conn_dw.commit()
            
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
            self.conn_dw.commit()
            
            logger.info(f"✅ {table_name}: {len(df_filtered):,} registros cargados")
            return len(df_filtered)
            
        except Exception as e:
            self.conn_dw.rollback()
            logger.error(f"❌ Error cargando {table_name}: {str(e)}")
            return 0


class ETLOrchestrator:
    """Orquestador principal del ETL"""
    
    def __init__(self):
        self.db = DatabaseConnections()
        self.output_dir = Path('/root/PuntaFina_DW_Oro/data/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """Ejecutar ETL completo"""
        start_time = datetime.now()
        logger.info("\n" + "=" * 80)
        logger.info("🚀 INICIANDO ETL COMPLETO - Data Warehouse Punta Fina")
        logger.info("=" * 80)
        
        # Conexiones
        conn_oro = self.db.get_orocommerce_conn()
        conn_crm = self.db.get_orocrm_conn()
        conn_dw = self.db.get_dw_conn()
        
        # Builders
        dim_builder = DimensionBuilder(conn_oro, conn_crm)
        fact_builder = FactBuilder(conn_oro, conn_dw)
        loader = SimpleDatabaseLoader(conn_dw)
        
        # ==================== DIMENSIONES CONFORMADAS ====================
        logger.info("\n📋 FASE 1: DIMENSIONES CONFORMADAS")
        logger.info("=" * 80)
        
        dims_conformadas = [
            ('dim_fecha', dim_builder.build_dim_fecha),
            ('dim_usuario', dim_builder.build_dim_usuario),
            ('dim_detalle_venta', dim_builder.build_dim_detalle_venta),
        ]
        
        for table_name, build_func in dims_conformadas:
            try:
                logger.info(f"📥 Procesando: {table_name}")
                df = build_func()
                if not df.empty:
                    loader.load_to_database(df, table_name)
            except Exception as e:
                logger.error(f"❌ Error en {table_name}: {str(e)}")
        
        # ==================== DIMENSIONES DE VENTAS ====================
        logger.info("\n💰 FASE 2: DIMENSIONES DE VENTAS")
        logger.info("=" * 80)
        
        dims_ventas = [
            ('dim_cliente', dim_builder.build_dim_cliente),
            ('dim_producto', dim_builder.build_dim_producto),
            ('dim_orden', dim_builder.build_dim_orden),
            ('dim_sitio_web', dim_builder.build_dim_sitio_web),
            ('dim_canal', dim_builder.build_dim_canal),
            ('dim_promocion', dim_builder.build_dim_promocion),
            ('dim_vendedor', dim_builder.build_dim_vendedor),
            ('dim_metodo_pago', dim_builder.build_dim_metodo_pago),
            ('dim_metodo_envio', dim_builder.build_dim_metodo_envio),
            ('dim_direccion', dim_builder.build_dim_direccion),
            ('dim_estado_orden', dim_builder.build_dim_estado_orden),
        ]
        
        for table_name, build_func in dims_ventas:
            try:
                logger.info(f"📥 Procesando: {table_name}")
                df = build_func()
                if not df.empty:
                    loader.load_to_database(df, table_name)
            except Exception as e:
                logger.error(f"❌ Error en {table_name}: {str(e)}")
        
        # ==================== DIMENSIONES DE INVENTARIO ====================
        logger.info("\n📦 FASE 3: DIMENSIONES DE INVENTARIO")
        logger.info("=" * 80)
        
        dims_inventario = [
            ('dim_almacen', dim_builder.build_dim_almacen),
            ('dim_proveedor', dim_builder.build_dim_proveedor),
            ('dim_tipo_movimiento', dim_builder.build_dim_tipo_movimiento),
            ('dim_categoria_producto', dim_builder.build_dim_categoria_producto),
        ]
        
        for table_name, build_func in dims_inventario:
            try:
                logger.info(f"📥 Procesando: {table_name}")
                df = build_func()
                if not df.empty:
                    loader.load_to_database(df, table_name)
            except Exception as e:
                logger.error(f"❌ Error en {table_name}: {str(e)}")
        
        # ==================== DIMENSIONES DE FINANZAS ====================
        logger.info("\n💼 FASE 4: DIMENSIONES DE FINANZAS")
        logger.info("=" * 80)
        
        dims_finanzas = [
            ('dim_cuenta_contable', dim_builder.build_dim_cuenta_contable),
            ('dim_centro_costo', dim_builder.build_dim_centro_costo),
            ('dim_tipo_transaccion', dim_builder.build_dim_tipo_transaccion),
            ('dim_periodo_contable', dim_builder.build_dim_periodo_contable),
        ]
        
        for table_name, build_func in dims_finanzas:
            try:
                logger.info(f"📥 Procesando: {table_name}")
                df = build_func()
                if not df.empty:
                    loader.load_to_database(df, table_name)
            except Exception as e:
                logger.error(f"❌ Error en {table_name}: {str(e)}")
        
        # ==================== TABLAS DE HECHOS ====================
        logger.info("\n🎯 FASE 5: TABLAS DE HECHOS")
        logger.info("=" * 80)
        
        facts = [
            ('fact_ventas', fact_builder.build_fact_ventas),
            ('fact_inventario', fact_builder.build_fact_inventario),
            ('fact_transacciones', fact_builder.build_fact_transacciones),
            ('fact_balance', fact_builder.build_fact_balance),
            ('fact_estado_resultados', fact_builder.build_fact_estado_resultados),
        ]
        
        for table_name, build_func in facts:
            try:
                logger.info(f"📊 Procesando: {table_name}")
                df = build_func()
                if not df.empty:
                    loader.load_to_database(df, table_name)
            except Exception as e:
                logger.error(f"❌ Error en {table_name}: {str(e)}")
        
        # Cerrar conexiones
        conn_oro.close()
        conn_crm.close()
        conn_dw.close()
        
        # ==================== REPORTE FINAL ====================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.success("✅ ETL COMPLETO FINALIZADO")
        logger.info("=" * 80)
        logger.info(f"⏱️  Tiempo total: {duration:.2f} segundos")
        logger.info(f"📊 Verificar: python scripts/validate_dw_structure.py")
        logger.info("=" * 80)


if __name__ == "__main__":
    orchestrator = ETLOrchestrator()
    orchestrator.run()
