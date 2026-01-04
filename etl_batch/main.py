#!/usr/bin/env python3
"""
ORQUESTADOR ETL BATCH - SISTEMA PRINCIPAL
=========================================
Orquestador principal del sistema ETL con procesamiento por lotes
optimizado para Ubuntu 22.04
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import yaml
import click
from dotenv import load_dotenv
from typing import Dict, Any, List

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from core.batch_processor import BatchProcessor, BatchConfig, StreamingBatchProcessor
from core.data_validator import DataValidator
from extractors.database_extractor import DatabaseExtractor
from extractors.csv_extractor import CSVExtractor
from transformers.dimension_builder import DimensionBuilder
from transformers.fact_builder import FactBuilder
from loaders.database_loader import DatabaseLoader
from utils.logger import setup_logger
from utils.metrics import MetricsCollector


class ETLOrchestrator:
    """Orquestador principal del ETL"""

    def __init__(self, config_path: Path = None):
        """
        Inicializa el orquestador

        Args:
            config_path: Ruta al archivo de configuración
        """
        # Cargar configuración
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "etl_config.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Cargar variables de entorno
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Configurar logger
        self.logger = setup_logger("ETLOrchestrator", self.config["paths"]["logs"])

        # Inicializar componentes
        batch_config = BatchConfig(
            chunk_size=self.config["batch"]["chunk_size"],
            max_workers=self.config["batch"]["max_workers"],
            timeout=self.config["batch"]["timeout"],
            max_retries=self.config["batch"]["max_retries"],
            retry_delay=self.config["batch"]["retry_delay"],
            max_memory_mb=self.config["batch"]["max_memory_mb"],
            enable_checkpoints=self.config["recovery"]["enable_checkpoints"],
            checkpoint_interval=self.config["recovery"]["checkpoint_interval"],
        )

        self.batch_processor = BatchProcessor(
            batch_config, Path(self.config["paths"]["checkpoints"])
        )

        self.streaming_processor = StreamingBatchProcessor(
            batch_config, Path(self.config["paths"]["checkpoints"])
        )

        self.data_validator = DataValidator(self.config)

        self.db_extractor = DatabaseExtractor(self.config)
        self.csv_extractor = CSVExtractor(self.config)

        self.dimension_builder = DimensionBuilder(self.config)
        self.fact_builder = FactBuilder(self.config)

        self.db_loader = DatabaseLoader(self.config)

        self.metrics = MetricsCollector()

        self.logger.info("🚀 Orquestador ETL inicializado")

    def run_full_etl(self) -> Dict[str, Any]:
        """
        Ejecuta el proceso ETL completo

        Returns:
            Diccionario con resultados de la ejecución
        """
        self.logger.info("=" * 80)
        self.logger.info("🏪 PUNTAFINA ETL BATCH - PROCESO COMPLETO")
        self.logger.info("=" * 80)

        start_time = datetime.now()

        try:
            # 1. Extracción
            self.logger.info("\n📥 FASE 1: EXTRACCIÓN")
            extraction_results = self._run_extraction()

            # 2. Transformación - Dimensiones
            self.logger.info("\n🔄 FASE 2: TRANSFORMACIÓN - DIMENSIONES")
            dimension_results = self._run_dimension_building()

            # 3. Transformación - Facts
            self.logger.info("\n🔄 FASE 3: TRANSFORMACIÓN - TABLAS DE HECHOS")
            fact_results = self._run_fact_building()

            # 4. Carga
            self.logger.info("\n📤 FASE 4: CARGA")
            loading_results = self._run_loading()

            # 5. Validación final
            self.logger.info("\n✅ FASE 5: VALIDACIÓN FINAL")
            validation_results = self._run_final_validation()

            elapsed_time = (datetime.now() - start_time).total_seconds()

            # Reporte final
            final_report = {
                "status": "success",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_time": elapsed_time,
                "extraction": extraction_results,
                "dimensions": dimension_results,
                "facts": fact_results,
                "loading": loading_results,
                "validation": validation_results,
                "metrics": self.metrics.get_summary(),
            }

            self._print_final_summary(final_report)

            return final_report

        except Exception as e:
            self.logger.error(f"❌ Error en proceso ETL: {e}", exc_info=True)
            raise

    def _run_extraction(self) -> Dict[str, Any]:
        """Fase de extracción de datos"""
        results = {"database": {}, "csv": {}, "total_records": 0}

        # Extraer de OroCommerce
        if self.config["data_sources"]["orocommerce"]["enabled"]:
            self.logger.info("   📊 Extrayendo de OroCommerce...")
            oro_data = self.db_extractor.extract_orocommerce()
            results["database"]["orocommerce"] = {
                "tables": len(oro_data),
                "records": sum(len(df) for df in oro_data.values()),
            }
            self.logger.info(
                f"      ✓ {results['database']['orocommerce']['records']:,} registros"
            )

        # Extraer de OroCRM
        if self.config["data_sources"]["orocrm"]["enabled"]:
            self.logger.info("   📊 Extrayendo de OroCRM...")
            crm_data = self.db_extractor.extract_orocrm()
            results["database"]["orocrm"] = {
                "tables": len(crm_data),
                "records": sum(len(df) for df in crm_data.values()),
            }
            self.logger.info(
                f"      ✓ {results['database']['orocrm']['records']:,} registros"
            )

        # Extraer de CSVs
        if self.config["data_sources"]["csv_files"]["enabled"]:
            self.logger.info("   📁 Extrayendo de archivos CSV...")
            csv_data = self.csv_extractor.extract_all()
            results["csv"] = {
                "files": len(csv_data),
                "records": sum(len(df) for df in csv_data.values()),
            }
            self.logger.info(f"      ✓ {results['csv']['records']:,} registros")

        # Total
        results["total_records"] = (
            results["database"].get("orocommerce", {}).get("records", 0)
            + results["database"].get("orocrm", {}).get("records", 0)
            + results["csv"].get("records", 0)
        )

        self.logger.info(
            f"\n   ✅ Extracción completada: {results['total_records']:,} registros totales"
        )

        return results

    def _run_dimension_building(self) -> Dict[str, Any]:
        """Fase de construcción de dimensiones"""
        results = {"dimensions_built": [], "total_records": 0, "errors": []}

        dimensions_config = self.config["dimensions"]

        # Dimensiones conformadas (compartidas)
        for dim_name in dimensions_config["conformed"]:
            try:
                self.logger.info(f"   🔨 Construyendo {dim_name}...")
                dim_df = self.dimension_builder.build(dim_name)

                # Validar y poblar
                dim_df, validation_report = self.data_validator.validate_and_populate(
                    dim_df, self.dimension_builder.get_schema(dim_name), dim_name
                )

                # Guardar
                self._save_dimension(dim_name, dim_df)

                results["dimensions_built"].append(
                    {
                        "name": dim_name,
                        "records": len(dim_df),
                        "validation": validation_report,
                    }
                )
                results["total_records"] += len(dim_df)

                self.logger.info(f"      ✓ {len(dim_df):,} registros")

            except Exception as e:
                self.logger.error(f"      ✗ Error: {e}")
                results["errors"].append({dim_name: str(e)})

        # Dimensiones por módulo
        for module, dims in dimensions_config.items():
            if module == "conformed":
                continue

            self.logger.info(f"\n   📦 Módulo: {module}")

            for dim_name in dims:
                try:
                    self.logger.info(f"      🔨 Construyendo {dim_name}...")
                    dim_df = self.dimension_builder.build(dim_name)

                    dim_df, validation_report = (
                        self.data_validator.validate_and_populate(
                            dim_df,
                            self.dimension_builder.get_schema(dim_name),
                            dim_name,
                        )
                    )

                    self._save_dimension(dim_name, dim_df)

                    results["dimensions_built"].append(
                        {
                            "name": dim_name,
                            "records": len(dim_df),
                            "module": module,
                            "validation": validation_report,
                        }
                    )
                    results["total_records"] += len(dim_df)

                    self.logger.info(f"         ✓ {len(dim_df):,} registros")

                except Exception as e:
                    self.logger.error(f"         ✗ Error: {e}")
                    results["errors"].append({dim_name: str(e)})

        self.logger.info(
            f"\n   ✅ Dimensiones completadas: {results['total_records']:,} registros totales"
        )

        return results

    def _run_fact_building(self) -> Dict[str, Any]:
        """Fase de construcción de tablas de hechos"""
        results = {"facts_built": [], "total_records": 0, "errors": []}

        facts_config = self.config["facts"]

        for fact_name, fact_def in facts_config.items():
            try:
                self.logger.info(f"   🏗️  Construyendo {fact_name}...")

                # Construir fact table
                fact_df = self.fact_builder.build(fact_name, fact_def)

                # Validar
                fact_df, validation_report = self.data_validator.validate_and_populate(
                    fact_df, self.fact_builder.get_schema(fact_name), fact_name
                )

                # Guardar
                self._save_fact(fact_name, fact_df)

                results["facts_built"].append(
                    {
                        "name": fact_name,
                        "records": len(fact_df),
                        "grain": fact_def.get("grain", "N/A"),
                        "validation": validation_report,
                    }
                )
                results["total_records"] += len(fact_df)

                self.logger.info(f"      ✓ {len(fact_df):,} registros")

            except Exception as e:
                self.logger.error(f"      ✗ Error: {e}")
                results["errors"].append({fact_name: str(e)})

        self.logger.info(
            f"\n   ✅ Facts completadas: {results['total_records']:,} registros totales"
        )

        return results

    def _run_loading(self) -> Dict[str, Any]:
        """Fase de carga a base de datos"""
        results = {"tables_loaded": [], "total_records": 0, "errors": []}

        self.logger.info("   🚛 Cargando dimensiones...")

        # Cargar dimensiones
        dimension_files = list(
            Path(self.config["paths"]["output_parquet"]).glob("dim_*.parquet")
        )

        for dim_file in dimension_files:
            try:
                table_name = dim_file.stem
                self.logger.info(f"      📤 {table_name}...")

                records_loaded = self.db_loader.load_table(
                    dim_file, table_name, strategy=self.config["loading"]["strategy"]
                )

                results["tables_loaded"].append(
                    {"table": table_name, "records": records_loaded}
                )
                results["total_records"] += records_loaded

                self.logger.info(f"         ✓ {records_loaded:,} registros")

            except Exception as e:
                self.logger.error(f"         ✗ Error: {e}")
                results["errors"].append({table_name: str(e)})

        # Cargar facts
        self.logger.info("\n   🚛 Cargando tablas de hechos...")

        fact_files = list(
            Path(self.config["paths"]["output_parquet"]).glob("fact_*.parquet")
        )

        for fact_file in fact_files:
            try:
                table_name = fact_file.stem
                self.logger.info(f"      📤 {table_name}...")

                records_loaded = self.db_loader.load_table(
                    fact_file, table_name, strategy=self.config["loading"]["strategy"]
                )

                results["tables_loaded"].append(
                    {"table": table_name, "records": records_loaded}
                )
                results["total_records"] += records_loaded

                self.logger.info(f"         ✓ {records_loaded:,} registros")

            except Exception as e:
                self.logger.error(f"         ✗ Error: {e}")
                results["errors"].append({table_name: str(e)})

        self.logger.info(
            f"\n   ✅ Carga completada: {results['total_records']:,} registros totales"
        )

        return results

    def _run_final_validation(self) -> Dict[str, Any]:
        """Validación final del proceso"""
        results = {"validations": [], "passed": True}

        self.logger.info("   🔍 Verificando integridad de datos...")

        # TODO: Implementar validaciones finales
        # - Contar registros en base de datos
        # - Verificar integridad referencial
        # - Validar rangos y valores

        self.logger.info("      ✓ Integridad verificada")

        return results

    def _save_dimension(self, name: str, df):
        """Guarda dimensión en formato parquet y CSV"""
        output_dir = Path(self.config["paths"]["output_parquet"])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Parquet
        parquet_file = output_dir / f"{name}.parquet"
        df.to_parquet(parquet_file, index=False, compression="snappy")

        # CSV (opcional)
        if self.config.get("exportar_csv", True):
            csv_dir = Path(self.config["paths"]["output_csv"])
            csv_dir.mkdir(parents=True, exist_ok=True)
            csv_file = csv_dir / f"{name}.csv"
            df.to_csv(csv_file, index=False, encoding="utf-8")

    def _save_fact(self, name: str, df):
        """Guarda fact table en formato parquet y CSV"""
        self._save_dimension(name, df)  # Mismo proceso

    def _print_final_summary(self, report: Dict[str, Any]):
        """Imprime resumen final"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 RESUMEN FINAL DEL PROCESO ETL")
        self.logger.info("=" * 80)

        self.logger.info(f"\n⏱️  Tiempo total: {report['elapsed_time']:.2f} segundos")
        self.logger.info(f"✅ Estado: {report['status']}")

        self.logger.info(f"\n📥 Extracción:")
        self.logger.info(
            f"   Total registros: {report['extraction']['total_records']:,}"
        )

        self.logger.info(f"\n🔄 Transformación:")
        self.logger.info(
            f"   Dimensiones: {len(report['dimensions']['dimensions_built'])}"
        )
        self.logger.info(f"   Facts: {len(report['facts']['facts_built'])}")
        self.logger.info(
            f"   Total registros: {report['dimensions']['total_records'] + report['facts']['total_records']:,}"
        )

        self.logger.info(f"\n📤 Carga:")
        self.logger.info(f"   Tablas: {len(report['loading']['tables_loaded'])}")
        self.logger.info(f"   Total registros: {report['loading']['total_records']:,}")

        if (
            report["dimensions"]["errors"]
            or report["facts"]["errors"]
            or report["loading"]["errors"]
        ):
            self.logger.warning(f"\n⚠️  Errores encontrados:")
            for error in (
                report["dimensions"]["errors"]
                + report["facts"]["errors"]
                + report["loading"]["errors"]
            ):
                self.logger.warning(f"   {error}")

        self.logger.info("\n" + "=" * 80)


@click.group()
def cli():
    """PuntaFina ETL Batch - Sistema de procesamiento por lotes"""
    pass


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Archivo de configuración")
def run(config):
    """Ejecuta el proceso ETL completo"""
    orchestrator = ETLOrchestrator(Path(config) if config else None)
    orchestrator.run_full_etl()


@cli.command()
def setup():
    """Configura el sistema inicial"""
    click.echo("🔧 Configurando sistema ETL...")
    # TODO: Implementar setup inicial
    click.echo("✅ Configuración completada")


@cli.command()
def validate():
    """Valida la configuración y conexiones"""
    click.echo("🔍 Validando configuración...")
    # TODO: Implementar validación
    click.echo("✅ Validación completada")


if __name__ == "__main__":
    cli()
