-- ============================================================================
-- ESQUEMA DATA WAREHOUSE - PUNTAFINA
-- ============================================================================
-- Creación de tablas dimensionales y de hechos para el Data Warehouse

-- Eliminar tablas existentes si existen
DROP TABLE IF EXISTS fact_transacciones CASCADE;
DROP TABLE IF EXISTS fact_inventario CASCADE;
DROP TABLE IF EXISTS fact_ventas CASCADE;
DROP TABLE IF EXISTS fact_estado_resultados CASCADE;
DROP TABLE IF EXISTS fact_balance CASCADE;

DROP TABLE IF EXISTS dim_periodo_contable CASCADE;
DROP TABLE IF EXISTS dim_tipo_transaccion CASCADE;
DROP TABLE IF EXISTS dim_centro_costo CASCADE;
DROP TABLE IF EXISTS dim_cuenta_contable CASCADE;
DROP TABLE IF EXISTS dim_categoria_producto CASCADE;
DROP TABLE IF EXISTS dim_tipo_movimiento CASCADE;
DROP TABLE IF EXISTS dim_proveedor CASCADE;
DROP TABLE IF EXISTS dim_almacen CASCADE;
DROP TABLE IF EXISTS dim_estado_pago CASCADE;
DROP TABLE IF EXISTS dim_estado_orden CASCADE;
DROP TABLE IF EXISTS dim_line_item CASCADE;
DROP TABLE IF EXISTS dim_promocion CASCADE;
DROP TABLE IF EXISTS dim_impuestos CASCADE;
DROP TABLE IF EXISTS dim_pago CASCADE;
DROP TABLE IF EXISTS dim_envio CASCADE;
DROP TABLE IF EXISTS dim_direccion CASCADE;
DROP TABLE IF EXISTS dim_canal CASCADE;
DROP TABLE IF EXISTS dim_sitio_web CASCADE;
DROP TABLE IF EXISTS dim_orden CASCADE;
DROP TABLE IF EXISTS dim_producto CASCADE;
DROP TABLE IF EXISTS dim_cliente CASCADE;
DROP TABLE IF EXISTS dim_usuario CASCADE;
DROP TABLE IF EXISTS dim_detalle_venta CASCADE;
DROP TABLE IF EXISTS dim_fecha CASCADE;

-- ============================================================================
-- DIMENSIONES CONFORMADAS
-- ============================================================================

CREATE TABLE dim_fecha (
    fecha_id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semana_anio INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    dia_semana_nombre VARCHAR(20),
    mes_nombre VARCHAR(20),
    es_fin_semana BOOLEAN DEFAULT FALSE,
    es_festivo BOOLEAN DEFAULT FALSE,
    nombre_festivo VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_fecha_fecha ON dim_fecha(fecha);
CREATE INDEX idx_dim_fecha_anio_mes ON dim_fecha(anio, mes);

CREATE TABLE dim_usuario (
    usuario_id SERIAL PRIMARY KEY,
    usuario_externo_id INTEGER,
    username VARCHAR(255),
    email VARCHAR(255),
    nombre_completo VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_usuario_externo ON dim_usuario(usuario_externo_id);

CREATE TABLE dim_detalle_venta (
    detalle_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50),
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DIMENSIONES DE VENTAS
-- ============================================================================

CREATE TABLE dim_cliente (
    cliente_id SERIAL PRIMARY KEY,
    cliente_externo_id INTEGER,
    codigo_cliente VARCHAR(50),
    nombre VARCHAR(255),
    tipo_cliente VARCHAR(50),
    segmento VARCHAR(50),
    email VARCHAR(255),
    telefono VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_cliente_externo ON dim_cliente(cliente_externo_id);

CREATE TABLE dim_producto (
    producto_id SERIAL PRIMARY KEY,
    producto_externo_id INTEGER,
    sku VARCHAR(100) UNIQUE,
    nombre VARCHAR(500),
    descripcion TEXT,
    categoria VARCHAR(100),
    marca VARCHAR(100),
    tipo VARCHAR(50),
    unidad_medida VARCHAR(20),
    precio_base DECIMAL(10,2),
    costo_estandar DECIMAL(10,2),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_producto_externo ON dim_producto(producto_externo_id);
CREATE INDEX idx_dim_producto_sku ON dim_producto(sku);

CREATE TABLE dim_orden (
    orden_id SERIAL PRIMARY KEY,
    orden_externo_id INTEGER,
    numero_orden VARCHAR(100) UNIQUE,
    tipo_orden VARCHAR(50),
    canal VARCHAR(50),
    moneda VARCHAR(3),
    tasa_cambio DECIMAL(10,4) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_orden_externo ON dim_orden(orden_externo_id);

CREATE TABLE dim_sitio_web (
    sitio_id SERIAL PRIMARY KEY,
    sitio_externo_id INTEGER,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    url VARCHAR(500),
    pais VARCHAR(100),
    idioma VARCHAR(10),
    moneda_default VARCHAR(3),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_canal (
    canal_id SERIAL PRIMARY KEY,
    canal_externo_id INTEGER,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    tipo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_direccion (
    direccion_id SERIAL PRIMARY KEY,
    direccion_externo_id INTEGER,
    calle VARCHAR(255),
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(100),
    tipo_direccion VARCHAR(50)
);

CREATE TABLE dim_envio (
    envio_id SERIAL PRIMARY KEY,
    envio_externo_id INTEGER,
    metodo_envio VARCHAR(100),
    transportista VARCHAR(100),
    costo_envio DECIMAL(10,2),
    tiempo_estimado_dias INTEGER
);

CREATE TABLE dim_pago (
    pago_id SERIAL PRIMARY KEY,
    pago_externo_id INTEGER,
    metodo_pago VARCHAR(100),
    procesador VARCHAR(100),
    tipo_pago VARCHAR(50)
);

CREATE TABLE dim_impuestos (
    impuesto_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50),
    nombre VARCHAR(100),
    tasa DECIMAL(5,2),
    tipo VARCHAR(50)
);

CREATE TABLE dim_promocion (
    promocion_id SERIAL PRIMARY KEY,
    promocion_externo_id INTEGER,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    descripcion TEXT,
    tipo_descuento VARCHAR(50),
    valor_descuento DECIMAL(10,2),
    fecha_inicio DATE,
    fecha_fin DATE
);

CREATE TABLE dim_line_item (
    line_item_id SERIAL PRIMARY KEY,
    line_item_externo_id INTEGER,
    numero_linea INTEGER,
    tipo_linea VARCHAR(50)
);

CREATE TABLE dim_estado_orden (
    estado_orden_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_estado_pago (
    estado_pago_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- DIMENSIONES DE INVENTARIO
-- ============================================================================

CREATE TABLE dim_almacen (
    almacen_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    direccion VARCHAR(255),
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    capacidad INTEGER,
    tipo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_almacen_codigo ON dim_almacen(codigo);

CREATE TABLE dim_proveedor (
    proveedor_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    contacto VARCHAR(255),
    email VARCHAR(255),
    telefono VARCHAR(50),
    direccion VARCHAR(255),
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_proveedor_codigo ON dim_proveedor(codigo);

CREATE TABLE dim_tipo_movimiento (
    tipo_movimiento_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100),
    descripcion TEXT,
    tipo VARCHAR(50),
    afecta_stock VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_tipo_mov_codigo ON dim_tipo_movimiento(codigo);

CREATE TABLE dim_categoria_producto (
    categoria_id SERIAL PRIMARY KEY,
    categoria_externo_id INTEGER,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    descripcion TEXT,
    categoria_padre_id INTEGER,
    nivel INTEGER,
    activo BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- DIMENSIONES DE FINANZAS
-- ============================================================================

CREATE TABLE dim_cuenta_contable (
    cuenta_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    descripcion TEXT,
    tipo VARCHAR(50),
    categoria VARCHAR(50),
    nivel INTEGER,
    cuenta_padre VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_cuenta_codigo ON dim_cuenta_contable(codigo);

CREATE TABLE dim_centro_costo (
    centro_costo_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    descripcion TEXT,
    tipo VARCHAR(50),
    responsable VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_centro_codigo ON dim_centro_costo(codigo);

CREATE TABLE dim_tipo_transaccion (
    tipo_transaccion_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100),
    descripcion TEXT,
    categoria VARCHAR(50),
    afecta_flujo VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dim_tipo_trans_codigo ON dim_tipo_transaccion(codigo);

CREATE TABLE dim_periodo_contable (
    periodo_id SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    nombre_periodo VARCHAR(50),
    fecha_inicio DATE,
    fecha_fin DATE,
    cerrado BOOLEAN DEFAULT FALSE,
    UNIQUE(anio, mes)
);

-- ============================================================================
-- TABLAS DE HECHOS
-- ============================================================================

CREATE TABLE fact_ventas (
    venta_id SERIAL PRIMARY KEY,
    fecha_id INTEGER REFERENCES dim_fecha(fecha_id),
    cliente_id INTEGER REFERENCES dim_cliente(cliente_id),
    producto_id INTEGER REFERENCES dim_producto(producto_id),
    orden_id INTEGER REFERENCES dim_orden(orden_id),
    usuario_id INTEGER REFERENCES dim_usuario(usuario_id),
    almacen_id INTEGER REFERENCES dim_almacen(almacen_id),
    
    -- Medidas
    cantidad DECIMAL(10,2),
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    descuento DECIMAL(10,2),
    impuesto DECIMAL(10,2),
    envio DECIMAL(10,2),
    total DECIMAL(10,2),
    costo_unitario DECIMAL(10,2),
    costo_total DECIMAL(10,2),
    margen DECIMAL(10,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_ventas_fecha ON fact_ventas(fecha_id);
CREATE INDEX idx_fact_ventas_cliente ON fact_ventas(cliente_id);
CREATE INDEX idx_fact_ventas_producto ON fact_ventas(producto_id);

CREATE TABLE fact_inventario (
    movimiento_id SERIAL PRIMARY KEY,
    fecha_id INTEGER REFERENCES dim_fecha(fecha_id),
    producto_id INTEGER REFERENCES dim_producto(producto_id),
    almacen_id INTEGER REFERENCES dim_almacen(almacen_id),
    tipo_movimiento_id INTEGER REFERENCES dim_tipo_movimiento(tipo_movimiento_id),
    proveedor_id INTEGER REFERENCES dim_proveedor(proveedor_id),
    usuario_id INTEGER REFERENCES dim_usuario(usuario_id),
    
    -- Medidas
    cantidad DECIMAL(10,2),
    costo_unitario DECIMAL(10,2),
    costo_total DECIMAL(10,2),
    stock_anterior DECIMAL(10,2),
    stock_resultante DECIMAL(10,2),
    
    documento VARCHAR(100),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_inv_fecha ON fact_inventario(fecha_id);
CREATE INDEX idx_fact_inv_producto ON fact_inventario(producto_id);
CREATE INDEX idx_fact_inv_almacen ON fact_inventario(almacen_id);

CREATE TABLE fact_transacciones (
    transaccion_id SERIAL PRIMARY KEY,
    fecha_id INTEGER REFERENCES dim_fecha(fecha_id),
    cuenta_id INTEGER REFERENCES dim_cuenta_contable(cuenta_id),
    centro_costo_id INTEGER REFERENCES dim_centro_costo(centro_costo_id),
    tipo_transaccion_id INTEGER REFERENCES dim_tipo_transaccion(tipo_transaccion_id),
    usuario_id INTEGER REFERENCES dim_usuario(usuario_id),
    
    -- Medidas
    numero_asiento VARCHAR(50),
    tipo_movimiento VARCHAR(10),  -- debe/haber
    monto DECIMAL(15,2),
    
    documento_referencia VARCHAR(100),
    descripcion TEXT,
    orden_id INTEGER,
    movimiento_inventario_id INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_trans_fecha ON fact_transacciones(fecha_id);
CREATE INDEX idx_fact_trans_cuenta ON fact_transacciones(cuenta_id);
CREATE INDEX idx_fact_trans_centro ON fact_transacciones(centro_costo_id);

CREATE TABLE fact_balance (
    balance_id SERIAL PRIMARY KEY,
    periodo_id INTEGER REFERENCES dim_periodo_contable(periodo_id),
    cuenta_id INTEGER REFERENCES dim_cuenta_contable(cuenta_id),
    
    -- Medidas
    saldo_inicial DECIMAL(15,2),
    debitos DECIMAL(15,2),
    creditos DECIMAL(15,2),
    saldo_final DECIMAL(15,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(periodo_id, cuenta_id)
);

CREATE INDEX idx_fact_balance_periodo ON fact_balance(periodo_id);
CREATE INDEX idx_fact_balance_cuenta ON fact_balance(cuenta_id);

CREATE TABLE fact_estado_resultados (
    resultado_id SERIAL PRIMARY KEY,
    periodo_id INTEGER REFERENCES dim_periodo_contable(periodo_id),
    cuenta_id INTEGER REFERENCES dim_cuenta_contable(cuenta_id),
    centro_costo_id INTEGER REFERENCES dim_centro_costo(centro_costo_id),
    
    -- Medidas
    ingresos DECIMAL(15,2),
    costos DECIMAL(15,2),
    gastos DECIMAL(15,2),
    utilidad_bruta DECIMAL(15,2),
    utilidad_neta DECIMAL(15,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_resultado_periodo ON fact_estado_resultados(periodo_id);
CREATE INDEX idx_fact_resultado_cuenta ON fact_estado_resultados(cuenta_id);

-- ============================================================================
-- COMENTARIOS EN TABLAS
-- ============================================================================

COMMENT ON TABLE dim_fecha IS 'Dimensión de tiempo conformada';
COMMENT ON TABLE dim_usuario IS 'Dimensión de usuarios del sistema';
COMMENT ON TABLE dim_cliente IS 'Dimensión de clientes';
COMMENT ON TABLE dim_producto IS 'Dimensión de productos';
COMMENT ON TABLE fact_ventas IS 'Tabla de hechos de ventas';
COMMENT ON TABLE fact_inventario IS 'Tabla de hechos de movimientos de inventario';
COMMENT ON TABLE fact_transacciones IS 'Tabla de hechos de transacciones contables';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
