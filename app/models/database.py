import sqlite3
import os
from flask import current_app, g
from pathlib import Path

def get_db():
    """Obtener conexión a la base de datos"""
    if 'db' not in g:
        # Asegurar que el directorio data existe
        data_dir = Path(current_app.root_path).parent / 'data'
        data_dir.mkdir(exist_ok=True)
        
        db_path = os.path.join(data_dir, 'database.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    """Cerrar conexión a la base de datos"""
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """Inicializar la base de datos con datos de prueba"""
    print("Inicializando base de datos...")
    db = get_db()
    
    # Crear tablas si no existen
    db.execute('''
        CREATE TABLE IF NOT EXISTS compradores (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            total_compras REAL NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS deudores (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            monto_adeudado REAL NOT NULL
        )
    ''')
    
    # Insertar datos de prueba solo si las tablas están vacías
    if db.execute('SELECT COUNT(*) FROM compradores').fetchone()[0] == 0:
        print("Insertando datos de prueba en tabla compradores...")
        compradores = [
            (1, 'Juan Pérez', 5000.50),
            (2, 'María López', 7500.75),
            (3, 'Carlos Gómez', 2300.25),
            (4, 'Ana Martínez', 9800.00),
            (5, 'Pedro Sánchez', 3200.60)
        ]
        db.executemany('INSERT INTO compradores VALUES (?, ?, ?)', compradores)
    
    if db.execute('SELECT COUNT(*) FROM deudores').fetchone()[0] == 0:
        print("Insertando datos de prueba en tabla deudores...")
        deudores = [
            (1, 'Roberto Díaz', 1500.00),
            (2, 'Sofía Ramírez', 3000.50),
            (3, 'Miguel Torres', 500.25),
            (4, 'Laura Jiménez', 4200.75),
            (5, 'Alejandro Ruiz', 2100.30)
        ]
        db.executemany('INSERT INTO deudores VALUES (?, ?, ?)', deudores)
    
    db.commit()
    print("Base de datos inicializada")

def consultar_mejores_compradores(limite=3):
    """Consultar los mejores compradores ordenados por total de compras"""
    try:
        db = get_db()
        compradores = db.execute(
            'SELECT id, nombre, total_compras FROM compradores ORDER BY total_compras DESC LIMIT ?',
            (limite,)
        ).fetchall()
        
        return [dict(c) for c in compradores]
    except Exception as e:
        current_app.logger.error(f"Error al consultar mejores compradores: {str(e)}")
        raise

def consultar_deudores_altos(limite=3):
    """Consultar los deudores con mayor monto adeudado"""
    try:
        db = get_db()
        deudores = db.execute(
            'SELECT id, nombre, monto_adeudado FROM deudores ORDER BY monto_adeudado DESC LIMIT ?',
            (limite,)
        ).fetchall()
        
        return [dict(d) for d in deudores]
    except Exception as e:
        current_app.logger.error(f"Error al consultar deudores altos: {str(e)}")
        raise

def contar_compradores():
    """Contar el número total de compradores"""
    try:
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM compradores').fetchone()[0]
        return count
    except Exception as e:
        current_app.logger.error(f"Error al contar compradores: {str(e)}")
        raise

def contar_deudores():
    """Contar el número total de deudores"""
    try:
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM deudores').fetchone()[0]
        return count
    except Exception as e:
        current_app.logger.error(f"Error al contar deudores: {str(e)}")
        raise