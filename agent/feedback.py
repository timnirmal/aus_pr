import streamlit as st
import pandas as pd
from datetime import datetime

from bson import ObjectId

from user.recommadations import recommend_pr_pathways


# Function to fetch anonymized user profiles for agent to choose from
def get_anonymized_user_profiles(db):
    # Fetch users with type 'prospective_migrant'
    users = db["users"].find({"user_type": "prospective_migrant"})
    anonymized_profiles = []

    for user in users:
        profile = user.get("profile", {})
        anonymized_profiles.append({
            "user_id": user["_id"],
            "skills": profile.get("skills", []),
            "location": profile.get("location", ""),
            "experience_years": sum(
                [employment["years_in_current_role"] for employment in profile.get("employment", [])]),
            "education": [edu["degree_or_course_name"] for edu in profile.get("education", [])],
            "preferences": profile.get("preferences", {})
        })

    return anonymized_profiles


# Function to display anonymized user profiles and let agent pick one
def pick_user_to_review(db):
    st.subheader("Pick a User to Review")

    anonymized_profiles = get_anonymized_user_profiles(db)

    # Create a dropdown with anonymized user details (without names)
    user_options = [
        f"User {i + 1} - Skills: {user['skills']} - Location: {user['location']} - Experience: {user['experience_years']} years"
        for i, user in enumerate(anonymized_profiles)]

    selected_index = st.selectbox("Select a user:", range(len(user_options)), format_func=lambda x: user_options[x])

    # Return the selected user
    return anonymized_profiles[selected_index]


# Function to display recommendations to migration agents with feedback option
def show_recommendations_for_feedback(user, recommendations, db):
    st.subheader(f"Recommendations for the selected user")

    for category, paths in recommendations.items():
        st.subheader(f"{category.upper()} PATHWAYS:")

        if paths:
            df = pd.DataFrame(paths)
            df_display = df[['pathway_name', 'cost', 'duration', 'success_rate', 'difficulty_level',
                             'required_skills', 'recommended_courses', 'locations', 'pr_points_threshold']]
            st.table(df_display)

            # Feedback section for each pathway
            for i, path in df.iterrows():
                st.write(f"Provide Feedback for {path['pathway_name']}")

                # Rating for accuracy and feasibility
                accuracy = st.slider(f"Accuracy of Recommendation for {path['pathway_name']}", 1, 5, 3,
                                     key=f"accuracy_{path['pathway_id']}")
                feasibility = st.slider(f"Feasibility of Pathway for {path['pathway_name']}", 1, 5, 3,
                                        key=f"feasibility_{path['pathway_id']}")

                # Comment box for additional feedback
                comments = st.text_area(f"Comments or Suggestions for {path['pathway_name']}", "",
                                        key=f"comments_{path['pathway_id']}")

                if st.button(f"Submit Feedback for {path['pathway_name']}", key=f"submit_{path['pathway_id']}"):
                    feedback = {
                        "user_id": user['user_id'],
                        "pathway_id": path['pathway_id'],
                        "agent_id": st.session_state.user["_id"],  # Assuming agent is logged in
                        "accuracy": accuracy,
                        "feasibility": feasibility,
                        "comments": comments,
                        "reply": "",
                        "submitted_at": datetime.utcnow()
                    }

                    # Store feedback in the database
                    db["agent_feedback"].insert_one(feedback)
                    st.success(f"Feedback for {path['pathway_name']} submitted successfully.")


# Main function to let agent select a user and view recommendations
def show_agent_feedbacks(db):
    # Agent selects a user based on anonymized data
    selected_user = pick_user_to_review(db)

    if selected_user:
        # Show recommendations for the selected user
        with st.spinner('Loading recommendations...'):
            recommendations = recommend_pr_pathways({"_id": selected_user['user_id']}, db)  # Generating recommendations
            # keep only first 5
            recommendations = {k: v[:5] for k, v in recommendations.items()}
            show_recommendations_for_feedback(selected_user, recommendations, db)


# Function to view past feedback from migration agents
def show_past_feedback(user, db):
    st.subheader(f"Past Feedback for the selected user")

    # Fetch feedback records from the database based on the agent_id
    feedback_records = db["agent_feedback"].find({"agent_id": user['_id']})
    feedback_list = []

    for record in feedback_records:
        # Find the pathway details using the pathway_id
        pathway = db["pr_pathways"].find_one({"_id": ObjectId(record["pathway_id"])})
        if pathway:
            feedback_list.append({
                "pathway_name": pathway['pathway_name'],
                "accuracy": record["accuracy"],
                "feasibility": record["feasibility"],
                "comments": record["comments"],
                "reply": record["reply"],
                "submitted_at": record["submitted_at"]
            })
        else:
            st.warning(f"Pathway ID {record['pathway_id']} not found in the database.")

    # Display feedback if available
    if feedback_list:
        feedback_df = pd.DataFrame(feedback_list)
        st.table(feedback_df)
    else:
        st.write("No feedback found for this user.")

