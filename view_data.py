import sqlite3
import pandas as pd

conn = sqlite3.connect("healthcare.db")
df = pd.read_sql_query("SELECT * FROM users", conn)
conn.close()

print(df)
