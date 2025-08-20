import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, datetime
from database import SessionLocal, init_db, User, Task, Journal, Meal

# --- Initialize DB ---
init_db()
db = SessionLocal()

st.set_page_config(page_title="LifeBot AI", layout="wide")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "signup" not in st.session_state:
    st.session_state["signup"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# --- Signup ---
if st.session_state.get("signup"):
    st.subheader("Sign Up")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Create Account"):
        if username and password:
            existing_user = db.query(User).filter_by(username=username).first()
            if existing_user:
                st.error("Username already exists! Please choose another.")
            else:
                new_user = User(username=username, password=password)
                db.add(new_user)
                db.commit()
                st.success("Account created! You can now log in.")
                st.session_state["signup"] = False
        else:
            st.warning("Please enter both username and password.")

# --- Login ---
elif not st.session_state["logged_in"]:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            user = db.query(User).filter_by(username=username, password=password).first()
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.id
                st.session_state["username"] = user.username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

    if st.button("Sign Up Instead"):
        st.session_state["signup"] = True

# --- Main App ---
else:
    st.title("🌟 LifeBot AI")

    menu = st.sidebar.radio("Navigation", ["Tasks", "Journals", "Meal Planner", "Profile", "Logout"])

    # --- Tasks Module ---
    if menu == "Tasks":
        st.header("✅ Tasks")
        task_input = st.text_input("New Task")
        if st.button("Add Task"):
            if task_input:
                new_task = Task(user_id=st.session_state["user_id"], title=task_input)
                db.add(new_task)
                db.commit()
                st.success("Task added!")

        tasks = db.query(Task).filter_by(user_id=st.session_state["user_id"]).all()
        if tasks:
            for t in tasks:
                st.write(f"- {t.title}")

    # --- Journals Module ---
    elif menu == "Journals":
        st.header("📔 Journals")
        journal_entry = st.text_area("Write your journal entry here...")
        if st.button("Save Entry"):
            if journal_entry:
                new_journal = Journal(user_id=st.session_state["user_id"], content=journal_entry, mood="neutral")
                db.add(new_journal)
                db.commit()
                st.success("Journal saved!")

        journals = db.query(Journal).filter_by(user_id=st.session_state["user_id"]).all()
        if journals:
            for j in journals:
                st.markdown(f"**Entry {j.id}**: {j.content}")

    # --- Meal Planner Module ---
    elif menu == "Meal Planner":
        st.header("🍽 Meal Planner")
        meal = st.text_input("Meal")
        if st.button("Add Meal"):
            if meal:
                new_meal = Meal(user_id=st.session_state["user_id"], meal_name=meal)
                db.add(new_meal)
                db.commit()
                st.success("Meal added!")

        meals = db.query(Meal).filter_by(user_id=st.session_state["user_id"]).all()
        if meals:
            for m in meals:
                st.write(f"- {m.meal_name}")

    # --- Profile Module ---
    elif menu == "Profile":
        st.header("👤 Profile")
        st.write(f"User ID: {st.session_state['user_id']}")
        st.write(f"Username: {st.session_state['username']}")

    # --- Logout ---
    elif menu == "Logout":
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.success("You have been logged out.")
