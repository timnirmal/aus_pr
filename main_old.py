import streamlit as st
import bcrypt
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
uri = os.getenv("MONGO_URI")
print(uri)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["aus-pr"]
users_collection = db["users"]
print("Connected to MongoDB")

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


def create_user(username, password, user_type):
    hashed_password = hash_password(password)
    user = {
        "_id": ObjectId(),
        "username": username,
        "password": hashed_password,
        "user_type": user_type,
        "profile": {
            "first_name": "",
            "last_name": "",
            "date_of_birth": None,
            "gender": "",
            "location": "",
            "nationality": "",
            "skills": [],
            "experience_years": 0,
            "english_proficiency": "",
            "preferences": {
                "location_preference": "",
                "study_preference": "",
                "cost_limit": 0,
                "duration_limit": 0
            }
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    users_collection.insert_one(user)


def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user["password"], password):
        return user
    return None


def main():
    st.title("Migration Application System")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if st.session_state.logged_in:
        show_user_dashboard(st.session_state.user)
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    else:
        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Logged in as {user['username']} ({user['user_type']})")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        elif choice == "Register":
            st.subheader("Register")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            user_type = st.selectbox("User Type",
                                     ["prospective_migrant", "migration_agent", "education_provider", "administrator"])

            if st.button("Register"):
                if users_collection.find_one({"username": new_username}):
                    st.error("Username already exists")
                else:
                    create_user(new_username, new_password, user_type)
                    st.success("Registration successful. Please login.")


def show_user_dashboard(user):
    st.subheader(f"Welcome, {user['username']}!")

    if user['user_type'] == "prospective_migrant":
        st.write("Manage your migration profile:")
        update_profile(user)
    elif user['user_type'] == "migration_agent":
        st.write("Manage your clients:")
        # Add client management options for agents
    elif user['user_type'] == "education_provider":
        st.write("Manage your educational programs:")
        # Add program management options for education providers
    elif user['user_type'] == "administrator":
        st.write("System administration:")
        # Add admin functionalities


def update_profile(user):
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


if __name__ == "__main__":
    main()
