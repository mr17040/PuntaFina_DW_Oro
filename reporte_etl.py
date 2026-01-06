#!/usr/bin/env python3
"""
Reporte completo del estado del Data Warehouse
"""
import psycopg2
from datetime import datetime

# Configuración de conexión
DB_CONFIG = {
    'host': '104.156.246.237',
    'port': 5432,
    'database': 'puntafina_dw',
    'user': 'sa',
    'password': 'IngDatos123*'
}

def get_connection():
    """Crear conexión a la base de datos"""
    return psycopg2.connect(**DB_CONFIG)

def get_table_counts(conn):
    """Obtener conteos de todas las tablas dim y fact"""
    query = """
    SELECT 
        table_name,
        CASE 
            WHEN table_name LIKE 'dim_%' THEN 'DIMENSION'
            WHEN table_name LIKE 'fact_%' THEN 'HECHO'
        END as tipo
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_type = 'BASE TABLE'
      AND (table_name LIKE 'dim_%' OR table_name LIKE 'fact_%')
    ORDER BY tipo, table_name
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        tables = cur.fetchall()
        
        results = []
        for table_name, tipo in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            results.append({
                'tabla': table_name,
                'tipo': tipo,
                'registros': count,
                'estado': '✅ POBLADA' if count > 0 else '❌ VACÍA'
            })
        
        return results

def get_fact_details(conn):
    """Obtener detalles de las tablas de hechos"""
    facts = ['fact_ventas', 'fact_inventario', 'fact_transacciones', 'fact_balance', 'fact_estado_resultados']
    
    results = []
    with conn.cursor() as cur:
        for fact in facts:
            try:
                # Primero intentar con fecha_id
                query = f"""
                SELECT 
                    COUNT(*) as total,
                    MIN(fecha_id) as fecha_min,
                    MAX(fecha_id) as fecha_max
                FROM {fact}
                """
                cur.execute(query)
                count, fecha_min, fecha_max = cur.fetchone()
                
                results.append({
                    'tabla': fact,
                    'registros': count,
                    'fecha_min': fecha_min,
                    'fecha_max': fecha_max
                })
            except Exception as e:
                # Hacer rollback para poder ejecutar más queries
                conn.rollback()
                
                # Si no tiene fecha_id, intentar con periodo_id
                if 'fecha_id' in str(e) and 'does not exist' in str(e):
                    try:
                        query = f"""
                        SELECT 
                            COUNT(*) as total,
                            MIN(periodo_id) as periodo_min,
                            MAX(periodo_id) as periodo_max
                        FROM {fact}
                        """
                        cur.execute(query)
                        count, periodo_min, periodo_max = cur.fetchone()
                        
                        # Convertir periodo_id (YYYYMM) a fecha_id (YYYYMM01)
                        fecha_min = periodo_min * 100 + 1 if periodo_min else None
                        fecha_max = periodo_max * 100 + 1 if periodo_max else None
                        
                        results.append({
                            'tabla': fact,
                            'registros': count,
                            'fecha_min': fecha_min,
                            'fecha_max': fecha_max
                        })
                    except Exception as e2:
                        conn.rollback()
                        results.append({
                            'tabla': fact,
                            'registros': 0,
                            'fecha_min': None,
                            'fecha_max': None,
                            'error': str(e2)
                        })
                else:
                    results.append({
                        'tabla': fact,
                        'registros': 0,
                        'fecha_min': None,
                        'fecha_max': None,
                        'error': str(e)
                    })
    
    return results

def print_report():
    """Generar reporte completo"""
    print("=" * 80)
    print(f"📊 REPORTE ETL DATA WAREHOUSE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"\n🔗 Conexión: {DB_CONFIG['host']} - Base de datos: {DB_CONFIG['database']}\n")
    
    try:
        conn = get_connection()
        
        # Obtener conteos de todas las tablas
        tables = get_table_counts(conn)
        
        # Agrupar por tipo
        dimensiones = [t for t in tables if t['tipo'] == 'DIMENSION']
        hechos = [t for t in tables if t['tipo'] == 'HECHO']
        
        # Reporte de dimensiones
        print("📐 TABLAS DE DIMENSIONES")
        print("-" * 80)
        print(f"{'Tabla':<35} {'Registros':>15} {'Estado':>20}")
        print("-" * 80)
        
        total_dim_registros = 0
        total_dim_pobladas = 0
        
        for dim in dimensiones:
            print(f"{dim['tabla']:<35} {dim['registros']:>15,} {dim['estado']:>20}")
            total_dim_registros += dim['registros']
            if dim['registros'] > 0:
                total_dim_pobladas += 1
        
        print("-" * 80)
        print(f"{'TOTAL DIMENSIONES':<35} {total_dim_registros:>15,}")
        print(f"Pobladas: {total_dim_pobladas}/{len(dimensiones)}\n")
        
        # Reporte de hechos
        print("📊 TABLAS DE HECHOS")
        print("-" * 80)
        print(f"{'Tabla':<35} {'Registros':>15} {'Estado':>20}")
        print("-" * 80)
        
        total_fact_registros = 0
        total_fact_pobladas = 0
        
        for fact in hechos:
            print(f"{fact['tabla']:<35} {fact['registros']:>15,} {fact['estado']:>20}")
            total_fact_registros += fact['registros']
            if fact['registros'] > 0:
                total_fact_pobladas += 1
        
        print("-" * 80)
        print(f"{'TOTAL HECHOS':<35} {total_fact_registros:>15,}")
        print(f"Pobladas: {total_fact_pobladas}/{len(hechos)}\n")
        
        # Detalles de hechos con rangos de fechas
        print("📅 RANGOS DE FECHAS EN TABLAS DE HECHOS")
        print("-" * 80)
        print(f"{'Tabla':<25} {'Registros':>12} {'Fecha Mínima':>15} {'Fecha Máxima':>15}")
        print("-" * 80)
        
        fact_details = get_fact_details(conn)
        for detail in fact_details:
            if detail['registros'] > 0:
                print(f"{detail['tabla']:<25} {detail['registros']:>12,} {str(detail['fecha_min']):>15} {str(detail['fecha_max']):>15}")
            else:
                print(f"{detail['tabla']:<25} {detail['registros']:>12,} {'N/A':>15} {'N/A':>15}")
        
        print("-" * 80)
        
        # Resumen general
        total_registros = total_dim_registros + total_fact_registros
        total_tablas = len(dimensiones) + len(hechos)
        total_pobladas = total_dim_pobladas + total_fact_pobladas
        
        print("\n" + "=" * 80)
        print("📈 RESUMEN GENERAL")
        print("=" * 80)
        print(f"Total de tablas: {total_tablas} ({len(dimensiones)} dimensiones + {len(hechos)} hechos)")
        print(f"Tablas pobladas: {total_pobladas}/{total_tablas} ({(total_pobladas/total_tablas*100):.1f}%)")
        print(f"Total de registros: {total_registros:,}")
        print(f"  - Dimensiones: {total_dim_registros:,}")
        print(f"  - Hechos: {total_fact_registros:,}")
        
        # Estado general
        if total_pobladas == total_tablas:
            print(f"\n✅ ESTADO: TODAS LAS TABLAS ESTÁN POBLADAS")
        else:
            print(f"\n⚠️ ESTADO: {total_tablas - total_pobladas} TABLA(S) SIN DATOS")
            print("\nTablas vacías:")
            for t in tables:
                if t['registros'] == 0:
                    print(f"  - {t['tabla']}")
        
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print_report()
