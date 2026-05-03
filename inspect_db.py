import sqlite3

DB_PATH = "db.sqlite3"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\n📦 DATABASE TABLES:\n")

for table in tables:
    table_name = table[0]
    print(f"\n================ {table_name} ================\n")

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]

    print("Columns:", col_names)

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

conn.close()