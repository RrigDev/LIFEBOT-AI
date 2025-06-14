import streamlit as st

# Set page config
st.set_page_config(page_title="LifeBot-AI", layout="centered")

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
    st.header("🧠 Daily Companion")
    st.write("This section will include mood check-ins, journaling, and reminders. Coming soon!")

elif page == "Meal Planner":
    st.header("🍽️ Nutrition & Meal Planner")
    st.write("Here you'll find personalized meals and healthy tips. Coming soon!")

elif page == "Career Pathfinder":
    st.header("💼 Career Pathfinder")
    st.write("Explore careers based on your skills and interests. Coming soon!")

elif page == "Skill-Up AI":
    st.header("📚 Skill-Up AI")
    st.write("Learn anything, your way! Coming soon.")
