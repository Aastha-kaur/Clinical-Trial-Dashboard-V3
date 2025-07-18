# app.py — Main Streamlit Launcher
import streamlit as st
from coordinator import coordinator_view
from admin import admin_view
from utils.auth import authenticate_user, signup_user, log_user_activity

st.set_page_config(page_title="Reimbursement Generator App", layout="centered")

# App Title
st.markdown("<h1 style='text-align: center;'>Reimbursement Generator</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Alzheimer's Research Australia</h3>", unsafe_allow_html=True)

# View Selector
view = st.selectbox("Select View", ["Login", "Sign Up"])

if view == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            log_user_activity(email, "login")
            if user['role'] == "Coordinator":
                coordinator_view(user)
            elif user['role'] == "Admin":
                admin_view(user)
        else:
            st.error("Invalid email or password.")

elif view == "Sign Up":
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Access Type", ["Coordinator", "Admin"])
    if st.button("Register"):
        if signup_user(name, email, password, role):
            st.success("Account created. Please login.")
            log_user_activity(email, "signup")
        else:
            st.error("Email already exists.")
