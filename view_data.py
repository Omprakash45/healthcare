import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("healthcare.db")  # Ensure this file is in the same directory
cursor = conn.cursor()

# Fetch data
df = pd.read_sql_query("SELECT id, name, email, age FROM users", conn)  # Exclude password for security
conn.close()

# Display data
print("\n📢 Registered Users:\n")
print(df)

# Save to CSV (optional)
df.to_csv("registered_users.csv", index=False)
print("\n✅ Data saved to 'registered_users.csv'")
