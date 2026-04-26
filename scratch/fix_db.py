import duckdb

db_path = r"C:\Users\MARCO\Desktop\PC3 ORIA\local_forecaster.duckdb"
conn = duckdb.connect(db_path)

print("Before:")
print(conn.execute("SELECT id, name FROM projects").fetchdf())

# Delete 'HOLA'
try:
    conn.execute("DELETE FROM projects WHERE name = 'HOLA'")
    print("Deleted 'HOLA'")
except Exception as e:
    print("Error deleting HOLA:", e)

# Rename 'nuevo' to 'Demanda San Fernando'
try:
    conn.execute("UPDATE projects SET name = 'Demanda San Fernando' WHERE name = 'nuevo'")
    print("Renamed 'nuevo'")
except Exception as e:
    print("Error renaming nuevo:", e)

print("After:")
print(conn.execute("SELECT id, name FROM projects").fetchdf())

conn.close()
