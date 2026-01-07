#!/usr/bin/env python3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

print("="*80)
print("CARGANDO DIMENSIONES DESDE ORIGEN")
print("="*80)

dw_conn = psycopg2.connect(
    host='104.156.246.237', port=5432,
    dbname='datawarehouse_bi', user='sa', password='IngDatos123*'
)
cursor = dw_conn.cursor()

# 1. DIM_ALMACEN
print("\n📦 dim_almacen...")
df = pd.read_csv('data/inputs/inventario/almacenes.csv')
df = df.rename(columns={
    'id_almacen': 'codigo',
    'nombre_almacen': 'nombre',
    'departamento': 'pais',
    'capacidad_m3': 'capacidad',
    'tipo_almacen': 'tipo'
})
df['capacidad'] = df['capacidad'].fillna(0).astype(int)
df['tipo'] = df['tipo'].fillna('Almacén')
df = df[['codigo', 'nombre', 'direccion', 'ciudad', 'pais', 'capacidad', 'tipo', 'activo']]

cursor.execute("TRUNCATE dim_almacen CASCADE")
execute_values(cursor, "INSERT INTO dim_almacen (codigo, nombre, direccion, ciudad, pais, capacidad, tipo, activo) VALUES %s",
               [tuple(row) for row in df.values])
dw_conn.commit()
print(f"   ✅ {len(df)} registros")

# 2. DIM_PROVEEDOR
print("\n🏭 dim_proveedor...")
df = pd.read_csv('data/inputs/inventario/proveedores.csv')
df = df.rename(columns={
    'id_proveedor': 'codigo',
    'nombre_proveedor': 'nombre',
    'contacto_principal': 'contacto',
    'pais_origen': 'pais'
})
df['email'] = df['email'].fillna('info@proveedor.com')
df['telefono'] = df['telefono'].fillna('+503-0000-0000')
df = df[['codigo', 'nombre', 'contacto', 'email', 'telefono', 'direccion', 'ciudad', 'pais', 'activo']]

cursor.execute("TRUNCATE dim_proveedor CASCADE")
execute_values(cursor, "INSERT INTO dim_proveedor (codigo, nombre, contacto, email, telefono, direccion, ciudad, pais, activo) VALUES %s",
               [tuple(row) for row in df.values])
dw_conn.commit()
print(f"   ✅ {len(df)} registros")

# 3. DIM_TIPO_MOVIMIENTO
print("\n📋 dim_tipo_movimiento...")
df = pd.read_csv('data/inputs/inventario/tipos_movimiento.csv')
df = df.rename(columns={
    'id_tipo_movimiento': 'codigo',
    'nombre_tipo': 'nombre',
    'categoria': 'tipo'
})
df['activo'] = True
df = df[['codigo', 'nombre', 'descripcion', 'tipo', 'afecta_stock', 'activo']]

cursor.execute("TRUNCATE dim_tipo_movimiento CASCADE")
execute_values(cursor, "INSERT INTO dim_tipo_movimiento (codigo, nombre, descripcion, tipo, afecta_stock, activo) VALUES %s",
               [tuple(row) for row in df.values])
dw_conn.commit()
print(f"   ✅ {len(df)} registros")

# 4. DIM_CENTRO_COSTO
print("\n🏢 dim_centro_costo...")
df = pd.read_csv('data/inputs/finanzas/centros_costo.csv')
df = df.rename(columns={
    'id_centro_costo': 'codigo',
    'nombre_centro': 'nombre',
    'tipo_centro': 'tipo'
})
df['descripcion'] = 'Centro de costo ' + df['tipo']
df = df[['codigo', 'nombre', 'descripcion', 'tipo', 'responsable', 'activo']]

cursor.execute("TRUNCATE dim_centro_costo CASCADE")
execute_values(cursor, "INSERT INTO dim_centro_costo (codigo, nombre, descripcion, tipo, responsable, activo) VALUES %s",
               [tuple(row) for row in df.values])
dw_conn.commit()
print(f"   ✅ {len(df)} registros")

# 5. DIM_TIPO_TRANSACCION
print("\n💼 dim_tipo_transaccion...")
df = pd.read_csv('data/inputs/finanzas/tipos_transaccion.csv')
df = df.rename(columns={
    'id_tipo_transaccion': 'codigo',
    'nombre_tipo': 'nombre'
})
df['activo'] = True
df['afecta_flujo'] = df['categoria'].isin(['ingreso', 'egreso'])
df = df[['codigo', 'nombre', 'descripcion', 'categoria', 'afecta_flujo', 'activo']]

cursor.execute("TRUNCATE dim_tipo_transaccion CASCADE")
execute_values(cursor, "INSERT INTO dim_tipo_transaccion (codigo, nombre, descripcion, categoria, afecta_flujo, activo) VALUES %s",
               [tuple(row) for row in df.values])
dw_conn.commit()
print(f"   ✅ {len(df)} registros")

# 6. DIM_CLIENTE
print("\n👥 dim_cliente...")
oro_conn = psycopg2.connect(
    host='104.156.246.237', port=5432,
    dbname='orocommerce', user='sa', password='IngDatos123*'
)

query = "SELECT id, name, created_at FROM oro_customer ORDER BY id"
cursor_oro = oro_conn.cursor()
cursor_oro.execute(query)
rows = cursor_oro.fetchall()

data = []
for row in rows:
    cliente_id, nombre, fecha_registro = row
    codigo = f'CLI-{str(cliente_id).zfill(6)}'
    email = nombre.replace(' ', '.').lower() + '@cliente.puntafina.com'
    telefono = f'+503-{2200 + (cliente_id % 7999)}'
    data.append((cliente_id, codigo, nombre, 'B2B', 'Regular', email, telefono, True, fecha_registro))

cursor.execute("TRUNCATE dim_cliente CASCADE")
execute_values(cursor, 
               "INSERT INTO dim_cliente (cliente_externo_id, codigo_cliente, nombre, tipo_cliente, segmento, email, telefono, activo, fecha_registro) VALUES %s",
               data)
dw_conn.commit()
print(f"   ✅ {len(data)} registros")

# 7. DIM_ORDEN
print("\n📋 dim_orden...")
query = "SELECT id, identifier, COALESCE(currency, 'USD'), created_at FROM oro_order ORDER BY id"
cursor_oro.execute(query)
rows = cursor_oro.fetchall()

data = []
for row in rows:
    orden_id, numero, moneda, created = row
    data.append((orden_id, numero, moneda, 'Venta', 'E-Commerce', 1.0, created))

cursor.execute("TRUNCATE dim_orden CASCADE")
execute_values(cursor,
               "INSERT INTO dim_orden (orden_externo_id, numero_orden, moneda, tipo_orden, canal, tasa_cambio, created_at) VALUES %s",
               data)
dw_conn.commit()
print(f"   ✅ {len(data)} registros")

cursor_oro.close()
oro_conn.close()
cursor.close()
dw_conn.close()

print("\n" + "="*80)
print("✅ DIMENSIONES CARGADAS CORRECTAMENTE")
print("="*80)
