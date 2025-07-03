import streamlit as st
import pandas as pd
import os
import altair as alt

# --- Authentication Setup ---
USERS_FILE = "users.csv"
os.makedirs("user_tasks", exist_ok=True)
os.makedirs("user_history", exist_ok=True)
os.makedirs("user_journals", exist_ok=True)

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Login to LifeBot AI")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        users = pd.read_csv(USERS_FILE)
        match = users[(users["username"] == username) & (users["password"] == password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# --- Session State Initialization ---
if 'expanders_state' not in st.session_state:
    st.session_state.expanders_state = {
        'Daily Companion': True,
        'Meal Planner': True,
        'Career Pathfinder': True,
        'Managing Finances': True,
        'Skill-Up AI': True
    }

if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Sidebar Navigation ---
st.sidebar.title("🧭 LifeBot AI Menu")
user_type = st.sidebar.radio("Who are you?", ["Student", "Adult", "Senior Citizen"], horizontal=True)

pages = ["Home", "Profile", "Daily Companion"]
if user_type == "Student":
    pages.append("Career Pathfinder")
elif user_type in ["Adult", "Senior Citizen"]:
    pages.append("Managing Finances")
pages.extend(["Skill-Up AI", "Meal Planner"])

previous_page = st.session_state.get('current_page', 'Home')
st.session_state.current_page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))
current_page = st.session_state.current_page

if previous_page != current_page:
    st.session_state.page = current_page

# --- Main Content Area ---
def render_daily_companion():
    st.header("🧠 Daily Companion")
    tabs = st.tabs(["📋 Tasks", "📓 Journal", "💬 Companion"])

    with tabs[0]:
        TASK_FILE = f"user_tasks/{st.session_state.username}_tasks.csv"
        if os.path.exists(TASK_FILE):
            tasks = pd.read_csv(TASK_FILE)
        else:
            tasks = pd.DataFrame(columns=["Task", "Done", "Due Date", "Category", "Completed Date"])

        with st.form("add_task_form", clear_on_submit=True):
            new_task = st.text_input("📝 Task")
            due_date = st.date_input("📅 Due Date")
            category = st.radio("🏷️ Category", ["Study", "Work", "Personal", "Health", "Other"], horizontal=True)
            submitted = st.form_submit_button("➕ Add Task")

            if submitted and new_task.strip():
                new_row = pd.DataFrame([{
                    "Task": new_task.strip(),
                    "Done": False,
                    "Due Date": due_date,
                    "Category": category,
                    "Completed Date": pd.NaT
                }])
                tasks = pd.concat([tasks, new_row], ignore_index=True)
                tasks.to_csv(TASK_FILE, index=False)
                st.rerun()

        total = len(tasks)
        done_count = tasks["Done"].sum()
        if total > 0:
            st.progress(done_count / total)
            st.markdown(f"✅ **{done_count} of {total} tasks completed**")
        else:
            st.info("No tasks added yet!")

        tasks_sorted = tasks.sort_values(by=["Done", "Due Date"])
        for i, row in tasks_sorted.iterrows():
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
            with col1:
                done = st.checkbox(f"{row['Task']} [{row['Category']}] (Due: {row['Due Date']})", 
                                   value=row["Done"], key=f"done_{i}")
            with col3:
                delete = st.button("🗑️", key=f"del_{i}")

            if done != row["Done"]:
                tasks.at[i, "Done"] = done
                if done:
                    tasks.at[i, "Completed Date"] = pd.Timestamp.today().normalize()
                else:
                    tasks.at[i, "Completed Date"] = pd.NaT
                tasks.to_csv(TASK_FILE, index=False)
                st.rerun()

            if delete:
                tasks = tasks.drop(i)
                tasks.to_csv(TASK_FILE, index=False)
                st.rerun()

    with tabs[1]:
        st.text_area("Write your thoughts here:")

    with tabs[2]:
        st.write("Coming soon: Chat with your AI companion!")

def render_profile():
    st.header("👤 Your Profile")
    HISTORY_FILE = f"user_history/{st.session_state.username}_history.csv"
    today_str = pd.Timestamp.today().strftime("%Y-%m-%d")

    TASK_FILE = f"user_tasks/{st.session_state.username}_tasks.csv"
    if os.path.exists(TASK_FILE):
        tasks = pd.read_csv(TASK_FILE)
    else:
        tasks = pd.DataFrame(columns=["Task", "Done", "Completed Date"])

    done_count_today = tasks[(tasks["Done"] == True) & 
                           (pd.to_datetime(tasks["Completed Date"]).dt.strftime("%Y-%m-%d") == today_str)].shape[0]

    if os.path.exists(HISTORY_FILE):
        history = pd.read_csv(HISTORY_FILE)
    else:
        history = pd.DataFrame(columns=["Date", "Completed"])

    if today_str not in history["Date"].values:
        new_entry = pd.DataFrame([{"Date": today_str, "Completed": done_count_today}])
        history = pd.concat([history, new_entry], ignore_index=True)
        history.to_csv(HISTORY_FILE, index=False)

    st.subheader("📊 Your Task Completion Over Time")
    chart = alt.Chart(history).mark_bar(color="#0984e3").encode(
        x="Date:T",
        y=alt.Y("Completed:Q", title="Tasks Completed")
    ).properties(width=700, height=300)
    st.altair_chart(chart, use_container_width=True)

# --- Page Rendering Logic ---
if st.session_state.page == "Home":
    st.title("🤖 LifeBot AI")
    st.write(f"Welcome, {st.session_state.username}! I'm your all-in-one AI assistant.")
    st.markdown("---")
    st.subheader("Choose a tool from the left menu to begin.")

if st.session_state.page == "Profile":
    render_profile()

if st.session_state.page == "Daily Companion":
    render_daily_companion()

if st.session_state.page == "Career Pathfinder":
    st.header("💼 Career Pathfinder")
    st.write("Explore careers based on your skills and interests. Coming soon!")

if st.session_state.page == "Managing Finances":
    st.header("💰 Managing Finances")
    st.write("Financial planning tools and tips. Coming soon!")

if st.session_state.page == "Skill-Up AI":
    st.header("📚 Skill-Up AI")
    st.write("Learn anything, your way! Coming soon!")

if st.session_state.page == "Meal Planner":
    st.header("🍽️ Nutrition & Meal Planner")
    st.write("Here you'll find personalized meals and healthy tips. Coming soon!")
