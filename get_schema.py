import psycopg2
import pandas as pd

# Database connection parameters
db_user = "postgres"
db_password = "postgres"
db_name = "checklistdb"
db_host = "localhost"
db_port = 5432


def get_table_schemas():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()

        # Query to get all user-defined tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        schema_dict = {}

        for table in tables:
            table_name = table[0]
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            columns = cursor.fetchall()

            schema_dict[table_name] = columns

        cursor.close()
        conn.close()
        return schema_dict

    except Exception as e:
        print("Error:", e)
        return {}


if __name__ == "__main__":
    schemas = get_table_schemas()
    for table, cols in schemas.items():
        print(f"\nTable: {table}")
        df = pd.DataFrame(cols, columns=["Column", "Type", "Nullable", "Default"])
        print(df.to_string(index=False))
