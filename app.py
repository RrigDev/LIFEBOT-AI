import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LifeBot AI", layout="centered")

# Create users file and data folder if not present
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["Username", "Password"]).to_csv("users.csv", index=False)
if not os.path.exists("data"):
    os.makedirs("data")

# Load users
users_df = pd.read_csv("users.csv")

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login/Sign-up Toggle
auth_mode = st.sidebar.radio("🔐 Choose mode:", ["Login", "Sign Up"])

# Sign-Up Logic
if auth_mode == "Sign Up":
    st.sidebar.subheader("Create a New Account")
    new_user = st.sidebar.text_input("👤 New Username")
    new_pass = st.sidebar.text_input("🔑 New Password", type="password")
    if st.sidebar.button("📩 Register"):
        if new_user in users_df["Username"].values:
            st.sidebar.error("Username already exists!")
        elif not new_user or not new_pass:
            st.sidebar.error("Username and Password required!")
        else:
            users_df = users_df.append({"Username": new_user, "Password": new_pass}, ignore_index=True)
            users_df.to_csv("users.csv", index=False)
            pd.DataFrame(columns=["Task", "Done", "Due Date", "Category", "Completed Date"]).to_csv(f"data/{new_user}_tasks.csv", index=False)
            pd.DataFrame(columns=["Date", "Completed"]).to_csv(f"data/{new_user}_history.csv", index=False)
            st.sidebar.success("Account created! Please log in.")

# Login Logic
if auth_mode == "Login":
    st.sidebar.subheader("Login to LifeBot")
    username = st.sidebar.text_input("👤 Username")
    password = st.sidebar.text_input("🔒 Password", type="password")
    if st.sidebar.button("✅ Login"):
        if ((users_df["Username"] == username) & (users_df["Password"] == password)).any():
            st.session_state.authenticated = True
            st.session_state.username = username
            st.sidebar.success(f"Welcome back, {username}!")
        else:
            st.sidebar.error("Invalid username or password!")

# Stop page if not authenticated
if not st.session_state.authenticated:
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
