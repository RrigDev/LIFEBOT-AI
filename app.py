import streamlit as st
from database import SessionLocal, User

# --- Signup Function ---
def signup(username, password):
    db = SessionLocal()
    existing_user = db.query(User).filter_by(username=username).first()
    if existing_user:
        return "User already exists"
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    return "Signup successful!"


# --- Login Function ---
def login(username, password):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username, password=password).first()
    return user


# --- Streamlit UI ---
st.title("LifeBot AI - Login/Signup Test")

# State initialization
if "user" not in st.session_state:
    st.session_state["user"] = None

# Tabs for Login and Signup
tab1, tab2 = st.tabs(["Login", "Signup"])

with tab1:
    st.subheader("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = login(login_username, login_password)
        if user:
            st.session_state["user"] = user.id
            st.success(f"Welcome back, {user.username}!")
        else:
            st.error("Invalid credentials")

with tab2:
    st.subheader("Signup")
    signup_username = st.text_input("New Username", key="signup_username")
    signup_password = st.text_input("New Password", type="password", key="signup_password")

    if st.button("Signup"):
        message = signup(signup_username, signup_password)
        if message == "Signup successful!":
            st.success(message)
        else:
            st.warning(message)
