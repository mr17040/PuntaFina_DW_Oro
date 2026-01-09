#!/usr/bin/env python3
"""
Script para crear registros por defecto en dimensiones que faltan
"""
import psycopg2

conn = psycopg2.connect(
    host="104.156.246.237",
    port=5432,
    dbname="datawarehouse_bi",
    user="sa",
    password="IngDatos123*",
)
conn.autocommit = True
cur = conn.cursor()

# Crear registro por defecto en dim_cliente
cur.execute(
    """
    INSERT INTO dim_cliente (cliente_id, nombre, email) 
    VALUES (1, 'Cliente Por Defecto', 'default@puntafina.com')
    ON CONFLICT (cliente_id) DO NOTHING
"""
)
print("✓ dim_cliente: registro por defecto creado")

# Crear registro por defecto en dim_producto
cur.execute(
    """
    INSERT INTO dim_producto (producto_id, nombre, sku)
    VALUES (1, 'Producto Por Defecto', 'DEFAULT-SKU')
    ON CONFLICT (producto_id) DO NOTHING
"""
)
print("✓ dim_producto: registro por defecto creado")

# Crear registro por defecto en dim_orden
cur.execute(
    """
    INSERT INTO dim_orden (id_orden, numero_orden, cliente_nombre)
    VALUES ('1', 'ORDER-DEFAULT', 'Cliente Por Defecto')
    ON CONFLICT (id_orden) DO NOTHING
"""
)
print("✓ dim_orden: registro por defecto creado")

# Crear registro por defecto en dim_usuario
cur.execute(
    """
    INSERT INTO dim_usuario (usuario_id, username, email)
    VALUES (1, 'default_user', 'user@puntafina.com')
    ON CONFLICT (usuario_id) DO NOTHING
"""
)
print("✓ dim_usuario: registro por defecto creado")

# Crear registro por defecto en dim_almacen
cur.execute(
    """
    INSERT INTO dim_almacen (id_almacen, nombre, codigo)
    VALUES ('1', 'Almacén Central', 'ALM_CENTRAL')
    ON CONFLICT (id_almacen) DO NOTHING
"""
)
print("✓ dim_almacen: registro por defecto creado")

cur.close()
conn.close()

print("\n✅ Registros por defecto creados exitosamente")
