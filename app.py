import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
import os

# --- Supabase Setup with Fallback ---
try:
    from supabase import create_client, Client

    SUPABASE_URL = "https://zphpikwyhjeybysfpcfn.supabase.co"
    SUPABASE_KEY = "your_supabase_key_here"  # Replace with your actual Supabase key
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_AVAILABLE = True

except Exception as e:
    st.warning("⚠️ Running in demo mode (Supabase not connected). Data won't be saved permanently.")

    class MockTable:
        def __init__(self, name):
            self.name = name
            self.data = []

        def select(self, *args, **kwargs):
            return type("Resp", (), {"data": self.data})

        def insert(self, row):
            if isinstance(row, dict):
                self.data.append(row)
            elif isinstance(row, list):
                self.data.extend(row)
            return type("Resp", (), {"data": row})

        def upsert(self, row, **kwargs):
            self.insert(row)
            return type("Resp", (), {"data": row})

        def update(self, row):
            return type("Resp", (), {"data": row})

        def delete(self):
            return self

        def eq(self, *args, **kwargs):
            return self

        def order(self, *args, **kwargs):
            return self

        def execute(self):
            return type("Resp", (), {"data": self.data})

    class MockClient:
        def table(self, name):
            return MockTable(name)

    supabase = MockClient()
    SUPABASE_AVAILABLE = False


# --- Streamlit Config ---
st.set_page_config(page_title="LifeBot AI", layout="centered")

# --- Session State Initialization ---
for key in ["logged_in", "username", "page"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else ""

# --- Login via Name Input ---
st.sidebar.title("\U0001F464 Welcome")
name_input = st.sidebar.text_input("Enter your name", key="username_input")
if st.sidebar.button("Submit", key="submit_button"):
    if name_input:
        username = name_input.strip().lower()
        st.session_state.username = username

        # Ensure user exists in the users table
        existing_user = supabase.table("users").select("id").filter("username", "eq", username).execute()
        if not existing_user.data:
            supabase.table("users").insert({"username": username}).execute()

        st.session_state.logged_in = True
        supabase.table("users").upsert(
            {"username": username},
            on_conflict=["username"]
        ).execute()

        st.rerun()

# --- If Logged In ---
if st.session_state.logged_in:
    st.sidebar.title("\U0001F9ED LifeBot AI Menu")
    user_type = st.sidebar.radio("Who are you?", ["Student", "Adult", "Senior Citizen"], horizontal=True)

    pages = ["Home", "Profile", "Daily Companion"]
    pages.append("Career Pathfinder" if user_type == "Student" else "Managing Finances")
    pages.extend(["Skill-Up AI", "Meal Planner"])

    if "page" not in st.session_state or st.session_state.page not in pages:
        st.session_state.page = pages[0]

    st.session_state.page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))

    # --- Page: Home ---
    if st.session_state.page == "Home":
        st.title("\U0001F916 LifeBot AI")
        st.write("Welcome! I'm your all-in-one AI assistant.")
        st.markdown("---")
        st.subheader("Choose a tool from the left menu to begin.")

    # --- Page: Profile ---
    elif st.session_state.page == "Profile":
        st.header("\U0001F464 Your Profile")
        today_str = str(date.today())
        done_today = supabase.table("tasks").select("*")\
            .eq("username", st.session_state.username).eq("done", True).eq("completed_date", today_str).execute().data

        if not supabase.table("history").select("*")\
                .eq("username", st.session_state.username).eq("date", today_str).execute().data:
            supabase.table("history").insert({"username": st.session_state.username, "date": today_str, "completed": len(done_today)}).execute()

        history = supabase.table("history").select("*")\
            .eq("username", st.session_state.username).execute().data

        df = pd.DataFrame(history)
        if not df.empty:
            st.subheader("\U0001F4CA Your Task Completion Over Time")
            chart = alt.Chart(df).mark_bar(color="#0984e3").encode(
                x="date:T",
                y=alt.Y("completed:Q", title="Tasks Completed")
            ).properties(width=700, height=300)
            st.altair_chart(chart, use_container_width=True)

    # --- Page: Daily Companion ---
    elif st.session_state.page == "Daily Companion":
        st.header("\U0001F9E0 Daily Companion")
        tabs = st.tabs(["\U0001F4CB Tasks", "\U0001F4D3 Journal", "\U0001F4AC Companion"])

        # --- Tasks ---
        with tabs[0]:
            tasks = supabase.table("tasks").select("*")\
                .eq("username", st.session_state.username).order("done").order("due_date").execute().data
            df = pd.DataFrame(tasks)

            with st.form("add_task_form", clear_on_submit=True):
                new_task = st.text_input("\U0001F4DD Task")
                due_date = st.date_input("\U0001F4C5 Due Date")
                category = st.radio("\U0001F3F7️ Category", ["Study", "Work", "Personal", "Fitness", "Other"], horizontal=True)
                if st.form_submit_button("➕ Add Task") and new_task.strip():
                    try:
                        supabase.table("tasks").insert({
                            "username": st.session_state.username,
                            "task": new_task.strip(),
                            "done": False,
                            "due_date": str(due_date),
                            "category": category
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

            if not df.empty:
                total = len(df)
                done_count = df["done"].sum()
                st.progress(done_count / total)
                st.markdown(f"✅ **{done_count} of {total} tasks completed**")

                for _, row in df.iterrows():
                    col1, _, col3 = st.columns([0.6, 0.2, 0.2])
                    with col1:
                        done = st.checkbox(
                            f"{row['task']} [{row['category']}] (Due: {row['due_date']})",
                            value=row["done"],
                            key=f"done_{row.get('id', _)}"
                        )
                    with col3:
                        if st.button("🗑️", key=f"del_{row.get('id', _)}"):
                            supabase.table("tasks").delete().eq("id", row.get("id", _)).execute()
                            st.rerun()

                    if done != row["done"]:
                        supabase.table("tasks").update({"done": done, "completed_date": str(date.today()) if done else None})\
                            .eq("id", row.get("id", _)).execute()
                        st.rerun()

        # --- Journal ---
        with tabs[1]:
            st.subheader("\U0001F4DD Journal Your Thoughts")
            mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry", "😴 Tired"])
            entry = st.text_area("Write here")
            if st.button("💾 Save Entry") and entry.strip():
                try:
                    supabase.table("journals").insert({
                        "username": st.session_state.username,
                        "entry": entry.strip(),
                        "mood": mood,
                        "date": str(date.today())
                    }).execute()
                    st.success("Entry saved!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

            st.subheader("\U0001F4DA Past Entries")
            entries = supabase.table("journals").select("*")\
                .eq("username", st.session_state.username).order("date", desc=True).execute().data
            for e in entries:
                st.markdown(f"**{e.get('date', '')}** — *{e.get('mood', '')}*\n> {e.get('entry', '')}")

        # --- Companion ---
        with tabs[2]:
            st.write("Coming soon: Chat with your AI companion!")

    # --- Placeholder Pages ---
    elif st.session_state.page == "Career Pathfinder":
        st.header("\U0001F4BC Career Pathfinder")
        st.info("Explore careers based on your skills and interests. Coming soon!")

    elif st.session_state.page == "Managing Finances":
        st.header("\U0001F4B0 Managing Finances")
        st.info("Financial planning tools and tips. Coming soon!")

    elif st.session_state.page == "Skill-Up AI":
        st.header("\U0001F4DA Skill-Up AI")
        st.info("Learn anything, your way! Coming soon!")

    elif st.session_state.page == "Meal Planner":
        st.title("\U0001F37D️ Meal Planner")
        tabs = st.tabs(["\U0001F372 Log Meal", "\U0001F9FE Suggestions", "\U0001F4A7 Water Tracker", "\U0001F4C8 Overview"])

        with tabs[0]:
            st.subheader("Log Your Meals")
            today = datetime.now().strftime("%Y-%m-%d")
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            meal_name = st.text_input("Meal Name")
            mood = st.radio("Mood After Meal", ["🙂 Happy", "😐 Neutral", "🙁 Low"], horizontal=True)

            if st.button("Save Meal") and meal_name:
                try:
                    supabase.table("meals").insert({
                        "username": st.session_state.username,
                        "date": today,
                        "meal_type": meal_type,
                        "meal_name": meal_name,
                        "mood": mood
                    }).execute()
                    st.success("Meal logged!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        with tabs[1]:
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

        with tabs[2]:
            st.subheader("Track Your Water Intake")
            st.info("Coming soon!")

        with tabs[3]:
            st.subheader("Weekly Meal Overview")
            data = supabase.table("meals").select("date").eq("username", st.session_state.username).execute().data
            df = pd.DataFrame(data)
            if not df.empty:
                count_df = df.groupby("date").size().reset_index(name="meals")
                chart = alt.Chart(count_df).mark_bar(color="#00cec9").encode(
                    x="date:T",
                    y=alt.Y("meals:Q", title="Meals Logged")
                ).properties(width=700, height=300)
                st.altair_chart(chart, use_container_width=True)

else:
    st.title("Welcome to LifeBot AI")
    st.info("Please enter your name in the sidebar to get started.")
