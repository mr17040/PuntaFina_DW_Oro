#!/usr/bin/env python3
"""Test del loader con dim_cuenta_contable"""
import sys
sys.path.insert(0, '/root/PuntaFina_DW_Oro/etl_batch')

from loaders.database_loader import DatabaseLoader
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

loader = DatabaseLoader()

# Cargar dim_cuenta_contable
result = loader.load_to_dw(
    file_path='/root/PuntaFina_DW_Oro/data/outputs/parquet/dim_cuenta_contable.parquet',
    table_name='dim_cuenta_contable',
    strategy='truncate_and_load'
)

print(f"\nResultado: {result} registros cargados")
