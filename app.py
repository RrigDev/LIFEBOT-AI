import streamlit as st
import pandas as pd
import os
import altair as alt

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# --- User Identification ---
st.sidebar.title("👤 Welcome")
raw_username = st.sidebar.text_input("Enter your name")

if raw_username:
    username = raw_username.strip().lower()
    st.session_state.username = username
    st.sidebar.success(f"Hello, {raw_username.strip().capitalize()}!")
else:
    st.warning("Please enter your name to continue.")
    st.stop()

# --- File Paths (User-Specific) ---
USER_DB = "users.csv"  # For potential expansion if needed later
TASK_FILE = f"tasks_{username}.csv"
JOURNAL_FILE = f"journal_{username}.csv"
HISTORY_FILE = f"history_{username}.csv"

# --- Ensure Files Exist ---
if not os.path.exists(TASK_FILE):
    pd.DataFrame(columns=["Task", "Done", "Due Date", "Category", "Completed Date"]).to_csv(TASK_FILE, index=False)

if not os.path.exists(JOURNAL_FILE):
    pd.DataFrame(columns=["Date", "Mood", "Entry"]).to_csv(JOURNAL_FILE, index=False)

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["Date", "Completed"]).to_csv(HISTORY_FILE, index=False)

# --- App Launch ---
st.title("Welcome to LifeBot AI")
st.write(f"You are logged in as **{username}**.")
# From here, render your full app interface



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
        HISTORY_FILE = "task_history.csv"
        today_str = pd.Timestamp.today().strftime("%Y-%m-%d")

        if os.path.exists("tasks.csv"):
            tasks = pd.read_csv("tasks.csv")
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

    elif st.session_state.page == "Daily Companion":
        st.header("🧠 Daily Companion")
        tabs = st.tabs(["📋 Tasks", "📓 Journal", "💬 Companion"])

        with tabs[0]:
            TASK_FILE = "tasks.csv"
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
                    tasks.at[i, "Completed Date"] = pd.Timestamp.today().normalize() if done else pd.NaT
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
