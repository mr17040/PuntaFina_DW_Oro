-- ============================================================================
-- Script para agregar dim_promocion y campos de promoción a fact_ventas
-- ============================================================================

-- 1. Verificar y actualizar dim_promocion
DO $$ 
BEGIN
    -- Agregar porcentaje_descuento si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dim_promocion' AND column_name = 'porcentaje_descuento'
    ) THEN
        ALTER TABLE dim_promocion ADD COLUMN porcentaje_descuento DECIMAL(5,2) DEFAULT 0;
    END IF;
    
    -- Agregar activo si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dim_promocion' AND column_name = 'activo'
    ) THEN
        ALTER TABLE dim_promocion ADD COLUMN activo BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Agregar created_at si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dim_promocion' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE dim_promocion ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Agregar updated_at si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dim_promocion' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE dim_promocion ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Agregar índices a dim_promocion
CREATE INDEX IF NOT EXISTS idx_dim_promocion_codigo ON dim_promocion(codigo);
CREATE INDEX IF NOT EXISTS idx_dim_promocion_nombre ON dim_promocion(nombre);

-- 2. Agregar columnas a fact_ventas si no existen
DO $$ 
BEGIN
    -- Agregar promocion_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fact_ventas' AND column_name = 'promocion_id'
    ) THEN
        ALTER TABLE fact_ventas ADD COLUMN promocion_id INTEGER;
        ALTER TABLE fact_ventas ADD CONSTRAINT fk_fact_ventas_promocion 
            FOREIGN KEY (promocion_id) REFERENCES dim_promocion(promocion_id);
        CREATE INDEX idx_fact_ventas_promocion ON fact_ventas(promocion_id);
    END IF;
    
    -- Agregar promocion_nombre (campo desnormalizado para análisis rápido)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fact_ventas' AND column_name = 'promocion_nombre'
    ) THEN
        ALTER TABLE fact_ventas ADD COLUMN promocion_nombre VARCHAR(255);
    END IF;
END $$;

-- 3. Insertar registro por defecto "Sin promoción" si no existe
INSERT INTO dim_promocion (
    promocion_id, codigo, nombre, descripcion, tipo_descuento, 
    valor_descuento, porcentaje_descuento, fecha_inicio, fecha_fin, activo
)
SELECT 
    1, 'PROMO0000', 'Sin promoción', 'Registro por defecto para ventas sin promoción', 
    'Ninguno', 0.0, 0.0, '2020-01-01', '2030-12-31', TRUE
WHERE NOT EXISTS (SELECT 1 FROM dim_promocion WHERE promocion_id = 1);

-- Resetear secuencia si es necesario
SELECT setval('dim_promocion_promocion_id_seq', 
    GREATEST(1, (SELECT COALESCE(MAX(promocion_id), 0) FROM dim_promocion)), 
    true);

-- 4. Actualizar fact_ventas existentes con promocion_id = 1 (Sin promoción)
UPDATE fact_ventas 
SET promocion_id = 1, 
    promocion_nombre = 'Sin promoción'
WHERE promocion_id IS NULL OR promocion_nombre IS NULL;

COMMENT ON TABLE dim_promocion IS 'Dimensión de promociones y descuentos aplicados a ventas';
COMMENT ON COLUMN fact_ventas.promocion_id IS 'FK a dim_promocion - Promoción aplicada a la venta';
COMMENT ON COLUMN fact_ventas.promocion_nombre IS 'Nombre de la promoción (campo desnormalizado)';
