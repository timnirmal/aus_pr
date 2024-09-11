import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# Function to display admin panel for refining recommendation algorithm
def admin_refine_algorithm(db):
    st.title("Admin - Refine Recommendation Algorithm")

    # Fetch existing algorithm parameters from MongoDB or set defaults
    parameters = db["algorithm_parameters"].find_one({"_id": "default"})
    if not parameters:
        # Default weights
        parameters = {
            "skill_weight": 0.25,
            "experience_weight": 0.2,
            "course_completion_weight": 0.15,
            "location_weight": 0.1,
            "pr_points_weight": 0.1,
            "success_rate_weight": 0.1,
            "difficulty_weight": 0.05,
            "cost_weight": 0.05,
            "duration_weight": 0.05
        }

    st.subheader("Adjust Algorithm Weights")

    # Adjust each parameter
    skill_weight = st.slider("Skill Match Weight", 0.0, 1.0, parameters.get("skill_weight", 0.25))
    experience_weight = st.slider("Experience Match Weight", 0.0, 1.0, parameters.get("experience_weight", 0.2))
    course_completion_weight = st.slider("Course Completion Weight", 0.0, 1.0, parameters.get("course_completion_weight", 0.15))
    location_weight = st.slider("Location Match Weight", 0.0, 1.0, parameters.get("location_weight", 0.1))
    pr_points_weight = st.slider("PR Points Match Weight", 0.0, 1.0, parameters.get("pr_points_weight", 0.1))
    success_rate_weight = st.slider("Success Rate Weight", 0.0, 1.0, parameters.get("success_rate_weight", 0.1))
    difficulty_weight = st.slider("Difficulty Level Weight", 0.0, 1.0, parameters.get("difficulty_weight", 0.05))
    cost_weight = st.slider("Cost Weight", 0.0, 1.0, parameters.get("cost_weight", 0.05))
    duration_weight = st.slider("Duration Weight", 0.0, 1.0, parameters.get("duration_weight", 0.05))

    if st.button("Save Changes"):
        # Save the updated parameters to MongoDB
        db["algorithm_parameters"].update_one({"_id": "default"}, {
            "$set": {
                "skill_weight": skill_weight,
                "experience_weight": experience_weight,
                "course_completion_weight": course_completion_weight,
                "location_weight": location_weight,
                "pr_points_weight": pr_points_weight,
                "success_rate_weight": success_rate_weight,
                "difficulty_weight": difficulty_weight,
                "cost_weight": cost_weight,
                "duration_weight": duration_weight,
                "updated_at": datetime.utcnow()
            }
        }, upsert=True)
        st.success("Algorithm parameters updated successfully!")
