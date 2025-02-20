import streamlit as st
import sqlite3
import pandas as pd
import shutil

# Secure Password for Database Download (Change this)
ADMIN_PASSWORD = "548017"

# Database connection
def create_connection():
    return sqlite3.connect("healthcare.db", check_same_thread=False)

# Create users table if not exists
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Ensure table is created at startup
create_table()

# Insert user into database
def insert_user(name, email, password, age):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password, age) VALUES (?, ?, ?, ?)", (name, email, password, age))
        conn.commit()
        st.success("User registered successfully!")
    except sqlite3.IntegrityError:
        st.error("Email already exists!")
    except sqlite3.OperationalError as e:
        st.error(f"Database Error: {e}")
    finally:
        conn.close()

# Fetch all users
def fetch_users():
    conn = create_connection()
    df = pd.read_sql_query("SELECT id, name, email, age FROM users", conn)  # Exclude password for security
    conn.close()
    return df

# User authentication
def authenticate_user(email, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

# UI Setup
st.title("Healthcare Management System")

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "View Users", "Download Database"])

# Register
if menu == "Register":
    st.subheader("Register User")
    
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    age = st.number_input("Age", min_value=1, step=1)
    
    if st.button("Register"):
        if name and email and password and age:
            insert_user(name, email, password, age)
        else:
            st.error("Please fill all fields.")

# Login
elif menu == "Login":
    st.subheader("User Login")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.success(f"Welcome {user[1]}!")
        else:
            st.error("Invalid credentials!")

# View Registered Users
elif menu == "View Users":
    st.subheader("Registered Users")
    df = fetch_users()
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No users found.")

# Download Database (Password Protected)
elif menu == "Download Database":
    st.subheader("Download SQLite Database (Admin Only)")
    
    admin_password = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Download Database"):
        if admin_password == ADMIN_PASSWORD:
            shutil.copy("healthcare.db", "healthcare_download.db")
            with open("healthcare_download.db", "rb") as file:
                st.download_button("Click here to download", file, file_name="healthcare.db")
        else:
            st.error("❌ Incorrect password! Access denied.")
