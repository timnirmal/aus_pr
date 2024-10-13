import re
import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

from admin.analyze import show_analytics
from admin.feedback import show_feedbacks_for_admin
from admin.manage_user_account import manage_user_accounts
from admin.refine_algo import admin_refine_algorithm
from admin.inquery import manage_user_inquiries
from admin.statics import admin_report_page
from agent.feedback import show_past_feedback, show_agent_feedbacks
from agent.statics import show_migration_agent_statistics
from education.education import manage_educational_programs
from education.statics import show_full_anonymized_statistics
from education.update_education import manage_course_updates
from user.questions import update_profile
from user.recommadations import recommend_pr_pathways, show_recommendations, show_saved_recommendations
from user.inquery import user_inquiry_section
from user.user_management import create_user, authenticate_user

# Load environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")

# Initialize MongoDB client
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["aus-pr"]
users_collection = db["users"]

# Custom CSS for styling
custom_css = """
    <style>
    body {
        background-color: #F2F2F2;
    }
    .auth-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
        color: #2BA9E0;
    }
    .stButton button {
        width: 100%;
        background-color: #2BA9E0;
        color: white;
        padding: 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #0C2A50;
    }
    a {
        color: #2BA9E0;
        text-align: center;
        display: block;
        margin-top: 20px;
        cursor: pointer;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Verify MongoDB connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    # Debug: Show session state
    # st.write('Session State at start of main:', st.session_state)

    if st.session_state.logged_in:
        user_type = st.session_state.user['user_type']
        menu = get_user_menu(user_type)

        st.sidebar.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)
        for item in menu:
            if st.sidebar.button(item, key=item):
                st.session_state.selected_menu_item = item

        # Ensure selected_menu_item is set
        selected_menu_item = st.session_state.get('selected_menu_item', "Dashboard")

        # Debug: Print selected menu item
        # st.write('Selected Menu Item:', selected_menu_item)

        handle_navigation(selected_menu_item)
    else:
        # Reset selected_menu_item when not logged in
        st.session_state.selected_menu_item = None

        if st.session_state.page == "login":
            login_form()
        elif st.session_state.page == "register":
            register_form()

def get_user_menu(user_type):
    return {
        "prospective_migrant": ["Dashboard", "Update Profile", "Inquery", "View Analytics", "Logout"],
        "migration_agent": ["Dashboard", "Feedbacks", "Logout"],
        "education_provider": ["Dashboard", "Manage Educational Programs", "Update Course", "Logout"],
        "administrator": ["Dashboard", "Refine Recommendation Algorithm", "Manage Users",
                          "Reply", "Inquery", "View Analytics", "Logout"]
    }.get(user_type, [])

def handle_navigation(selected_menu_item):
    user = st.session_state.user
    if selected_menu_item == "Dashboard":
        show_user_dashboard(user)
    elif selected_menu_item == "Update Profile":
        update_profile_page(user)
    elif selected_menu_item == "Inquery":
        if user['user_type'] == "prospective_migrant":
            user_inquiry_section(user, db)
        elif user['user_type'] == "administrator":
            manage_user_inquiries(db)
    elif selected_menu_item == "Feedbacks":
        show_past_feedback(user, db)
        show_agent_feedbacks(db)
    elif selected_menu_item == "Manage Educational Programs":
        manage_educational_programs(user, db)
    elif selected_menu_item == "Update Course":
        manage_course_updates(user, db)
    elif selected_menu_item == "Refine Recommendation Algorithm":
        admin_refine_algorithm(db)
    elif selected_menu_item == "Manage Users":
        manage_user_accounts(db)
    elif selected_menu_item == "View Analytics":
        show_analytics()
    elif selected_menu_item == "Reply":
        show_feedbacks_for_admin(db)
    elif selected_menu_item == "Logout":
        # Reset session state on logout
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "login"
        st.session_state.selected_menu_item = None  # Reset selected_menu_item
        st.rerun()
    else:
        # Default to Dashboard if unknown selection
        show_user_dashboard(user)

def login_form():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password, users_collection)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.page = "dashboard"
            st.session_state.selected_menu_item = "Dashboard"  # Reset selected menu item
            st.success(f"Logged in as {user['username']} ({user['user_type']})")
            st.rerun()
        else:
            st.error("Invalid username or password")

    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()

def register_form():
    st.header("Register")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    user_type = st.selectbox("User Type", ["prospective_migrant", "migration_agent",
                                           "education_provider", "administrator"])

    if st.button("Register"):
        if users_collection.find_one({"username": new_username}):
            st.error("Username already exists.")
        elif users_collection.find_one({"email": new_email}):
            st.error("Email already exists.")
        else:
            create_user(new_username, new_password, user_type, users_collection)
            st.success("Registration successful. Please login.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

def show_user_dashboard(user):
    st.subheader(f"Welcome, {user['username']}!")
    if user['user_type'] == "prospective_migrant":
        rec_saved = show_saved_recommendations(user, db)
        with st.spinner('Loading recommendations...'):
            recommendations = recommend_pr_pathways(user, db)
            # Limit to first 10 recommendations
            recommendations = {k: recommendations[k][:10] for k in recommendations}
            show_recommendations(recommendations, user, db, rec_saved)
    elif user['user_type'] == "migration_agent":
        show_migration_agent_statistics(db)
    elif user['user_type'] == "education_provider":
        show_full_anonymized_statistics(db)
    elif user['user_type'] == "administrator":
        admin_report_page(db)

def update_profile_page(user):
    update_profile(user, users_collection, db)

if __name__ == "__main__":
    main()
