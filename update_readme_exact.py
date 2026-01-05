#!/usr/bin/env python3
"""
Script para actualizar el README con la información exacta de la base de datos
"""
import psycopg2
from datetime import datetime

def get_db_connection():
    """Conectar a la base de datos"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="datawarehouse_bi",
            user="sa",
            password="IngDatos123*"
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def get_all_table_counts(conn):
    """Obtener conteo de registros de todas las tablas"""
    cursor = conn.cursor()
    
    tables = [
        'dim_almacen', 'dim_canal', 'dim_categoria_producto', 'dim_centro_costo',
        'dim_cliente', 'dim_cuenta_contable', 'dim_detalle_venta', 'dim_direccion',
        'dim_envio', 'dim_estado_orden', 'dim_estado_pago', 'dim_fecha',
        'dim_impuestos', 'dim_line_item', 'dim_orden', 'dim_pago',
        'dim_periodo_contable', 'dim_producto', 'dim_promocion', 'dim_proveedor',
        'dim_sitio_web', 'dim_tipo_movimiento', 'dim_tipo_transaccion', 'dim_usuario',
        'fact_balance', 'fact_estado_resultados', 'fact_inventario',
        'fact_transacciones', 'fact_ventas'
    ]
    
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        counts[table] = cursor.fetchone()[0]
    
    cursor.close()
    return counts

def get_table_details(conn, table_name):
    """Obtener detalles completos de una tabla"""
    cursor = conn.cursor()
    
    # Obtener columnas
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, (table_name,))
    
    columns = cursor.fetchall()
    
    # Obtener primary keys
    cursor.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = %s
        AND tc.constraint_type = 'PRIMARY KEY';
    """, (table_name,))
    
    pk_cols = [row[0] for row in cursor.fetchall()]
    
    # Obtener foreign keys
    cursor.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name,
            ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s;
    """, (table_name,))
    
    fk_cols = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    cursor.close()
    
    return {
        'columns': columns,
        'pk_cols': pk_cols,
        'fk_cols': fk_cols
    }

def format_type(data_type, char_len, num_prec, num_scale):
    """Formatear tipo de dato"""
    if data_type == 'character varying':
        return f'VARCHAR({char_len})' if char_len else 'VARCHAR'
    elif data_type == 'numeric':
        if num_prec and num_scale:
            return f'NUMERIC({num_prec},{num_scale})'
        return 'NUMERIC'
    elif data_type == 'integer':
        return 'INTEGER'
    elif data_type == 'timestamp without time zone':
        return 'TIMESTAMP'
    elif data_type == 'date':
        return 'DATE'
    elif data_type == 'boolean':
        return 'BOOLEAN'
    elif data_type == 'text':
        return 'TEXT'
    else:
        return data_type.upper()

def generate_table_section(table_name, details, count):
    """Generar sección markdown para una tabla"""
    md = f"\n### 📊 {table_name}\n"
    md += f"**Registros:** {count:,}\n\n"
    md += "| Campo | Tipo | Clave | Nullable | Default | Descripción |\n"
    md += "|-------|------|-------|----------|---------|-------------|\n"
    
    for col in details['columns']:
        col_name = col[0]
        data_type = format_type(col[1], col[2], col[3], col[4])
        is_nullable = 'Sí' if col[5] == 'YES' else 'No'
        col_default = col[6] if col[6] else '-'
        
        # Simplificar defaults
        if col_default and 'nextval' in str(col_default):
            col_default = 'SERIAL'
        elif col_default == 'CURRENT_TIMESTAMP':
            col_default = 'NOW()'
        elif col_default == 'true':
            col_default = 'true'
        elif col_default == 'false':
            col_default = 'false'
        elif col_default == '1':
            col_default = '1'
        elif len(str(col_default)) > 25:
            col_default = str(col_default)[:22] + '...'
        
        # Determinar tipo de clave
        key_type = '-'
        if col_name in details['pk_cols']:
            key_type = 'PK'
        if col_name in details['fk_cols']:
            key_type = 'FK' if key_type == '-' else 'PK, FK'
        
        md += f"| {col_name} | {data_type} | {key_type} | {is_nullable} | {col_default} | |\n"
    
    # Foreign Keys
    if details['fk_cols']:
        md += "\n**Foreign Keys:**\n"
        for col_name, (ref_table, ref_col) in details['fk_cols'].items():
            md += f"- `{col_name}` → `{ref_table}({ref_col})`\n"
    
    md += "\n---\n"
    return md

def main():
    print("=" * 70)
    print("ACTUALIZANDO README CON INFORMACIÓN EXACTA DE LA BASE DE DATOS")
    print("=" * 70)
    
    conn = get_db_connection()
    if not conn:
        return
    
    # Obtener conteos
    print("\n📊 Obteniendo conteo de registros...")
    counts = get_all_table_counts(conn)
    
    # Mostrar resumen
    print(f"\n✅ Tablas encontradas: {len(counts)}")
    print(f"\nRegistros por módulo:")
    
    # Ventas
    ventas_tables = ['dim_cliente', 'dim_sitio_web', 'dim_canal', 'dim_direccion', 
                     'dim_envio', 'dim_pago', 'dim_estado_orden', 'dim_estado_pago',
                     'dim_impuestos', 'dim_promocion', 'dim_orden', 'dim_line_item', 
                     'dim_detalle_venta', 'dim_usuario', 'fact_ventas']
    ventas_total = sum(counts.get(t, 0) for t in ventas_tables if 'fact' in t or 'dim_orden' in t or 'dim_line' in t)
    print(f"  VENTAS: {ventas_total:,} registros")
    
    # Inventario
    inventario_total = counts.get('fact_inventario', 0)
    print(f"  INVENTARIO: {inventario_total:,} registros")
    
    # Finanzas
    finanzas_total = (counts.get('fact_transacciones', 0) + 
                      counts.get('fact_estado_resultados', 0) + 
                      counts.get('fact_balance', 0))
    print(f"  FINANZAS: {finanzas_total:,} registros")
    
    print(f"\nTotal general de hechos: {ventas_total + inventario_total + finanzas_total:,}")
    
    # Generar actualización
    print("\n📝 Generando actualización del README...")
    
    output = []
    output.append(f"<!-- ACTUALIZADO AUTOMÁTICAMENTE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n")
    output.append("## 📊 RESUMEN EJECUTIVO\n\n")
    output.append(f"### Totales por Módulo\n\n")
    output.append(f"- **VENTAS:** {counts['fact_ventas']:,} registros en fact_ventas\n")
    output.append(f"- **INVENTARIO:** {counts['fact_inventario']:,} registros en fact_inventario\n")
    output.append(f"- **FINANZAS:** {counts['fact_transacciones']:,} transacciones + {counts['fact_estado_resultados']:,} estado resultados + {counts['fact_balance']:,} balance\n")
    output.append(f"- **TOTAL HECHOS:** {counts['fact_ventas'] + counts['fact_inventario'] + counts['fact_transacciones']:,} registros\n\n")
    
    output.append(f"### Dimensiones Principales\n\n")
    output.append(f"- **dim_cliente:** {counts['dim_cliente']:,} clientes\n")
    output.append(f"- **dim_producto:** {counts['dim_producto']:,} productos\n")
    output.append(f"- **dim_fecha:** {counts['dim_fecha']:,} fechas\n")
    output.append(f"- **dim_orden:** {counts['dim_orden']:,} órdenes\n")
    output.append(f"- **dim_direccion:** {counts['dim_direccion']:,} direcciones\n\n")
    
    # Guardar
    with open('/root/PuntaFina_DW_Oro/docs/readme_update.md', 'w', encoding='utf-8') as f:
        f.write(''.join(output))
    
    print(f"\n✅ Actualización guardada en: docs/readme_update.md")
    
    # Generar tabla completa para cada tabla
    print(f"\n📝 Generando documentación detallada...")
    
    all_tables = sorted(counts.keys())
    full_doc = []
    
    for table in all_tables:
        details = get_table_details(conn, table)
        section = generate_table_section(table, details, counts[table])
        full_doc.append(section)
    
    with open('/root/PuntaFina_DW_Oro/docs/database_tables_complete.md', 'w', encoding='utf-8') as f:
        f.write(f"# 📋 Estructura Completa de Tablas\n\n")
        f.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(''.join(full_doc))
    
    print(f"✅ Documentación completa guardada en: docs/database_tables_complete.md")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    main()
