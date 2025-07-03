import streamlit as st
import pandas as pd
import os
import altair as alt

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

pages = ["Home"]
if user_type == "Student":
    pages.append("Career Pathfinder")
elif user_type in ["Adult", "Senior Citizen"]:
    pages.append("Managing Finances")
pages.extend(["Skill-Up AI", "Meal Planner"])

# Store previous page for comparison
previous_page = st.session_state.get('current_page', 'Home')
st.session_state.current_page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))
current_page = st.session_state.current_page

# Only update the main page if navigation changed
if previous_page != current_page:
    st.session_state.page = current_page

# --- Main Content Area ---
def render_daily_companion():
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
        JOURNAL_FILE = "journal.csv"
        if os.path.exists(JOURNAL_FILE):
            journal = pd.read_csv(JOURNAL_FILE)
        else:
            journal = pd.DataFrame(columns=["Date", "Entry"])

        selected_date = st.date_input("Select Date for Journal")
        entry = ""
        if selected_date.strftime("%Y-%m-%d") in journal["Date"].values:
            entry = journal.loc[journal["Date"] == selected_date.strftime("%Y-%m-%d"), "Entry"].values[0]

        new_entry = st.text_area("📝 Journal Entry", value=entry, height=200)
        if st.button("💾 Save Entry"):
            journal = journal[journal["Date"] != selected_date.strftime("%Y-%m-%d")]
            new_row = pd.DataFrame([{"Date": selected_date.strftime("%Y-%m-%d"), "Entry": new_entry}])
            journal = pd.concat([journal, new_row], ignore_index=True)
            journal.to_csv(JOURNAL_FILE, index=False)
            st.success("Entry saved successfully!")

        st.markdown("---")
        st.subheader("🗓️ Journal History")
        for _, row in journal.sort_values("Date", ascending=False).iterrows():
            with st.expander(f"{row['Date']} - {len(row['Entry'].split())} words"):
                st.write(row['Entry'])

    with tabs[2]:
        st.write("Coming soon: Chat with your AI companion!")

def render_profile():
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

# --- Page Rendering Logic ---
if st.session_state.page == "Home":
    st.title("🤖 LifeBot AI")
    st.write("Welcome! I'm your all-in-one AI assistant.")
    st.markdown("---")
    st.subheader("Choose a tool from the left menu to begin.")

# Render all modules in expanders that maintain their state
with st.expander("🧠 Daily Companion", expanded=st.session_state.expanders_state['Daily Companion']):
    render_daily_companion()
    st.session_state.expanders_state['Daily Companion'] = True  # Keep track that it was rendered

if user_type == "Student":
    with st.expander("💼 Career Pathfinder", expanded=st.session_state.expanders_state['Career Pathfinder']):
        st.header("💼 Career Pathfinder")
        st.write("Explore careers based on your skills and interests. Coming soon!")
        st.session_state.expanders_state['Career Pathfinder'] = True

if user_type in ["Adult", "Senior Citizen"]:
    with st.expander("💰 Managing Finances", expanded=st.session_state.expanders_state['Managing Finances']):
        st.header("💰 Managing Finances")
        st.write("Financial planning tools and tips. Coming soon!")
        st.session_state.expanders_state['Managing Finances'] = True

with st.expander("📚 Skill-Up AI", expanded=st.session_state.expanders_state['Skill-Up AI']):
    st.header("📚 Skill-Up AI")
    st.write("Learn anything, your way! Coming soon!")
    st.session_state.expanders_state['Skill-Up AI'] = True

with st.expander("🍽️ Meal Planner", expanded=st.session_state.expanders_state['Meal Planner']):
    st.header("🍽️ Nutrition & Meal Planner")
    st.write("Here you'll find personalized meals and healthy tips. Coming soon!")
    st.session_state.expanders_state['Meal Planner'] = True

# Profile section
if st.session_state.page == "Profile":
    render_profile()
