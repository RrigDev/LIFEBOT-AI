import streamlit as st

# App title
st.title("🤖 LifeBot AI")
st.write("Welcome! I’m your all-in-one AI assistant for students, parents, professionals — and everyone in between.")

# Divider
st.markdown("---")

# Navigation Buttons
st.subheader("Choose what you'd like help with:")
col1, col2 = st.columns(2)

with col1:
    if st.button("🧠 Daily Companion"):
        st.write("Coming soon: mood check-ins, journaling, reminders!")

    if st.button("🍽️ Nutrition & Meal Planner"):
        st.write("Coming soon: personalized meals and healthy tips!")

with col2:
    if st.button("💼 Career Pathfinder"):
        st.write("Coming soon: explore jobs based on your skills and interests!")

    if st.button("📚 Skill-Up AI"):
        st.write("Coming soon: learn anything, your way!")

# Footer
st.markdown("---")
st.write("🔒 Your data is safe. AI suggestions are personalized and private.")