#!/usr/bin/env python3
"""
COMPLETE ETL RUNNER - Ejecutor completo de ETL para poblar todo el Data Warehouse
Puebla TODAS las dimensiones y facts con datos reales de OroCommerce y CSVs
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Agregar directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
env_path = project_root / '.env'
load_dotenv(env_path)

import logging
from datetime import datetime
import pandas as pd

# Importar los constructores completos
from etl_batch.transformers.complete_dimension_builder import CompleteDimensionBuilder
from etl_batch.transformers.complete_fact_builder import CompleteFactBuilder
from etl_batch.loaders.simple_loader import SimpleDatabaseLoader

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/complete_etl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CompleteETLRunner:
    """Ejecutor completo de ETL para poblar todo el DW"""
    
    def __init__(self):
        self.dim_builder = CompleteDimensionBuilder()
        self.fact_builder = CompleteFactBuilder()
        self.loader = SimpleDatabaseLoader()
        self.output_dir = Path('data/processed')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_complete_etl(self):
        """Ejecutar ETL completo para todas las dimensiones y facts"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO ETL COMPLETO - POBLANDO TODO EL DATA WAREHOUSE")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # ==================== FASE 1: DIMENSIONES CONFORMADAS ====================
        logger.info("\n" + "=" * 80)
        logger.info("📊 FASE 1: CARGANDO DIMENSIONES CONFORMADAS")
        logger.info("=" * 80)
        
        dimensions_conformadas = [
            ('dim_fecha', self.dim_builder.build_dim_fecha),
            ('dim_usuario', self.dim_builder.build_dim_usuario),
            ('dim_producto', self.dim_builder.build_dim_producto),
        ]
        
        for table_name, build_func in dimensions_conformadas:
            self._load_dimension(table_name, build_func)
        
        # ==================== FASE 2: DIMENSIONES DE VENTAS ====================
        logger.info("\n" + "=" * 80)
        logger.info("💰 FASE 2: CARGANDO DIMENSIONES DE VENTAS")
        logger.info("=" * 80)
        
        dimensions_ventas = [
            ('dim_cliente', self.dim_builder.build_dim_cliente),
            ('dim_sitio_web', self.dim_builder.build_dim_sitio_web),
            ('dim_canal', self.dim_builder.build_dim_canal),
            ('dim_direccion', self.dim_builder.build_dim_direccion),
            ('dim_orden', self.dim_builder.build_dim_orden),
            ('dim_line_item', self.dim_builder.build_dim_line_item),
            ('dim_envio', self.dim_builder.build_dim_envio),
            ('dim_estado_orden', self.dim_builder.build_dim_estado_orden),
            ('dim_estado_pago', self.dim_builder.build_dim_estado_pago),
            ('dim_pago', self.dim_builder.build_dim_pago),
            ('dim_impuestos', self.dim_builder.build_dim_impuestos),
            ('dim_promocion', self.dim_builder.build_dim_promocion),
        ]
        
        for table_name, build_func in dimensions_ventas:
            self._load_dimension(table_name, build_func)
        
        # ==================== FASE 3: DIMENSIONES DE INVENTARIO ====================
        logger.info("\n" + "=" * 80)
        logger.info("📦 FASE 3: CARGANDO DIMENSIONES DE INVENTARIO")
        logger.info("=" * 80)
        
        dimensions_inventario = [
            ('dim_almacen', self.dim_builder.build_dim_almacen),
            ('dim_proveedor', self.dim_builder.build_dim_proveedor),
            ('dim_tipo_movimiento', self.dim_builder.build_dim_tipo_movimiento),
            ('dim_categoria_producto', self.dim_builder.build_dim_categoria_producto),
        ]
        
        for table_name, build_func in dimensions_inventario:
            self._load_dimension(table_name, build_func)
        
        # ==================== FASE 4: DIMENSIONES DE FINANZAS ====================
        logger.info("\n" + "=" * 80)
        logger.info("💼 FASE 4: CARGANDO DIMENSIONES DE FINANZAS")
        logger.info("=" * 80)
        
        dimensions_finanzas = [
            ('dim_cuenta_contable', self.dim_builder.build_dim_cuenta_contable),
            ('dim_centro_costo', self.dim_builder.build_dim_centro_costo),
            ('dim_tipo_transaccion', self.dim_builder.build_dim_tipo_transaccion),
            ('dim_periodo_contable', self.dim_builder.build_dim_periodo_contable),
        ]
        
        for table_name, build_func in dimensions_finanzas:
            self._load_dimension(table_name, build_func)
        
        # ==================== FASE 5: TABLAS DE HECHOS ====================
        logger.info("\n" + "=" * 80)
        logger.info("🎯 FASE 5: CARGANDO TABLAS DE HECHOS")
        logger.info("=" * 80)
        
        facts = [
            ('fact_ventas', self.fact_builder.build_fact_ventas),
            ('fact_inventario', self.fact_builder.build_fact_inventario),
            ('fact_transacciones', self.fact_builder.build_fact_transacciones),
            ('fact_balance', self.fact_builder.build_fact_balance),
            ('fact_estado_resultados', self.fact_builder.build_fact_estado_resultados),
        ]
        
        for table_name, build_func in facts:
            self._load_fact(table_name, build_func)
        
        # ==================== REPORTE FINAL ====================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ETL COMPLETO FINALIZADO")
        logger.info("=" * 80)
        logger.info(f"⏱️  Tiempo total: {duration:.2f} segundos")
        logger.info(f"📊 Verificar resultados con: python scripts/validate_dw_structure.py")
        logger.info("=" * 80)
    
    def _load_dimension(self, table_name: str, build_func):
        """Cargar una dimensión"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📥 Procesando: {table_name}")
            logger.info(f"{'='*60}")
            
            # Construir datos
            df = build_func()
            
            if df.empty:
                logger.warning(f"⚠️  {table_name}: Sin datos para cargar")
                return
            
            # Guardar a parquet
            output_file = self.output_dir / f"{table_name}.parquet"
            df.to_parquet(output_file, index=False)
            logger.info(f"💾 Guardado: {output_file} ({len(df):,} registros)")
            
            # Cargar a base de datos
            rows_loaded = self.loader.load_to_database(str(output_file), table_name)
            logger.info(f"✅ {table_name}: {rows_loaded:,} registros cargados")
            
        except Exception as e:
            logger.error(f"❌ Error en {table_name}: {str(e)}", exc_info=True)
    
    def _load_fact(self, table_name: str, build_func):
        """Cargar una tabla de hechos"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 Procesando FACT: {table_name}")
            logger.info(f"{'='*60}")
            
            # Construir datos
            df = build_func()
            
            if df.empty:
                logger.warning(f"⚠️  {table_name}: Sin datos para cargar")
                return
            
            # Guardar a parquet
            output_file = self.output_dir / f"{table_name}.parquet"
            df.to_parquet(output_file, index=False)
            logger.info(f"💾 Guardado: {output_file} ({len(df):,} registros)")
            
            # Cargar a base de datos
            rows_loaded = self.loader.load_to_database(str(output_file), table_name)
            logger.info(f"✅ {table_name}: {rows_loaded:,} registros cargados")
            
        except Exception as e:
            logger.error(f"❌ Error en {table_name}: {str(e)}", exc_info=True)

def main():
    """Punto de entrada principal"""
    runner = CompleteETLRunner()
    runner.run_complete_etl()

if __name__ == '__main__':
    main()
