import streamlit as st
import pandas as pd
import os
import altair as alt

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# Initialize session state for expanded modules
if 'expanded_modules' not in st.session_state:
    st.session_state.expanded_modules = {
        'Daily Companion': True,
        'Meal Planner': True,
        'Career Pathfinder': True,
        'Managing Finances': True,
        'Skill-Up AI': True
    }

# --- Sidebar ---
st.sidebar.title("🧭 LifeBot AI Menu")

# User type selection
user_type = st.sidebar.radio("Who are you?", ["Student", "Adult", "Senior Citizen"], horizontal=True)

# Dynamic page options based on user type
pages = ["Home", "Daily Companion", "Profile"]
if user_type == "Student":
    pages.append("Career Pathfinder")
elif user_type in ["Adult", "Senior Citizen"]:
    pages.append("Managing Finances")
pages.append("Skill-Up AI")
pages.append("Meal Planner")

# Initialize session state for current page
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation
selected_page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))
st.session_state.page = selected_page

# --- PAGE CONTENT ---
if st.session_state.page == "Home":
    st.title("🤖 LifeBot AI")
    st.write("Welcome! I'm your all-in-one AI assistant for students, parents, professionals — and everyone in between.")
    st.markdown("---")
    st.subheader("Choose a tool from the left menu to begin.")
    st.write("🔒 Your data is safe. AI suggestions are personalized and private.")

# Create a container for all modules
module_container = st.container()

# Always show Daily Companion module
with module_container:
    with st.expander("🧠 Daily Companion", expanded=st.session_state.expanded_modules['Daily Companion']):
        if st.session_state.page == "Daily Companion" or st.session_state.expanded_modules['Daily Companion']:
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

            with tabs[1]:
                st.text_area("Write your thoughts here:")

            with tabs[2]:
                st.write("Coming soon: Chat with your AI companion!")

# Always show Profile module
if st.session_state.page == "Profile":
    with module_container:
        st.header("👤 Your Profile")

        HISTORY_FILE = "task_history.csv"
        today_str = pd.Timestamp.today().strftime("%Y-%m-%d")

        if os.path.exists("tasks.csv"):
            tasks = pd.read_csv("tasks.csv")
        else:
            tasks = pd.DataFrame(columns=["Task", "Done", "Completed Date"])

        done_count_today = tasks[(tasks["Done"] == True) & (pd.to_datetime(tasks["Completed Date"]).dt.strftime("%Y-%m-%d") == today_str)].shape[0]

        if os.path.exists(HISTORY_FILE):
            history = pd.read_csv(HISTORY_FILE)
        else:
            history = pd.DataFrame(columns=["Date", "Completed"])

        if today_str in history["Date"].values:
            history.loc[history["Date"] == today_str, "Completed"] = done_count_today
        else:
            new_entry = pd.DataFrame([{"Date": today_str, "Completed": done_count_today}])
            history = pd.concat([history, new_entry], ignore_index=True)

        history.to_csv(HISTORY_FILE, index=False)

        st.subheader("📊 Your Task Completion Over Time")
        chart = alt.Chart(history).mark_bar(color="#0984e3").encode(
            x="Date:T",
            y=alt.Y("Completed:Q", title="Tasks Completed")
        ).properties(
            width=700,
            height=300
        )

        st.altair_chart(chart, use_container_width=True)

# Show other modules based on user type
with module_container:
    if user_type == "Student":
        with st.expander("💼 Career Pathfinder", expanded=st.session_state.expanded_modules['Career Pathfinder']):
            if st.session_state.page == "Career Pathfinder" or st.session_state.expanded_modules['Career Pathfinder']:
                st.header("💼 Career Pathfinder")
                st.write("Explore careers based on your skills and interests. Coming soon!")
    
    if user_type in ["Adult", "Senior Citizen"]:
        with st.expander("💰 Managing Finances", expanded=st.session_state.expanded_modules['Managing Finances']):
            if st.session_state.page == "Managing Finances" or st.session_state.expanded_modules['Managing Finances']:
                st.header("💰 Managing Finances")
                st.write("Financial planning tools and tips. Coming soon!")
    
    with st.expander("📚 Skill-Up AI", expanded=st.session_state.expanded_modules['Skill-Up AI']):
        if st.session_state.page == "Skill-Up AI" or st.session_state.expanded_modules['Skill-Up AI']:
            st.header("📚 Skill-Up AI")
            st.write("Learn anything, your way! Coming soon!")
    
    with st.expander("🍽️ Nutrition & Meal Planner", expanded=st.session_state.expanded_modules['Meal Planner']):
        if st.session_state.page == "Meal Planner" or st.session_state.expanded_modules['Meal Planner']:
            st.header("🍽️ Nutrition & Meal Planner")
            st.write("Here you'll find personalized meals and healthy tips. Coming soon!")

# Add toggle buttons to control module visibility
with st.sidebar:
    st.markdown("---")
    st.markdown("**Module Visibility**")
    for module in st.session_state.expanded_modules:
        st.session_state.expanded_modules[module] = st.checkbox(
            f"Show {module}",
            value=st.session_state.expanded_modules[module],
            key=f"show_{module}"
        )
