# -*- coding: utf-8 -*-
"""
Script seguro para reajustar la secuencia de `USUARIO.id_usuario`.
Ejecutar desde la carpeta `CRUD` con: python reset_sequences.py
El script usa la conexión definida en `app.get_db_connection()`.
"""

from app import get_db_connection


def reset_usuario_sequence(table_name='USUARIO', column_name='id_usuario'):
    """Ajusta la secuencia asociada a `table_name.column_name` al valor MAX(column)+1.

    Maneja columnas definidas como SERIAL o como IDENTITY. No modifica filas, solo la secuencia.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Normalizar nombres (Postgres guarda nombres sin comillas en minúsculas)
    tbl = table_name.lower()
    col = column_name

    # 1) Intentar pg_get_serial_sequence (funciona para SERIAL y a veces para identity)
    cur.execute("SELECT pg_get_serial_sequence(%s, %s)", (tbl, col))
    seq_row = cur.fetchone()
    seq_name = seq_row[0] if seq_row and seq_row[0] else None

    # 2) Si no se encontró, buscar la secuencia mediante dependencias (identity -> sequence)
    if not seq_name:
        cur.execute("""
            SELECT quote_ident(ns.nspname)||'.'||quote_ident(seq.relname) AS seq_name
            FROM pg_class seq
            JOIN pg_namespace ns ON ns.oid = seq.relnamespace
            JOIN pg_depend d ON d.objid = seq.oid
            JOIN pg_class tab ON d.refobjid = tab.oid
            JOIN pg_attribute attr ON attr.attrelid = tab.oid AND attr.attnum = d.refobjsubid
            WHERE seq.relkind = 'S' AND tab.relname = %s AND attr.attname = %s
            LIMIT 1
        """, (tbl, col))
        row = cur.fetchone()
        seq_name = row[0] if row else None

    # Calcular siguiente valor (MAX(id) + 1)
    cur.execute(f"SELECT COALESCE(MAX({col}), 0) FROM {tbl}")
    max_id = cur.fetchone()[0]
    next_val = (max_id or 0) + 1

    if not seq_name:
        print(f"No se encontró secuencia para {table_name}.{column_name}. No se realizó ningún cambio.")
    else:
        # Ajustar la secuencia a next_val de forma que el próximo nextval devuelva next_val
        cur.execute("SELECT setval(%s, %s, false)", (seq_name, next_val))
        conn.commit()
        print(f"Secuencia {seq_name} ajustada a {next_val} (el próximo INSERT usará {next_val}).")

    cur.close()
    conn.close()


if __name__ == '__main__':
    reset_usuario_sequence()
