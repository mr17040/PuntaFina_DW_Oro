#!/usr/bin/env python3
"""
Script de validación: Compara el README con la estructura implementada en el DW
"""
import psycopg2
from tabulate import tabulate

DB_CONFIG = {
    'host': 'localhost',
    'database': 'datawarehouse_bi',
    'user': 'sa',
    'password': 'IngDatos123*'
}

# Estructura esperada según README
ESTRUCTURA_README = {
    'DIMENSIONES': {
        # Conformadas
        'dim_fecha': {'columnas': 14, 'modulo': 'CONFORMADA', 'descripcion': 'Dimensión temporal'},
        'dim_usuario': {'columnas': 8, 'modulo': 'CONFORMADA', 'descripcion': 'Usuarios del sistema'},
        'dim_detalle_venta': {'columnas': 30, 'modulo': 'CONFORMADA', 'descripcion': 'Productos con métricas'},
        
        # Ventas
        'dim_cliente': {'columnas': 40, 'modulo': 'VENTAS', 'descripcion': 'Clientes con RFM y ML'},
        'dim_producto': {'columnas': 10, 'modulo': 'VENTAS', 'descripcion': 'Catálogo de productos'},
        'dim_sitio_web': {'columnas': 6, 'modulo': 'VENTAS', 'descripcion': 'Sitios web'},
        'dim_canal': {'columnas': 5, 'modulo': 'VENTAS', 'descripcion': 'Canales de venta'},
        'dim_direccion': {'columnas': 9, 'modulo': 'VENTAS', 'descripcion': 'Direcciones'},
        'dim_envio': {'columnas': 6, 'modulo': 'VENTAS', 'descripcion': 'Métodos de envío'},
        'dim_pago': {'columnas': 7, 'modulo': 'VENTAS', 'descripcion': 'Métodos de pago'},
        'dim_estado_orden': {'columnas': 8, 'modulo': 'VENTAS', 'descripcion': 'Estados de orden'},
        'dim_impuestos': {'columnas': 6, 'modulo': 'VENTAS', 'descripcion': 'Impuestos'},
        'dim_promocion': {'columnas': 8, 'modulo': 'VENTAS', 'descripcion': 'Promociones'},
        'dim_orden': {'columnas': 8, 'modulo': 'VENTAS', 'descripcion': 'Órdenes'},
        'dim_line_item': {'columnas': 4, 'modulo': 'VENTAS', 'descripcion': 'Líneas de pedido'},
        'dim_estado_pago': {'columnas': 5, 'modulo': 'VENTAS', 'descripcion': 'Estados de pago'},
        
        # Inventario
        'dim_almacen': {'columnas': 9, 'modulo': 'INVENTARIO', 'descripcion': 'Almacenes'},
        'dim_proveedor': {'columnas': 11, 'modulo': 'INVENTARIO', 'descripcion': 'Proveedores'},
        'dim_tipo_movimiento': {'columnas': 8, 'modulo': 'INVENTARIO', 'descripcion': 'Tipos de movimiento'},
        'dim_categoria_producto': {'columnas': 8, 'modulo': 'INVENTARIO', 'descripcion': 'Categorías'},
        
        # Finanzas
        'dim_cuenta_contable': {'columnas': 10, 'modulo': 'FINANZAS', 'descripcion': 'Plan de cuentas'},
        'dim_centro_costo': {'columnas': 8, 'modulo': 'FINANZAS', 'descripcion': 'Centros de costo'},
        'dim_tipo_transaccion': {'columnas': 8, 'modulo': 'FINANZAS', 'descripcion': 'Tipos de transacción'},
        'dim_periodo_contable': {'columnas': 8, 'modulo': 'FINANZAS', 'descripcion': 'Períodos contables'},
    },
    'FACTS': {
        'fact_ventas': {'columnas': 16, 'modulo': 'VENTAS', 'descripcion': 'Transacciones de venta'},
        'fact_inventario': {'columnas': 13, 'modulo': 'INVENTARIO', 'descripcion': 'Movimientos de inventario'},
        'fact_transacciones': {'columnas': 12, 'modulo': 'FINANZAS', 'descripcion': 'Transacciones contables'},
        'fact_balance': {'columnas': 7, 'modulo': 'FINANZAS', 'descripcion': 'Balance general'},
        'fact_estado_resultados': {'columnas': 9, 'modulo': 'FINANZAS', 'descripcion': 'Estado de resultados'},
    }
}

def get_db_tables():
    """Obtener todas las tablas del DW"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns 
             WHERE table_name = t.table_name AND table_schema = 'public') as num_columnas,
            (SELECT COUNT(*) FROM (SELECT 1 FROM pg_class WHERE relname = t.table_name LIMIT 1) x) as existe
        FROM information_schema.tables t
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND (table_name LIKE 'dim_%' OR table_name LIKE 'fact_%')
        ORDER BY table_name
    """)
    
    result = {}
    for row in cursor.fetchall():
        table_name, num_cols, existe = row
        result[table_name] = {'columnas': num_cols, 'existe': bool(existe)}
    
    cursor.close()
    conn.close()
    return result

def get_table_row_count(table_name):
    """Obtener cantidad de registros en una tabla"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except:
        return 0

def validar_estructura():
    """Validar la estructura completa"""
    print("=" * 100)
    print("🔍 VALIDACIÓN: README vs IMPLEMENTACIÓN DEL DATA WAREHOUSE")
    print("=" * 100)
    print()
    
    db_tables = get_db_tables()
    
    # Validar dimensiones
    print("📊 DIMENSIONES")
    print("-" * 100)
    
    dim_data = []
    total_dims = len(ESTRUCTURA_README['DIMENSIONES'])
    dims_ok = 0
    dims_estructura_ok = 0
    dims_pobladas = 0
    
    for table_name, expected in ESTRUCTURA_README['DIMENSIONES'].items():
        if table_name in db_tables:
            actual_cols = db_tables[table_name]['columnas']
            status = "✅" if actual_cols >= expected['columnas'] * 0.8 else "⚠️"
            
            # Verificar si tiene datos
            row_count = get_table_row_count(table_name)
            poblada = "✅" if row_count > 0 else "❌"
            
            if actual_cols >= expected['columnas'] * 0.8:
                dims_estructura_ok += 1
            if row_count > 0:
                dims_pobladas += 1
            
            dims_ok += 1
            dim_data.append([
                table_name,
                expected['modulo'],
                expected['descripcion'][:30],
                f"{actual_cols}/{expected['columnas']}",
                status,
                row_count,
                poblada
            ])
        else:
            dim_data.append([
                table_name,
                expected['modulo'],
                expected['descripcion'][:30],
                f"0/{expected['columnas']}",
                "❌",
                0,
                "❌"
            ])
    
    print(tabulate(dim_data, headers=['Tabla', 'Módulo', 'Descripción', 'Cols (Real/Esp)', 'Estructura', 'Registros', 'Poblada'], tablefmt='grid'))
    print()
    print(f"📈 Resumen Dimensiones: {dims_ok}/{total_dims} creadas | {dims_estructura_ok}/{total_dims} con estructura correcta | {dims_pobladas}/{total_dims} pobladas")
    print()
    
    # Validar facts
    print("📊 TABLAS DE HECHOS")
    print("-" * 100)
    
    fact_data = []
    total_facts = len(ESTRUCTURA_README['FACTS'])
    facts_ok = 0
    facts_estructura_ok = 0
    facts_pobladas = 0
    
    for table_name, expected in ESTRUCTURA_README['FACTS'].items():
        if table_name in db_tables:
            actual_cols = db_tables[table_name]['columnas']
            status = "✅" if actual_cols >= expected['columnas'] * 0.8 else "⚠️"
            
            # Verificar si tiene datos
            row_count = get_table_row_count(table_name)
            poblada = "✅" if row_count > 0 else "❌"
            
            if actual_cols >= expected['columnas'] * 0.8:
                facts_estructura_ok += 1
            if row_count > 0:
                facts_pobladas += 1
            
            facts_ok += 1
            fact_data.append([
                table_name,
                expected['modulo'],
                expected['descripcion'][:30],
                f"{actual_cols}/{expected['columnas']}",
                status,
                row_count,
                poblada
            ])
        else:
            fact_data.append([
                table_name,
                expected['modulo'],
                expected['descripcion'][:30],
                f"0/{expected['columnas']}",
                "❌",
                0,
                "❌"
            ])
    
    print(tabulate(fact_data, headers=['Tabla', 'Módulo', 'Descripción', 'Cols (Real/Esp)', 'Estructura', 'Registros', 'Poblada'], tablefmt='grid'))
    print()
    print(f"📈 Resumen Facts: {facts_ok}/{total_facts} creadas | {facts_estructura_ok}/{total_facts} con estructura correcta | {facts_pobladas}/{total_facts} pobladas")
    print()
    
    # Resumen general
    print("=" * 100)
    print("📊 RESUMEN GENERAL")
    print("=" * 100)
    total_tablas = total_dims + total_facts
    total_creadas = dims_ok + facts_ok
    total_estructura = dims_estructura_ok + facts_estructura_ok
    total_pobladas = dims_pobladas + facts_pobladas
    
    print(f"✅ Tablas creadas: {total_creadas}/{total_tablas} ({total_creadas/total_tablas*100:.1f}%)")
    print(f"✅ Estructura correcta: {total_estructura}/{total_tablas} ({total_estructura/total_tablas*100:.1f}%)")
    print(f"⚠️  Tablas pobladas: {total_pobladas}/{total_tablas} ({total_pobladas/total_tablas*100:.1f}%)")
    print()
    
    # Estado por módulo
    print("📦 ESTADO POR MÓDULO:")
    print()
    
    modulos = {}
    for tables_dict in [ESTRUCTURA_README['DIMENSIONES'], ESTRUCTURA_README['FACTS']]:
        for table_name, info in tables_dict.items():
            modulo = info['modulo']
            if modulo not in modulos:
                modulos[modulo] = {'total': 0, 'creadas': 0, 'pobladas': 0}
            modulos[modulo]['total'] += 1
            if table_name in db_tables:
                modulos[modulo]['creadas'] += 1
                if get_table_row_count(table_name) > 0:
                    modulos[modulo]['pobladas'] += 1
    
    modulo_data = []
    for modulo, stats in sorted(modulos.items()):
        modulo_data.append([
            modulo,
            f"{stats['creadas']}/{stats['total']}",
            f"{stats['creadas']/stats['total']*100:.0f}%",
            f"{stats['pobladas']}/{stats['total']}",
            f"{stats['pobladas']/stats['total']*100:.0f}%"
        ])
    
    print(tabulate(modulo_data, headers=['Módulo', 'Creadas', '%', 'Pobladas', '%'], tablefmt='grid'))
    print()
    
    # Recomendaciones
    print("🎯 RECOMENDACIONES:")
    print()
    if dims_pobladas < total_dims / 2:
        print("⚠️  1. Ejecutar ETL completo para poblar las dimensiones")
        print("   Comando: cd /root/PuntaFina_DW_Oro/etl_batch && python main.py run")
        print()
    if total_pobladas == 0:
        print("⚠️  2. Las tablas están vacías. Necesita poblar con datos reales.")
        print()
    if total_estructura < total_tablas:
        print("⚠️  3. Algunas tablas tienen menos columnas de las esperadas según README")
        print()
    
    print("=" * 100)

if __name__ == '__main__':
    validar_estructura()
