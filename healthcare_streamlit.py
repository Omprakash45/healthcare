import streamlit as st
import sqlite3
import pandas as pd
import json

# SQLite Database Connection
def connect_db():
    conn = sqlite3.connect("healthcare.db")
    return conn

# Create users table if not exists
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT, age INTEGER, location TEXT,
                      mobile TEXT, password TEXT)''')
    conn.commit()
    conn.close()

# Insert user into database
def insert_user(name, age, location, mobile, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, age, location, mobile, password) VALUES (?, ?, ?, ?, ?)", 
                   (name, age, location, mobile, password))
    conn.commit()
    conn.close()

# Fetch all users
def fetch_users():
    conn = connect_db()
    df = pd.read_sql_query("SELECT id, name, age, location, mobile FROM users", conn)
    conn.close()
    return df

# Load user data
USER_DATA_FILE = "user_data.json"

def load_users():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)

# Initialize database
create_table()
users = load_users()

# Streamlit UI
st.title("Healthcare Platform")

menu = st.sidebar.radio("Navigation", ["Register", "Login", "Get Treatment", "Edit Profile", "Change Password", "View Users"])

if menu == "Register":
    st.subheader("Register")
    name = st.text_input("Enter your name:")
    age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
    location = st.text_input("Enter your location:")
    mobile_number = st.text_input("Enter your mobile number:", max_chars=10)
    password = st.text_input("Enter your password:", type="password")
    confirm_password = st.text_input("Confirm your password:", type="password")
    
    if st.button("Register"):
        if password == confirm_password:
            insert_user(name, age, location, mobile_number, password)
            st.success(f"{name}, you have successfully registered!")
        else:
            st.error("Passwords do not match.")

elif menu == "Login":
    st.subheader("Login")
    name = st.text_input("Enter your name:")
    password = st.text_input("Enter your password:", type="password")
    
    if st.button("Login"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user"] = name
            st.success(f"Welcome {name}, you are logged in!")
        else:
            st.error("Invalid credentials.")

elif menu == "Get Treatment":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("Get Treatment")
        
        diseases = {
            "Diabetes": "Metformin, Insulin, Sulfonylureas.",
            "Hypertension": "ACE inhibitors, Beta-blockers, Diuretics.",
            "Asthma": "Inhaled corticosteroids, Beta-agonists.",
            "Arthritis": "NSAIDs, Corticosteroids, DMARDs.",
        }
        
        disease = st.selectbox("Select your disease:", list(diseases.keys()))
        
        if st.button("Get Treatment"):
            st.success(f"{st.session_state['user']}, your treatment is: {diseases[disease]}")
    else:
        st.warning("Please login first.")

elif menu == "Edit Profile":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("Edit Profile")
        name = st.session_state["user"]
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT age, location FROM users WHERE name = ?", (name,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            new_age = st.number_input("Update your age:", min_value=1, max_value=120, step=1, value=user_data[0])
            new_location = st.text_input("Update your location:", value=user_data[1])
            
            if st.button("Update Profile"):
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET age = ?, location = ? WHERE name = ?", 
                               (new_age, new_location, name))
                conn.commit()
                conn.close()
                st.success("Profile updated successfully!")
    else:
        st.warning("Please login first.")

elif menu == "Change Password":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("Change Password")
        name = st.session_state["user"]
        
        old_password = st.text_input("Enter your old password:", type="password")
        new_password = st.text_input("Enter new password:", type="password")
        confirm_password = st.text_input("Confirm new password:", type="password")
        
        if st.button("Change Password"):
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE name = ?", (name,))
            stored_password = cursor.fetchone()[0]
            
            if stored_password == old_password:
                if new_password == confirm_password:
                    cursor.execute("UPDATE users SET password = ? WHERE name = ?", (new_password, name))
                    conn.commit()
                    conn.close()
                    st.success("Password changed successfully!")
                else:
                    st.error("New passwords do not match.")
            else:
                st.error("Incorrect old password.")
            conn.close()
    else:
        st.warning("Please login first.")

elif menu == "View Users":
    st.subheader("Registered Users")
    df = fetch_users()
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No users found.")
