#!/usr/bin/env python3
"""
Script para generar documentación exacta del README basado en la estructura real de la base de datos
"""
import psycopg2
from psycopg2 import sql
import sys

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
        sys.exit(1)

def get_table_structure(conn, table_name):
    """Obtener estructura exacta de una tabla"""
    cursor = conn.cursor()
    
    # Obtener columnas con tipos, valores por defecto, etc.
    query = """
    SELECT 
        c.column_name,
        c.data_type,
        c.character_maximum_length,
        c.numeric_precision,
        c.numeric_scale,
        c.is_nullable,
        c.column_default,
        CASE 
            WHEN pk.column_name IS NOT NULL THEN 'PK'
            WHEN fk.column_name IS NOT NULL THEN 'FK'
            ELSE ''
        END as key_type
    FROM information_schema.columns c
    LEFT JOIN (
        SELECT ku.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage ku 
            ON tc.constraint_name = ku.constraint_name
        WHERE tc.table_name = %s
        AND tc.constraint_type = 'PRIMARY KEY'
    ) pk ON c.column_name = pk.column_name
    LEFT JOIN (
        SELECT ku.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage ku 
            ON tc.constraint_name = ku.constraint_name
        WHERE tc.table_name = %s
        AND tc.constraint_type = 'FOREIGN KEY'
    ) fk ON c.column_name = fk.column_name
    WHERE c.table_name = %s
    AND c.table_schema = 'public'
    ORDER BY c.ordinal_position;
    """
    
    cursor.execute(query, (table_name, table_name, table_name))
    columns = cursor.fetchall()
    
    # Obtener foreign keys
    fk_query = """
    SELECT
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = %s
        AND tc.table_schema = 'public';
    """
    cursor.execute(fk_query, (table_name,))
    foreign_keys = cursor.fetchall()
    
    # Obtener índices
    idx_query = """
    SELECT
        indexname,
        indexdef
    FROM pg_indexes
    WHERE tablename = %s
    AND schemaname = 'public'
    ORDER BY indexname;
    """
    cursor.execute(idx_query, (table_name,))
    indexes = cursor.fetchall()
    
    # Obtener conteo de registros
    count_query = f"SELECT COUNT(*) FROM {table_name};"
    cursor.execute(count_query)
    record_count = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        'columns': columns,
        'foreign_keys': foreign_keys,
        'indexes': indexes,
        'record_count': record_count
    }

def format_data_type(data_type, char_max_len, num_precision, num_scale):
    """Formatear tipo de dato con precisión exacta"""
    if data_type == 'character varying':
        if char_max_len:
            return f'VARCHAR({char_max_len})'
        return 'VARCHAR'
    elif data_type == 'numeric':
        if num_precision and num_scale:
            return f'NUMERIC({num_precision},{num_scale})'
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

def generate_table_markdown(table_name, structure):
    """Generar markdown para una tabla específica"""
    md = f"\n### 📊 {table_name}\n\n"
    md += f"**Registros:** {structure['record_count']:,}\n\n"
    
    # Tabla de campos
    md += "| Campo | Tipo | Clave | Nullable | Default | Descripción |\n"
    md += "|-------|------|-------|----------|---------|-------------|\n"
    
    for col in structure['columns']:
        col_name = col[0]
        data_type = format_data_type(col[1], col[2], col[3], col[4])
        is_nullable = 'Sí' if col[5] == 'YES' else 'No'
        col_default = col[6] if col[6] else '-'
        key_type = col[7] if col[7] else '-'
        
        # Simplificar defaults largos
        if col_default.startswith('nextval'):
            col_default = 'AUTO'
        elif col_default == 'CURRENT_TIMESTAMP':
            col_default = 'NOW'
        elif len(str(col_default)) > 20:
            col_default = col_default[:17] + '...'
            
        md += f"| {col_name} | {data_type} | {key_type} | {is_nullable} | {col_default} | |\n"
    
    # Foreign Keys
    if structure['foreign_keys']:
        md += "\n**Foreign Keys:**\n"
        for fk in structure['foreign_keys']:
            md += f"- `{fk[0]}` → `{fk[1]}({fk[2]})`\n"
    
    # Índices
    if structure['indexes']:
        md += "\n**Índices:**\n"
        for idx in structure['indexes']:
            md += f"- `{idx[0]}`\n"
    
    md += "\n---\n"
    return md

def main():
    print("Generando documentación exacta de la base de datos...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    # Generar documentación completa
    doc = "# 📋 Documentación Exacta de la Base de Datos\n\n"
    doc += f"**Base de datos:** datawarehouse_bi\n"
    doc += f"**Total de tablas:** {len(tables)}\n\n"
    
    # Separar dimensiones y facts
    dims = [t for t in tables if t.startswith('dim_')]
    facts = [t for t in tables if t.startswith('fact_')]
    
    doc += f"## 📊 Resumen\n\n"
    doc += f"- **Dimensiones:** {len(dims)}\n"
    doc += f"- **Tablas de Hechos:** {len(facts)}\n\n"
    
    # Documentar dimensiones
    doc += "## 🔷 Dimensiones\n\n"
    for table in dims:
        structure = get_table_structure(conn, table)
        doc += generate_table_markdown(table, structure)
    
    # Documentar facts
    doc += "## 🎯 Tablas de Hechos (Facts)\n\n"
    for table in facts:
        structure = get_table_structure(conn, table)
        doc += generate_table_markdown(table, structure)
    
    # Guardar documentación
    with open('/tmp/database_exact_structure.md', 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"\n✅ Documentación generada en: /tmp/database_exact_structure.md")
    print(f"\n📊 Estadísticas:")
    print(f"   - Dimensiones: {len(dims)}")
    print(f"   - Facts: {len(facts)}")
    print(f"   - Total tablas: {len(tables)}")
    
    # Mostrar conteo de registros
    print(f"\n📈 Registros por tabla:")
    for table in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"   - {table}: {count:,}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
