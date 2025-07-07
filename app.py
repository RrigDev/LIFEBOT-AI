import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from datetime import date

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# --- Database Setup ---
conn = sqlite3.connect("lifebot.db", check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    done BOOLEAN,
    due_date TEXT,
    category TEXT,
    completed_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    completed INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')
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
        c.execute("SELECT id FROM users WHERE LOWER(username) = ?", (username,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
        st.session_state.username = username
        st.session_state.logged_in = True
        st.rerun()

# --- Get Current User ID ---
def get_user_id():
    c.execute("SELECT id FROM users WHERE LOWER(username) = ?", (st.session_state.username,))
    result = c.fetchone()
    return result[0] if result else None

# --- Continue only if logged in ---
if st.session_state.get("logged_in"):
    user_id = get_user_id()

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
        today_str = date.today().isoformat()

        c.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND done=1 AND DATE(completed_date)=?", (user_id, today_str))
        done_count_today = c.fetchone()[0]

        c.execute("SELECT * FROM task_history WHERE user_id=? AND date=?", (user_id, today_str))
        if not c.fetchone():
            c.execute("INSERT INTO task_history (user_id, date, completed) VALUES (?, ?, ?)", (user_id, today_str, done_count_today))
            conn.commit()

        history_df = pd.read_sql_query("SELECT date, completed FROM task_history WHERE user_id=?", conn, params=(user_id,))

        st.subheader("📊 Your Task Completion Over Time")
        chart = alt.Chart(history_df).mark_bar(color="#0984e3").encode(
            x="date:T",
            y=alt.Y("completed:Q", title="Tasks Completed")
        ).properties(width=700, height=300)
        st.altair_chart(chart, use_container_width=True)

    elif st.session_state.page == "Daily Companion":
        st.header("🧠 Daily Companion")
        tabs = st.tabs(["📋 Tasks", "📓 Journal", "💬 Companion"])

        with tabs[0]:
            with st.form("add_task_form", clear_on_submit=True):
                new_task = st.text_input("📝 Task")
                due_date = st.date_input("📅 Due Date")
                category = st.radio("🏷️ Category", ["Study", "Work", "Personal", "Health", "Other"], horizontal=True)
                submitted = st.form_submit_button("➕ Add Task")

                if submitted and new_task.strip():
                    c.execute('''INSERT INTO tasks (user_id, task, done, due_date, category, completed_date)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (user_id, new_task.strip(), False, due_date.isoformat(), category, None))
                    conn.commit()
                    st.rerun()

            task_df = pd.read_sql_query("SELECT * FROM tasks WHERE user_id=?", conn, params=(user_id,))
            total = len(task_df)
            done_count = task_df["done"].sum()
            if total > 0:
                st.progress(done_count / total)
                st.markdown(f"✅ **{done_count} of {total} tasks completed**")
            else:
                st.info("No tasks added yet!")

            for _, row in task_df.sort_values(by=["done", "due_date"]).iterrows():
                col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
                with col1:
                    done = st.checkbox(f"{row['task']} [{row['category']}] (Due: {row['due_date']})", 
                                       value=row["done"], key=f"done_{row['id']}")
                with col3:
                    delete = st.button("🗑️", key=f"del_{row['id']}")

                if done != row["done"]:
                    completed_date = date.today().isoformat() if done else None
                    c.execute("UPDATE tasks SET done=?, completed_date=? WHERE id=?", (done, completed_date, row['id']))
                    conn.commit()
                    st.rerun()

                if delete:
                    c.execute("DELETE FROM tasks WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()

        with tabs[1]:
            st.text_area("Write your thoughts here:")

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
        st.header("🍽️ Nutrition & Meal Planner")
        st.write("Here you'll find personalized meals and healthy tips. Coming soon!")
else:
    st.title("Welcome to LifeBot AI")
    st.info("Please enter your name in the sidebar to get started.")
