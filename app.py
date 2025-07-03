import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LifeBot AI Login", layout="centered")

# --- Constants ---
USER_DB = "users.csv"

# --- Ensure User Database Exists ---
if not os.path.exists(USER_DB) or os.stat(USER_DB).st_size == 0:
    df = pd.DataFrame(columns=["Username", "Password"])
    df.to_csv(USER_DB, index=False)

# --- Load Users ---
users_df = pd.read_csv(USER_DB)

# --- Page State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# --- App Logic ---
st.title("🔐 LifeBot AI Login System")

menu = st.radio("Select an option", ["Login", "Sign Up"])

if menu == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users_df["Username"].values:
            user_row = users_df[users_df["Username"] == username]
            if user_row["Password"].values[0] == password:
                st.success(f"Welcome back, {username}!")
                st.session_state.logged_in = True
                st.session_state.current_user = username
            else:
                st.error("Incorrect password.")
        else:
            st.error("Username not found.")

elif menu == "Sign Up":
    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")

    if st.button("Sign Up"):
        if new_user in users_df["Username"].values:
            st.warning("Username already exists. Try logging in.")
        else:
            new_row = pd.DataFrame([{"Username": new_user, "Password": new_pass}])
            users_df = pd.concat([users_df, new_row], ignore_index=True)
            users_df.to_csv(USER_DB, index=False)
            st.success("Account created! You can now log in.")

# --- Logged In View ---
if st.session_state.logged_in:
    st.markdown("---")
    st.subheader(f"🎉 You are logged in as **{st.session_state.current_user}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.experimental_rerun()


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
