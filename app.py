iimport streamlit as st
from supabase import create_client, Client

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LifeBot AI", layout="wide")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "signup" not in st.session_state:
    st.session_state["signup"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# --- Signup ---
if st.session_state.get("signup"):
    st.subheader("Sign Up")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Create Account"):
        if username and password:
            existing_user = supabase.table("users").select("id").match({"username": username}).execute()
            if existing_user.data:
                st.error("Username already exists! Please choose another.")
            else:
                supabase.table("users").insert({"username": username, "password": password}).execute()
                st.success("Account created! You can now log in.")
                st.session_state["signup"] = False
        else:
            st.warning("Please enter both username and password.")

# --- Login ---
elif not st.session_state["logged_in"]:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            user = supabase.table("users").select("id").match({"username": username, "password": password}).execute()
            if user.data:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.data[0]["id"]
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

    if st.button("Sign Up Instead"):
        st.session_state["signup"] = True

# --- Main App ---
else:
    st.title("🌟 LifeBot AI")

    menu = st.sidebar.radio("Navigation", ["Tasks", "Journals", "Meal Planner", "Profile", "Logout"])

    # --- Tasks Module ---
    if menu == "Tasks":
        st.header("✅ Tasks")
        task_input = st.text_input("New Task")
        if st.button("Add Task"):
            if task_input:
                supabase.table("tasks").insert({"user_id": st.session_state["user_id"], "task": task_input}).execute()
                st.success("Task added!")

        tasks = supabase.table("tasks").select("*").match({"user_id": st.session_state["user_id"]}).execute()
        if tasks.data:
            for t in tasks.data:
                st.write(f"- {t['task']}")

    # --- Journals Module ---
    elif menu == "Journals":
        st.header("📔 Journals")
        journal_entry = st.text_area("Write your journal entry here...")
        if st.button("Save Entry"):
            if journal_entry:
                supabase.table("journals").insert(
                    {"user_id": st.session_state["user_id"], "entry": journal_entry}
                ).execute()
                st.success("Journal saved!")

        journals = supabase.table("journals").select("*").match({"user_id": st.session_state["user_id"]}).execute()
        if journals.data:
            for j in journals.data:
                st.markdown(f"**Entry {j['id']}**: {j['entry']}")

    # --- Meal Planner Module ---
    elif menu == "Meal Planner":
        st.header("🍽 Meal Planner")
        meal = st.text_input("Meal")
        if st.button("Add Meal"):
            if meal:
                supabase.table("meals").insert({"user_id": st.session_state["user_id"], "meal": meal}).execute()
                st.success("Meal added!")

        meals = supabase.table("meals").select("*").match({"user_id": st.session_state["user_id"]}).execute()
        if meals.data:
            for m in meals.data:
                st.write(f"- {m['meal']}")

    # --- Profile Module ---
    elif menu == "Profile":
        st.header("👤 Profile")
        st.write(f"User ID: {st.session_state['user_id']}")

    # --- Logout ---
    elif menu == "Logout":
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.success("You have been logged out.")


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
