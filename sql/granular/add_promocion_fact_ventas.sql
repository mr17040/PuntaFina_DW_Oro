-- Agregar campo de promoción a fact_ventas
DO $$ 
BEGIN
    -- Agregar sk_promocion (FK a dim_promocion)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fact_ventas' AND column_name = 'sk_promocion'
    ) THEN
        ALTER TABLE fact_ventas ADD COLUMN sk_promocion INTEGER DEFAULT 1;
        COMMENT ON COLUMN fact_ventas.sk_promocion IS 'FK a dim_promocion - 1=Sin Promoción por defecto';
    END IF;
END $$;

-- Crear índice
CREATE INDEX IF NOT EXISTS idx_fact_ventas_sk_promocion ON fact_ventas(sk_promocion);

COMMENT ON TABLE fact_ventas IS 'Tabla de hechos de ventas con promociones';
