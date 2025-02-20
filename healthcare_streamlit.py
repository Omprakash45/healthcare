import streamlit as st
import sqlite3
import pandas as pd
import shutil

# Database connection
def create_connection():
    return sqlite3.connect("healthcare.db")

# Create users table if not exists
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Insert user into database
def insert_user(name, email, age):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age))
    conn.commit()
    conn.close()

# Fetch all users
def fetch_users():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

# UI Setup
st.title("Healthcare User Registration")

menu = st.sidebar.selectbox("Menu", ["Register", "View Users", "Download Database"])

if menu == "Register":
    st.subheader("Register User")
    
    name = st.text_input("Name")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=1, step=1)
    
    if st.button("Register"):
        if name and email and age:
            try:
                insert_user(name, email, age)
                st.success("User registered successfully!")
            except sqlite3.IntegrityError:
                st.error("Email already exists!")
        else:
            st.error("Please fill all fields.")

elif menu == "View Users":
    st.subheader("Registered Users")
    df = fetch_users()
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No users found.")

elif menu == "Download Database":
    st.subheader("Download SQLite Database")
    
    if st.button("Download Database"):
        shutil.copy("healthcare.db", "healthcare_download.db")
        with open("healthcare_download.db", "rb") as file:
            st.download_button("Click here to download", file, file_name="healthcare.db")
