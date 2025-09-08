import boto3
import psycopg2

# AWS RDS info
host = "byod-stage.crwagmalobuu.us-east-2.rds.amazonaws.com"
port = 5432
user = "mabel_user"
dbname = "mabel_stage"
region = "us-east-2"

# Create boto3 RDS client
session = boto3.session.Session(region_name=region)
client = session.client("rds")

# Generate IAM auth token
token = client.generate_db_auth_token(
    DBHostname=host,
    Port=port,
    DBUsername=user
)

print("🔑 Generated IAM Auth Token (use as password):", token[:80] + "...")  # truncated for safety

# Connection params
DB_KW = dict(
    dbname=dbname,
    user=user,
    password=token,   # token goes here
    host=host,
    port=port,
    sslmode="require"  # IAM auth requires SSL
)

try:
    conn = psycopg2.connect(**DB_KW)
    cur = conn.cursor()

    cur.execute("SELECT version();")
    print("✅ Connection successful!")
    print("PostgreSQL version:", cur.fetchone()[0])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed!")
    print("Error:", e)
