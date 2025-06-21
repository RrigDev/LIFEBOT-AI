import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
import pytz

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# Sidebar navigation
st.sidebar.title("🧭 LifeBot AI Menu")
user_type = st.sidebar.radio("Who are you?", ["Student", "Adult", "Senior Citizen"], horizontal=True)

# Dynamic page options based on user type
pages = ["Home", "Daily Companion"]
if user_type == "Student":
    pages.append("Career Pathfinder")
elif user_type == "Senior Citizen":
    pages.append("Managing Finances")
pages.append("Skill-Up AI")
pages.append("Meal Planner")

page = st.sidebar.radio("Go to", pages)

# --- PAGE CONTENT ---
if page == "Home":
    st.title("🤖 LifeBot AI")
    st.write("Welcome! I’m your all-in-one AI assistant for students, parents, professionals — and everyone in between.")
    st.markdown("---")
    st.subheader("Choose a tool from the left menu to begin.")
    st.write("🔒 Your data is safe. AI suggestions are personalized and private.")

elif page == "Daily Companion":
    st.header("🧠 Daily Companion")

    tabs = st.tabs(["📋 Tasks", "📓 Journal", "💬 Companion Bot"])

    ### --- TASK TAB --- ###
    with tabs[0]:
        st.subheader("📋 Today's Tasks")

        TASK_FILE = "tasks.csv"
        today_ist = datetime.now(pytz.timezone("Asia/Kolkata")).date()

        # Load existing tasks
        if os.path.exists(TASK_FILE):
            tasks = pd.read_csv(TASK_FILE)
        else:
            tasks = pd.DataFrame(columns=["Task", "Done", "Due Date", "Category", "Completed Date"])

        # --- Add New Task ---
        with st.form("add_task_form", clear_on_submit=True):
            new_task = st.text_input("📝 Task")
            due_date = st.date_input("📅 Due Date", min_value=today_ist)
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

        # --- Task Progress ---
        total = len(tasks)
        done_count = tasks["Done"].sum()
        if total > 0:
            st.progress(done_count / total)
            st.markdown(f"✅ **{done_count} of {total} tasks completed**")
        else:
            st.info("No tasks added yet!")

        # --- Completion History and Chart ---
        HISTORY_FILE = "task_history.csv"
        today_str = pd.Timestamp.today().strftime("%Y-%m-%d")

        if os.path.exists(HISTORY_FILE):
            history = pd.read_csv(HISTORY_FILE)
        else:
            history = pd.DataFrame(columns=["Date", "Completed"])

        if today_str in history["Date"].values:
            history.loc[history["Date"] == today_str, "Completed"] = done_count
        else:
            new_entry = pd.DataFrame([{"Date": today_str, "Completed": done_count}])
            history = pd.concat([history, new_entry], ignore_index=True)

        history.to_csv(HISTORY_FILE, index=False)

        chart = alt.Chart(history).mark_bar(color="#74b9ff").encode(
            x="Date:T",
            y=alt.Y("Completed:Q", title="Tasks Completed")
        ).properties(
            title="📊 Task Completion Over Time"
        )

        st.altair_chart(chart, use_container_width=True)

        # --- Sort and Display Tasks ---
        tasks_sorted = tasks.sort_values(by=["Done", "Due Date"])

        for i, row in tasks_sorted.iterrows():
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
            with col1:
                done = st.checkbox(f"{row['Task']} [{row['Category']}] (Due: {row['Due Date']})", value=row["Done"], key=f"done_{i}")
            with col2:
                st.write("")
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

    ### --- JOURNAL TAB --- ###
    with tabs[1]:
        st.subheader("📓 Daily Journal")
        JOURNAL_FILE = "journal.csv"
        journal_entry = st.text_area("How was your day? Write your thoughts here:")
        if st.button("Save Entry"):
            today_str = pd.Timestamp.today().strftime("%Y-%m-%d")
            new_entry = pd.DataFrame([{"Date": today_str, "Entry": journal_entry}])
            if os.path.exists(JOURNAL_FILE):
                old_entries = pd.read_csv(JOURNAL_FILE)
                all_entries = pd.concat([old_entries, new_entry], ignore_index=True)
            else:
                all_entries = new_entry
            all_entries.to_csv(JOURNAL_FILE, index=False)
            st.success("Journal entry saved!")

    ### --- COMPANION BOT TAB --- ###
    with tabs[2]:
        st.subheader("💬 Companion Bot")
        st.info("Coming soon: Chat with your AI buddy for advice, ideas, or just a quick mood boost!")

elif page == "Meal Planner":
    st.header("🍽️ Nutrition & Meal Planner")
    st.write("Here you'll find personalized meals and healthy tips. Coming soon!")

elif page == "Career Pathfinder":
    st.header("💼 Career Pathfinder")
    st.write("Explore careers based on your skills and interests. Coming soon!")

elif page == "Managing Finances":
    st.header("💰 Managing Finances")
    st.write("Financial planning tools and tips. Coming soon!")

elif page == "Skill-Up AI":
    st.header("📚 Skill-Up AI")
    st.write("Learn anything, your way! Coming soon!")
