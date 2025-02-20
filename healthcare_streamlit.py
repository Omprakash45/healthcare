import streamlit as st
import pymysql
import pandas as pd

# MySQL Database Connection
def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",  # Update if using another user
        password="548017",
        database="healthcare_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# Insert User into MySQL
def insert_user(name, age, location, mobile, password):
    conn = connect_db()
    cursor = conn.cursor()
    sql = "INSERT INTO users (name, age, location, mobile, password) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (name, age, location, mobile, password))
    conn.commit()
    conn.close()

# Fetch Users from MySQL
def fetch_user(name):
    conn = connect_db()
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    user = cursor.fetchone()
    conn.close()
    return user

# Update Profile
def update_profile(name, age, location):
    conn = connect_db()
    cursor = conn.cursor()
    sql = "UPDATE users SET age = %s, location = %s WHERE name = %s"
    cursor.execute(sql, (age, location, name))
    conn.commit()
    conn.close()

# Change Password
def change_password(name, new_password):
    conn = connect_db()
    cursor = conn.cursor()
    sql = "UPDATE users SET password = %s WHERE name = %s"
    cursor.execute(sql, (new_password, name))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("🏥 Healthcare Platform")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["Register", "Login", "Get Treatment", "Edit Profile", "Change Password"])

# Registration Page
if menu == "Register":
    st.subheader("📝 Register")
    name = st.text_input("Enter your name:")
    age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
    location = st.text_input("Enter your location:")
    mobile = st.text_input("Enter your mobile number:", max_chars=10)
    password = st.text_input("Enter your password:", type="password")
    confirm_password = st.text_input("Confirm your password:", type="password")

    if st.button("Register"):
        if password == confirm_password:
            insert_user(name, age, location, mobile, password)
            st.success(f"✅ {name}, you have successfully registered!")
        else:
            st.error("❌ Passwords do not match.")

# Login Page
elif menu == "Login":
    st.subheader("🔐 Login")
    name = st.text_input("Enter your name:")
    password = st.text_input("Enter your password:", type="password")

    if st.button("Login"):
        user = fetch_user(name)
        if user and user["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = name
            st.success(f"🎉 Welcome {name}, you are logged in!")
        else:
            st.error("❌ Invalid credentials.")

# Get Treatment Page
elif menu == "Get Treatment":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("💊 Get Treatment")

        diseases = {
            "Diabetes": "Metformin, Insulin, Sulfonylureas.",
            "Hypertension": "ACE inhibitors, Beta-blockers, Diuretics.",
            "Asthma": "Inhaled corticosteroids, Beta-agonists.",
            "Arthritis": "NSAIDs, Corticosteroids, DMARDs.",
        }

        disease = st.selectbox("Select your disease:", list(diseases.keys()))

        if st.button("Get Treatment"):
            st.success(f"💡 {st.session_state['user']}, your treatment is: {diseases[disease]}")
    else:
        st.warning("⚠️ Please login first.")

# Edit Profile Page
elif menu == "Edit Profile":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("✏️ Edit Profile")
        name = st.session_state["user"]
        user = fetch_user(name)

        if user:
            new_age = st.number_input("Update your age:", min_value=1, max_value=120, step=1, value=user["age"])
            new_location = st.text_input("Update your location:", value=user["location"])

            if st.button("Update Profile"):
                update_profile(name, new_age, new_location)
                st.success("✅ Profile updated successfully!")
        else:
            st.error("❌ User not found.")
    else:
        st.warning("⚠️ Please login first.")

# Change Password Page
elif menu == "Change Password":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("🔑 Change Password")
        name = st.session_state["user"]
        old_password = st.text_input("Enter your old password:", type="password")
        new_password = st.text_input("Enter new password:", type="password")
        confirm_password = st.text_input("Confirm new password:", type="password")

        if st.button("Change Password"):
            user = fetch_user(name)
            if user and user["password"] == old_password:
                if new_password == confirm_password:
                    change_password(name, new_password)
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ New passwords do not match.")
            else:
                st.error("❌ Incorrect old password.")
    else:
        st.warning("⚠️ Please login first.")
