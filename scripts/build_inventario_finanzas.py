#!/usr/bin/env python3
"""
SCRIPT: CONSTRUCCIÓN DE DIMENSIONES Y HECHOS - INVENTARIO Y FINANZAS
=====================================================================
Construye las tablas de dimensiones y hechos para los módulos de:
- Inventario (proveedores, almacenes, movimientos)
- Finanzas (cuentas contables, centros de costo, transacciones)

Lee archivos CSV de entrada y genera archivos parquet y CSV optimizados.

Dimensiones creadas:
- dim_proveedor
- dim_almacen
- dim_movimiento_tipo
- dim_cuenta_contable
- dim_centro_costo
- dim_tipo_transaccion

Tablas de hechos creadas:
- fact_inventario
- fact_transacciones_contables
- fact_estado_resultados (agregado mensual)
- fact_balance_general (saldo a fecha)
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import yaml
import warnings

warnings.filterwarnings("ignore")

# Configuración global
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
INPUT_DIR = ROOT / "data" / "inputs"
PARQUET_DIR = ROOT / "data" / "outputs" / "parquet"
CSV_DIR = ROOT / "data" / "outputs" / "csv"

# Crear directorios si no existen
PARQUET_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR.mkdir(parents=True, exist_ok=True)


def save_dimension(df, name):
    """Guarda dimensión en parquet y CSV"""
    # Parquet (optimizado)
    parquet_file = PARQUET_DIR / f"{name}.parquet"
    df.to_parquet(parquet_file, index=False, compression="snappy")

    # CSV (para revisión)
    csv_file = CSV_DIR / f"{name}.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")

    print(f"   ✓ {name}: {len(df):,} registros -> {parquet_file.name}, {csv_file.name}")
    return len(df)


def save_fact_table(df, name):
    """Guarda tabla de hechos en parquet y CSV"""
    return save_dimension(df, name)


# ============================================================================
# DIMENSIONES DE INVENTARIO
# ============================================================================


def build_dim_proveedor():
    """Construye dim_proveedor desde CSV"""
    print("\n[1/6] Construyendo dim_proveedor...")

    csv_file = INPUT_DIR / "inventario" / "proveedores.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=[
                "id_proveedor",
                "nombre_proveedor",
                "razon_social",
                "nit",
                "pais_origen",
                "ciudad",
                "direccion",
                "telefono",
                "email",
                "contacto_principal",
                "dias_credito",
                "tipo_proveedor",
                "categoria_productos",
                "activo",
                "fecha_registro",
            ]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

        # Conversiones de tipos
        df["dias_credito"] = (
            pd.to_numeric(df["dias_credito"], errors="coerce").fillna(0).astype(int)
        )
        df["activo"] = (
            df["activo"]
            .map({"TRUE": True, "True": True, "true": True, "1": True})
            .fillna(False)
        )
        df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")

    return save_dimension(df, "dim_proveedor")


def build_dim_almacen():
    """Construye dim_almacen desde CSV"""
    print("\n[2/6] Construyendo dim_almacen...")

    csv_file = INPUT_DIR / "inventario" / "almacenes.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=[
                "id_almacen",
                "nombre_almacen",
                "tipo_almacen",
                "ciudad",
                "departamento",
                "direccion",
                "capacidad_m3",
                "encargado",
                "telefono",
                "activo",
                "fecha_apertura",
            ]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

        # Conversiones de tipos
        df["capacidad_m3"] = pd.to_numeric(df["capacidad_m3"], errors="coerce").fillna(
            0
        )
        df["activo"] = (
            df["activo"]
            .map({"TRUE": True, "True": True, "true": True, "1": True})
            .fillna(False)
        )
        df["fecha_apertura"] = pd.to_datetime(df["fecha_apertura"], errors="coerce")

    return save_dimension(df, "dim_almacen")


def build_dim_movimiento_tipo():
    """Construye dim_movimiento_tipo desde CSV"""
    print("\n[3/6] Construyendo dim_movimiento_tipo...")

    csv_file = INPUT_DIR / "inventario" / "tipos_movimiento.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=[
                "id_tipo_movimiento",
                "nombre_tipo",
                "categoria",
                "afecta_stock",
                "descripcion",
            ]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

    return save_dimension(df, "dim_movimiento_tipo")


# ============================================================================
# DIMENSIONES DE FINANZAS
# ============================================================================


def build_dim_cuenta_contable():
    """Construye dim_cuenta_contable desde CSV"""
    print("\n[4/6] Construyendo dim_cuenta_contable...")

    csv_file = INPUT_DIR / "finanzas" / "cuentas_contables.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=[
                "id_cuenta",
                "nombre_cuenta",
                "tipo_cuenta",
                "clasificacion",
                "cuenta_padre",
                "nivel",
                "naturaleza",
                "acepta_movimientos",
                "estado_financiero",
                "descripcion",
                "activa",
            ]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

        # Conversiones de tipos
        df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce").fillna(0).astype(int)
        df["acepta_movimientos"] = (
            df["acepta_movimientos"]
            .map({"TRUE": True, "True": True, "true": True, "1": True})
            .fillna(False)
        )
        df["activa"] = (
            df["activa"]
            .map({"TRUE": True, "True": True, "true": True, "1": True})
            .fillna(False)
        )

    return save_dimension(df, "dim_cuenta_contable")


def build_dim_centro_costo():
    """Construye dim_centro_costo desde CSV"""
    print("\n[5/6] Construyendo dim_centro_costo...")

    csv_file = INPUT_DIR / "finanzas" / "centros_costo.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=[
                "id_centro_costo",
                "nombre_centro",
                "tipo_centro",
                "responsable",
                "activo",
            ]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

        # Conversiones de tipos
        df["activo"] = (
            df["activo"]
            .map({"TRUE": True, "True": True, "true": True, "1": True})
            .fillna(False)
        )

    return save_dimension(df, "dim_centro_costo")


def build_dim_tipo_transaccion():
    """Construye dim_tipo_transaccion desde CSV"""
    print("\n[6/6] Construyendo dim_tipo_transaccion...")

    csv_file = INPUT_DIR / "finanzas" / "tipos_transaccion.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando dimensión vacía...")
        df = pd.DataFrame(
            columns=["id_tipo_transaccion", "nombre_tipo", "categoria", "descripcion"]
        )
    else:
        df = pd.read_csv(csv_file, dtype=str)

    return save_dimension(df, "dim_tipo_transaccion")


# ============================================================================
# TABLAS DE HECHOS
# ============================================================================


def build_fact_inventario():
    """Construye fact_inventario desde CSV"""
    print("\n[7/10] Construyendo fact_inventario...")

    csv_file = INPUT_DIR / "inventario" / "movimientos_inventario.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando tabla de hechos vacía...")
        df = pd.DataFrame(
            columns=[
                "id_producto",
                "id_almacen",
                "id_proveedor",
                "id_tipo_movimiento",
                "fecha_movimiento",
                "id_usuario",
                "numero_documento",
                "cantidad",
                "costo_unitario",
                "costo_total",
                "stock_anterior",
                "stock_resultante",
                "motivo",
                "observaciones",
                "id_fecha",
                "año",
                "mes",
                "dia",
            ]
        )
    else:
        df = pd.read_csv(csv_file)

        # Conversiones de tipos
        df["fecha_movimiento"] = pd.to_datetime(df["fecha_movimiento"], errors="coerce")
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
        df["costo_unitario"] = pd.to_numeric(
            df["costo_unitario"], errors="coerce"
        ).fillna(0)
        df["costo_total"] = pd.to_numeric(df["costo_total"], errors="coerce").fillna(0)
        df["stock_anterior"] = pd.to_numeric(
            df["stock_anterior"], errors="coerce"
        ).fillna(0)
        df["stock_resultante"] = pd.to_numeric(
            df["stock_resultante"], errors="coerce"
        ).fillna(0)

        # Agregar campos derivados de fecha
        df["id_fecha"] = df["fecha_movimiento"].dt.strftime("%Y%m%d").astype("Int64")
        df["año"] = df["fecha_movimiento"].dt.year
        df["mes"] = df["fecha_movimiento"].dt.month
        df["dia"] = df["fecha_movimiento"].dt.day

        # Convertir columnas de texto
        df["id_producto"] = df["id_producto"].astype(str)
        df["id_almacen"] = df["id_almacen"].astype(str)
        df["id_proveedor"] = df["id_proveedor"].astype(str).replace("nan", "")
        df["id_tipo_movimiento"] = df["id_tipo_movimiento"].astype(str)
        df["id_usuario"] = df["id_usuario"].astype(str)
        df["numero_documento"] = df["numero_documento"].astype(str).replace("nan", "")
        df["motivo"] = df["motivo"].astype(str).replace("nan", "")
        df["observaciones"] = df["observaciones"].astype(str).replace("nan", "")

    return save_fact_table(df, "fact_inventario")


def build_fact_transacciones_contables():
    """Construye fact_transacciones_contables desde CSV"""
    print("\n[8/10] Construyendo fact_transacciones_contables...")

    csv_file = INPUT_DIR / "finanzas" / "transacciones_contables.csv"

    if not csv_file.exists():
        print(f"   ⚠ Archivo no encontrado: {csv_file}")
        print("   ⚠ Creando tabla de hechos vacía...")
        df = pd.DataFrame(
            columns=[
                "numero_asiento",
                "fecha_asiento",
                "id_cuenta",
                "id_centro_costo",
                "id_tipo_transaccion",
                "id_usuario",
                "tipo_movimiento",
                "monto",
                "documento_referencia",
                "descripcion",
                "id_venta",
                "id_movimiento_inventario",
                "observaciones",
                "id_fecha",
                "año",
                "mes",
            ]
        )
    else:
        df = pd.read_csv(csv_file)

        # Conversiones de tipos
        df["fecha_asiento"] = pd.to_datetime(df["fecha_asiento"], errors="coerce")
        df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)

        # Agregar campos derivados de fecha
        df["id_fecha"] = df["fecha_asiento"].dt.strftime("%Y%m%d").astype("Int64")
        df["año"] = df["fecha_asiento"].dt.year
        df["mes"] = df["fecha_asiento"].dt.month

        # Convertir columnas de texto
        df["numero_asiento"] = df["numero_asiento"].astype(str)
        df["id_cuenta"] = df["id_cuenta"].astype(str)
        df["id_centro_costo"] = df["id_centro_costo"].astype(str)
        df["id_tipo_transaccion"] = df["id_tipo_transaccion"].astype(str)
        df["id_usuario"] = df["id_usuario"].astype(str)
        df["tipo_movimiento"] = df["tipo_movimiento"].astype(str)
        df["documento_referencia"] = (
            df["documento_referencia"].astype(str).replace("nan", "")
        )
        df["descripcion"] = df["descripcion"].astype(str).replace("nan", "")
        df["id_venta"] = df["id_venta"].astype(str).replace("nan", "")
        df["id_movimiento_inventario"] = (
            df["id_movimiento_inventario"].astype(str).replace("nan", "")
        )
        df["observaciones"] = df["observaciones"].astype(str).replace("nan", "")

    return save_fact_table(df, "fact_transacciones_contables")


def build_fact_estado_resultados():
    """Construye fact_estado_resultados agregando transacciones por mes"""
    print("\n[9/10] Construyendo fact_estado_resultados (agregado mensual)...")

    # Leer fact_transacciones_contables
    fact_file = PARQUET_DIR / "fact_transacciones_contables.parquet"

    if not fact_file.exists():
        print(f"   ⚠ Archivo no encontrado: {fact_file}")
        print("   ⚠ Creando tabla de hechos vacía...")
        df = pd.DataFrame(
            columns=[
                "año",
                "mes",
                "id_cuenta",
                "id_centro_costo",
                "monto_debe",
                "monto_haber",
                "saldo_neto",
            ]
        )
    else:
        df_trans = pd.read_parquet(fact_file)

        # Calcular montos debe y haber
        df_trans["monto_debe"] = df_trans.apply(
            lambda x: x["monto"] if x["tipo_movimiento"] == "debe" else 0, axis=1
        )
        df_trans["monto_haber"] = df_trans.apply(
            lambda x: x["monto"] if x["tipo_movimiento"] == "haber" else 0, axis=1
        )

        # Agrupar por año, mes, cuenta y centro de costo
        df = (
            df_trans.groupby(["año", "mes", "id_cuenta", "id_centro_costo"])
            .agg({"monto_debe": "sum", "monto_haber": "sum"})
            .reset_index()
        )

        # Calcular saldo neto
        df["saldo_neto"] = df["monto_debe"] - df["monto_haber"]

    return save_fact_table(df, "fact_estado_resultados")


def build_fact_balance_general():
    """Construye fact_balance_general calculando saldos acumulados"""
    print("\n[10/10] Construyendo fact_balance_general (saldos a fecha)...")

    # Leer fact_transacciones_contables
    fact_file = PARQUET_DIR / "fact_transacciones_contables.parquet"

    if not fact_file.exists():
        print(f"   ⚠ Archivo no encontrado: {fact_file}")
        print("   ⚠ Creando tabla de hechos vacía...")
        df = pd.DataFrame(columns=["id_fecha", "id_cuenta", "saldo", "tipo_saldo"])
    else:
        df_trans = pd.read_parquet(fact_file)

        # Leer dim_cuenta_contable para obtener naturaleza
        dim_cuenta_file = PARQUET_DIR / "dim_cuenta_contable.parquet"
        if dim_cuenta_file.exists():
            df_cuentas = pd.read_parquet(dim_cuenta_file)
            df_trans = df_trans.merge(
                df_cuentas[["id_cuenta", "naturaleza"]], on="id_cuenta", how="left"
            )
        else:
            df_trans["naturaleza"] = "deudora"

        # Calcular saldo según naturaleza de la cuenta
        df_trans["saldo_movimiento"] = df_trans.apply(
            lambda x: (
                x["monto"]
                if (x["tipo_movimiento"] == "debe" and x["naturaleza"] == "deudora")
                or (x["tipo_movimiento"] == "haber" and x["naturaleza"] == "acreedora")
                else -x["monto"]
            ),
            axis=1,
        )

        # Agrupar por fecha y cuenta
        df = (
            df_trans.groupby(["id_fecha", "id_cuenta"])
            .agg({"saldo_movimiento": "sum"})
            .reset_index()
        )

        df.rename(columns={"saldo_movimiento": "saldo"}, inplace=True)

        # Calcular saldo acumulado por cuenta
        df = df.sort_values(["id_cuenta", "id_fecha"])
        df["saldo"] = df.groupby("id_cuenta")["saldo"].cumsum()

        # Determinar tipo de saldo
        df["tipo_saldo"] = df["saldo"].apply(
            lambda x: "deudor" if x >= 0 else "acreedor"
        )
        df["saldo"] = df["saldo"].abs()

    return save_fact_table(df, "fact_balance_general")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================


def main():
    """Ejecuta la construcción de todas las dimensiones y hechos"""
    print("=" * 70)
    print("CONSTRUCCIÓN DE DIMENSIONES Y HECHOS - INVENTARIO Y FINANZAS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Entrada: {INPUT_DIR}")
    print(f"Salida Parquet: {PARQUET_DIR}")
    print(f"Salida CSV: {CSV_DIR}")

    total_dims = 0
    total_facts = 0

    # Construir dimensiones de inventario
    print("\n" + "=" * 70)
    print("DIMENSIONES DE INVENTARIO")
    print("=" * 70)
    total_dims += build_dim_proveedor()
    total_dims += build_dim_almacen()
    total_dims += build_dim_movimiento_tipo()

    # Construir dimensiones de finanzas
    print("\n" + "=" * 70)
    print("DIMENSIONES DE FINANZAS")
    print("=" * 70)
    total_dims += build_dim_cuenta_contable()
    total_dims += build_dim_centro_costo()
    total_dims += build_dim_tipo_transaccion()

    # Construir tablas de hechos
    print("\n" + "=" * 70)
    print("TABLAS DE HECHOS")
    print("=" * 70)
    total_facts += build_fact_inventario()
    total_facts += build_fact_transacciones_contables()
    total_facts += build_fact_estado_resultados()
    total_facts += build_fact_balance_general()

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"✓ Dimensiones construidas: 6 tablas con {total_dims:,} registros")
    print(f"✓ Hechos construidos: 4 tablas con {total_facts:,} registros")
    print(f"✓ Archivos generados en:")
    print(f"  - {PARQUET_DIR}")
    print(f"  - {CSV_DIR}")
    print("\n¡Proceso completado exitosamente!")


if __name__ == "__main__":
    main()
