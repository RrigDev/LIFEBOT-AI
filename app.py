import streamlit as st

# Set page config
st.set_page_config(page_title="LifeBot AI", layout="centered")

# Sidebar navigation
st.sidebar.title("🧭 LifeBot AI Menu")
page = st.sidebar.radio("Go to", ["Home", "Daily Companion", "Meal Planner", "Career Pathfinder", "Skill-Up AI"])

# --- PAGE CONTENT ---
if page == "Home":
    st.title("🤖 LifeBot AI")
    st.write("Welcome! I’m your all-in-one AI assistant for students, parents, professionals — and everyone in between.")
    st.markdown("---")
    st.subheader("Choose a tool from the left menu to begin.")
    st.write("🔒 Your data is safe. AI suggestions are personalized and private.")

elif page == "Daily Companion":
    import pandas as pd
import os

st.header("🧠 Daily Companion")
st.subheader("📋 Today's Tasks")

# File to store tasks
TASK_FILE = "tasks.csv"

# Load tasks
if os.path.exists(TASK_FILE):
    tasks = pd.read_csv(TASK_FILE)
else:
    tasks = pd.DataFrame(columns=["Task", "Done"])

# Add new task
new_task = st.text_input("Add a new task:")
if st.button("➕ Add Task"):
    if new_task.strip():
        tasks = tasks.append({"Task": new_task.strip(), "Done": False}, ignore_index=True)
        tasks.to_csv(TASK_FILE, index=False)
        st.experimental_rerun()

# Show tasks
if not tasks.empty:
    for i, row in tasks.iterrows():
        col1, col2 = st.columns([0.8, 0.2])
        done = col1.checkbox(row["Task"], value=row["Done"])
        delete = col2.button("🗑️", key=i)

        if done != row["Done"]:
            tasks.at[i, "Done"] = done
            tasks.to_csv(TASK_FILE, index=False)

        if delete:
            tasks = tasks.drop(i)
            tasks.to_csv(TASK_FILE, index=False)
            st.experimental_rerun()
else:
    st.info("No tasks added yet!")


elif page == "Meal Planner":
    st.header("🍽️ Nutrition & Meal Planner")
    st.write("Here you'll find personalized meals and healthy tips. Coming soon!")

elif page == "Career Pathfinder":
    st.header("💼 Career Pathfinder")
    st.write("Explore careers based on your skills and interests. Coming soon!")

elif page == "Skill-Up AI":
    st.header("📚 Skill-Up AI")
    st.write("Learn anything, your way! Coming soon.")
