import streamlit as st
import pandas as pd
import os
import altair as alt
import sqlite3
from datetime import date

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# --- Database Setup ---
conn = sqlite3.connect("lifebot.db", check_same_thread=False)
c = conn.cursor()

# --- Create tables if not exists ---
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    username TEXT,
    task TEXT,
    done INTEGER,
    due_date TEXT,
    category TEXT,
    completed_date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    username TEXT,
    date TEXT,
    completed INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS journal (
    username TEXT,
    entry TEXT,
    mood TEXT,
    created_at TEXT
)
""")

conn.commit()

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Login via Name Input ---
st.sidebar.title("👤 Welcome")
name_input = st.sidebar.text_input("Enter your name")
if st.sidebar.button(f"Hello, {name_input.title()}!"):
    if name_input:
        username = name_input.strip().lower()
        st.session_state.username = username
        st.session_state.logged_in = True
        # Add to database if new
        c.execute("SELECT username FROM users WHERE LOWER(username) = ?", (username,))
        if not c.fetchone():
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
        st.rerun()

# --- Continue only if logged in ---
if st.session_state.get("logged_in"):
    # Sidebar Navigation
    st.sidebar.title("🧭 LifeBot AI Menu")
    user_type = st.sidebar.radio("Who are you?", ["Student", "Adult", "Senior Citizen"], horizontal=True)

    pages = ["Home", "Profile", "Daily Companion"]
    if user_type == "Student":
        pages.append("Career Pathfinder")
    elif user_type in ["Adult", "Senior Citizen"]:
        pages.append("Managing Finances")
    pages.extend(["Skill-Up AI", "Meal Planner"])

    selected_page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))
    st.session_state.page = selected_page

    # --- Main Page Rendering ---
    if st.session_state.page == "Home":
        st.title("🤖 LifeBot AI")
        st.write("Welcome! I'm your all-in-one AI assistant.")
        st.markdown("---")
        st.subheader("Choose a tool from the left menu to begin.")

    elif st.session_state.page == "Profile":
        st.header("👤 Your Profile")
        today_str = date.today().strftime("%Y-%m-%d")

        c.execute("SELECT COUNT(*) FROM tasks WHERE username = ? AND done = 1 AND completed_date = ?",
                  (st.session_state.username, today_str))
        done_count_today = c.fetchone()[0]

        c.execute("SELECT * FROM history WHERE username = ? AND date = ?", (st.session_state.username, today_str))
        if not c.fetchone():
            c.execute("INSERT INTO history (username, date, completed) VALUES (?, ?, ?)",
                      (st.session_state.username, today_str, done_count_today))
            conn.commit()

        c.execute("SELECT date, completed FROM history WHERE username = ?", (st.session_state.username,))
        history = pd.DataFrame(c.fetchall(), columns=["Date", "Completed"])

        st.subheader("📊 Your Task Completion Over Time")
        chart = alt.Chart(history).mark_bar(color="#0984e3").encode(
            x="Date:T",
            y=alt.Y("Completed:Q", title="Tasks Completed")
        ).properties(width=700, height=300)
        st.altair_chart(chart, use_container_width=True)

    elif st.session_state.page == "Daily Companion":
        st.header("🧠 Daily Companion")
        tabs = st.tabs(["📋 Tasks", "📓 Journal", "💬 Companion"])

        with tabs[0]:
            c.execute("SELECT rowid, * FROM tasks WHERE username = ? ORDER BY done, due_date",
                      (st.session_state.username,))
            tasks = pd.DataFrame(c.fetchall(), columns=["rowid", "Username", "Task", "Done", "Due Date", "Category", "Completed Date"])

            with st.form("add_task_form", clear_on_submit=True):
                new_task = st.text_input("📝 Task")
                due_date = st.date_input("📅 Due Date")
                category = st.radio("🏷️ Category", ["Study", "Work", "Personal", "Health", "Other"], horizontal=True)
                submitted = st.form_submit_button("➕ Add Task")

                if submitted and new_task.strip():
                    c.execute("""
                        INSERT INTO tasks (username, task, done, due_date, category, completed_date)
                        VALUES (?, ?, 0, ?, ?, NULL)
                    """, (st.session_state.username, new_task.strip(), str(due_date), category))
                    conn.commit()
                    st.rerun()

            total = len(tasks)
            done_count = tasks["Done"].sum()
            if total > 0:
                st.progress(done_count / total)
                st.markdown(f"✅ **{done_count} of {total} tasks completed**")
            else:
                st.info("No tasks added yet!")

            for i, row in tasks.iterrows():
                col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                with col1:
                    done = st.checkbox(
                        f"{row['Task']} [{row['Category']}] (Due: {row['Due Date']})",
                        value=bool(row["Done"]),
                        key=f"done_{row['rowid']}"
                    )
                with col3:
                    delete = st.button("🗑️", key=f"del_{row['rowid']}")

                if done != bool(row["Done"]):
                    completed_date = date.today().strftime("%Y-%m-%d") if done else None
                    c.execute("UPDATE tasks SET done = ?, completed_date = ? WHERE rowid = ?",
                              (int(done), completed_date, row["rowid"]))
                    conn.commit()
                    st.rerun()

                if delete:
                    c.execute("DELETE FROM tasks WHERE rowid = ?", (row["rowid"],))
                    conn.commit()
                    st.rerun()

        with tabs[1]:
            st.subheader("📝 Journal Your Thoughts")
            mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry", "😴 Tired"])
            entry = st.text_area("Write here")
            if st.button("💾 Save Entry"):
                if entry.strip():
                    c.execute("INSERT INTO journal (username, entry, mood, created_at) VALUES (?, ?, ?, ?)",
                              (st.session_state.username, entry.strip(), mood, date.today().strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success("Entry saved!")

            st.markdown("---")
            st.subheader("📚 Past Entries")
            c.execute("SELECT entry, mood, created_at FROM journal WHERE username = ? ORDER BY created_at DESC",
                      (st.session_state.username,))
            journal_entries = c.fetchall()
            for e in journal_entries:
                st.markdown(f"**{e[2]}** — *{e[1]}*\n> {e[0]}")

        with tabs[2]:
            st.write("Coming soon: Chat with your AI companion!")

    elif st.session_state.page == "Career Pathfinder":
        st.header("💼 Career Pathfinder")
        st.write("Explore careers based on your skills and interests. Coming soon!")

    elif st.session_state.page == "Managing Finances":
        st.header("💰 Managing Finances")
        st.write("Financial planning tools and tips. Coming soon!")

    elif st.session_state.page == "Skill-Up AI":
        st.header("📚 Skill-Up AI")
        st.write("Learn anything, your way! Coming soon!")

    elif st.session_state.page == "Meal Planner":
        st.title("🍽️ Meal Planner")
        tabs = st.tabs(["🍲 Log Meal", "🧾 Suggestions", "💧 Water Tracker", "📈 Overview"])

        with tabs[0]:  # Log Meal
            st.subheader("Log Your Meals")
            today = datetime.now().strftime("%Y-%m-%d")
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            meal_name = st.text_input("Meal Name")
            mood = st.radio("Mood After Meal", ["🙂 Happy", "😐 Neutral", "🙁 Low"], horizontal=True)

            if st.button("Save Meal"):
                if meal_name:
                    cursor.execute("""
                        INSERT INTO meals (username, date, meal_type, meal_name, mood)
                        VALUES (?, ?, ?, ?, ?)
                    """, (st.session_state.username, today, meal_type, meal_name, mood))
                    conn.commit()
                    st.success("Meal logged!")
                else:
                    st.warning("Please enter the meal name.")

        with tabs[1]:  # Suggestions
            st.subheader("Healthy Meal Suggestions")
            now = datetime.now().hour
            suggestions = {
                "Breakfast": ["Oats with fruits", "Boiled eggs & toast", "Smoothie bowl"],
                "Lunch": ["Grilled chicken salad", "Vegetable dal & rice", "Paneer wrap"],
                "Dinner": ["Soup & whole grain bread", "Quinoa & vegetables", "Tofu stir fry"],
                "Snack": ["Fruit salad", "Greek yogurt", "Roasted nuts"]
            }
            current = "Breakfast" if now < 11 else "Lunch" if now < 17 else "Dinner"
            for meal in suggestions.get(current, []):
                st.markdown(f"✅ {meal}")

        with tabs[2]:  # Water Tracker
            st.subheader("Track Your Water Intake")
            st.write("Feature coming soon!")

        with tabs[3]:  # Overview
            st.subheader("Weekly Meal Overview")
            df = pd.read_sql_query("SELECT date, COUNT(*) as meals FROM meals WHERE username=? GROUP BY date", conn, params=(st.session_state.username,))
            if not df.empty:
                chart = alt.Chart(df).mark_bar(color="#00cec9").encode(
                    x="date:T",
                    y=alt.Y("meals:Q", title="Meals Logged")
                ).properties(width=700, height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No meals logged yet.")

else:
    st.title("Welcome to LifeBot AI")
    st.info("Please enter your name in the sidebar to get started.")
