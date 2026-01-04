#!/usr/bin/env python3
"""
DATABASE LOADER - CARGA DE DATOS A BASE DE DATOS
================================================
Carga datos procesados al data warehouse
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, Any
from pathlib import Path
import os
import logging


class DatabaseLoader:
    """Loader de datos a PostgreSQL"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def load_table(
        self, file_path: Path, table_name: str, strategy: str = "truncate_and_load"
    ) -> int:
        """
        Carga un archivo parquet a una tabla

        Args:
            file_path: Ruta al archivo parquet
            table_name: Nombre de la tabla
            strategy: Estrategia de carga

        Returns:
            Número de registros cargados
        """
        # Leer archivo
        df = pd.read_parquet(file_path)

        # Conectar a base de datos
        conn = self._get_dw_connection()

        try:
            if strategy == "truncate_and_load":
                self._truncate_and_load(conn, table_name, df)
            elif strategy == "incremental":
                self._incremental_load(conn, table_name, df)
            elif strategy == "upsert":
                self._upsert_load(conn, table_name, df)
            else:
                raise ValueError(f"Estrategia desconocida: {strategy}")

            conn.commit()
            return len(df)

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _truncate_and_load(self, conn, table_name: str, df: pd.DataFrame):
        """Trunca tabla y carga datos"""
        cursor = conn.cursor()

        # Truncar tabla
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")

        # Insertar datos
        if len(df) > 0:
            # Obtener columnas de la tabla desde la base de datos
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                AND column_name NOT IN ('created_at', 'updated_at')
                ORDER BY ordinal_position
            """)
            
            db_columns = [row[0] for row in cursor.fetchall()]
            
            # Filtrar solo las columnas que existen en ambos
            available_columns = [col for col in db_columns if col in df.columns]
            
            if not available_columns:
                self.logger.warning(f"No hay columnas coincidentes para {table_name}")
                cursor.close()
                return
            
            # Seleccionar solo las columnas disponibles
            df_to_load = df[available_columns]
            values = [tuple(row) for row in df_to_load.values]

            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(available_columns)})
                VALUES %s
            """

            execute_values(cursor, insert_query, values)
            self.logger.debug(f"Cargados {len(df_to_load)} registros en {table_name}")

        cursor.close()

    def _incremental_load(self, conn, table_name: str, df: pd.DataFrame):
        """Carga incremental (solo nuevos registros)"""
        # TODO: Implementar lógica incremental
        self._truncate_and_load(conn, table_name, df)

    def _upsert_load(self, conn, table_name: str, df: pd.DataFrame):
        """Upsert (actualiza o inserta)"""
        # TODO: Implementar lógica upsert
        self._truncate_and_load(conn, table_name, df)

    def _get_dw_connection(self):
        """Obtiene conexión al data warehouse"""
        return psycopg2.connect(
            host=os.getenv("DW_ORO_DB_HOST"),
            port=int(os.getenv("DW_ORO_DB_PORT")),
            dbname=os.getenv("DW_ORO_DB_NAME"),
            user=os.getenv("DW_ORO_DB_USER"),
            password=os.getenv("DW_ORO_DB_PASS"),
        )
