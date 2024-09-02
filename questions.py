from datetime import datetime

import streamlit as st



def update_profile(user, users_collection, db):
    st.subheader("Update Profile")

    profile = user.get('profile', {})

    new_first_name = st.text_input("First Name", profile.get('first_name', ''))
    new_last_name = st.text_input("Last Name", profile.get('last_name', ''))
    new_date_of_birth = st.date_input("Date of Birth", profile.get('date_of_birth'))
    gender_options = ["Male", "Female", "Other"]
    new_gender = st.selectbox("Gender", gender_options,
                              index=gender_options.index(profile.get('gender', 'Other')) if profile.get('gender',
                                                                                                        'Other') in gender_options else 2)
    new_location = st.text_input("Current Location", profile.get('location', ''))
    new_nationality = st.text_input("Nationality", profile.get('nationality', ''))
    new_skills = st.text_input("Skills (comma-separated)", ", ".join(profile.get('skills', [])))
    new_experience_years = st.number_input("Years of Experience", value=profile.get('experience_years', 0), min_value=0)
    english_proficiency_options = ["Beginner", "Intermediate", "Advanced", "Native"]
    new_english_proficiency = st.selectbox("English Proficiency", english_proficiency_options,
                                           index=english_proficiency_options.index(
                                               profile.get('english_proficiency', 'Beginner')) if profile.get(
                                               'english_proficiency', 'Beginner') in english_proficiency_options else 0)

    st.subheader("Preferences")

    # Fetch available locations and study preferences from MongoDB
    location_options = [f"{loc['state']} - {loc['district']}" for loc in db["locations"].find()]
    study_preferences = [f"{study['institution_name']} - {study['study_location']}" for study in
                         db["study_locations"].find()]

    new_location_preference = st.selectbox("Preferred Location", location_options, index=location_options.index(
        profile.get('preferences', {}).get('location_preference', '')))
    new_study_preference = st.selectbox("Study Preference", study_preferences, index=study_preferences.index(
        profile.get('preferences', {}).get('study_preference', '')))
    new_cost_limit = st.number_input("Cost Limit", value=profile.get('preferences', {}).get('cost_limit', 0),
                                     min_value=0)
    new_duration_limit = st.number_input("Duration Limit (months)",
                                         value=profile.get('preferences', {}).get('duration_limit', 0), min_value=0)

    if st.button("Save Changes"):
        updates = {
            "profile": {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "date_of_birth": new_date_of_birth,
                "gender": new_gender,
                "location": new_location,
                "nationality": new_nationality,
                "skills": [skill.strip() for skill in new_skills.split(',') if skill.strip()],
                "experience_years": new_experience_years,
                "english_proficiency": new_english_proficiency,
                "preferences": {
                    "location_preference": new_location_preference,
                    "study_preference": new_study_preference,
                    "cost_limit": new_cost_limit,
                    "duration_limit": new_duration_limit
                }
            },
            "updated_at": datetime.utcnow()
        }

        users_collection.update_one({"_id": user['_id']}, {"$set": updates})
        st.success("Profile updated successfully")
