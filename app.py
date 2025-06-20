import streamlit as st
import pandas as pd
import os

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
    st.subheader("📋 Today's Tasks")

    TASK_FILE = "tasks.csv"

    # Load existing tasks
    if os.path.exists(TASK_FILE):
        tasks = pd.read_csv(TASK_FILE)
    else:
        tasks = pd.DataFrame(columns=["Task", "Done", "Due Date", "Category", "Completed Date"])

    # --- Add New Task ---
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

    # --- Task Progress ---
    total = len(tasks)
    done_count = tasks["Done"].sum()
    if total > 0:
        st.progress(done_count / total)
        st.markdown(f"✅ **{done_count} of {total} tasks completed**")
    else:
        st.info("No tasks added yet!")

    # --- Sort and Display Tasks ---
    tasks_sorted = tasks.sort_values(by=["Done", "Due Date"])

    for i, row in tasks_sorted.iterrows():
        col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
        with col1:
            done = st.checkbox(f"{row['Task']} [{row['Category']}] (Due: {row['Due Date']})", value=row["Done"], key=f"done_{i}")
        with col2:
            st.write("")  # Spacer
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

    # --- Task Completion Over Time Chart ---
    if "Completed Date" in tasks.columns:
        completed_tasks = tasks[tasks["Done"] == True].copy()
        completed_tasks["Completed Date"] = pd.to_datetime(completed_tasks["Completed Date"])
        chart_data = completed_tasks.groupby("Completed Date").size()

        if not chart_data.empty:
            st.subheader("📊 Task Completion Over Time")
            st.bar_chart(chart_data)

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