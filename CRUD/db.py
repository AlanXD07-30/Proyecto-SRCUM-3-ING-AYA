import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "crud"),  # 👈 nombre actualizado
        user=os.getenv("DB_USER", "postgres"),
        password=2426022023,
        row_factory=dict_row,
    )
