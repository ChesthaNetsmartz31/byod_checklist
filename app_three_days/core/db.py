import psycopg2
from psycopg2.extras import RealDictCursor

DB_KW = dict(
    dbname="checklistdb",
    user="postgres",
    password="123456",
    host="localhost",
    port=5432,
)

def get_connection():
    return psycopg2.connect(**DB_KW, cursor_factory=RealDictCursor)
