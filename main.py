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

load_dotenv()
uri = os.getenv("MONGO_URI")
print(uri)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["aus-pr"]
users_collection = db["users"]
print("Connected to MongoDB")

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

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if st.session_state.logged_in:
        user_type = st.session_state.user['user_type']

        # Define the menu based on user type
        if user_type == "prospective_migrant":
            menu = ["Dashboard", "Update Profile", "Inquery", "View Analytics", "Logout"]
        elif user_type == "migration_agent":
            menu = ["Dashboard", "Feedbacks", "Logout"]
        elif user_type == "education_provider":
            menu = ["Dashboard", "Manage Educational Programs", "Update Course", "Logout"]
        elif user_type == "administrator":
            menu = ["Dashboard", "Refine Recommendation Algorithm", "Manage Users",
                    "Reply", "Inquery", "View Analytics", "Logout"]

        # Display buttons in the sidebar
        st.sidebar.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)

        # Render each menu item as a button
        selected_menu_item = None
        for item in menu:
            if st.sidebar.button(item):
                selected_menu_item = item

        # Navigate based on the selected menu item
        if selected_menu_item == "Dashboard":
            show_user_dashboard(st.session_state.user)
        elif selected_menu_item == "Update Profile":
            update_profile_page(st.session_state.user)
        elif selected_menu_item == "Inquery" and user_type == "prospective_migrant":
            user_inquiry_section(st.session_state.user, db)
        elif selected_menu_item == "Feedbacks" and user_type == "migration_agent":
            show_past_feedback(st.session_state.user, db)
            show_agent_feedbacks(db)
        elif selected_menu_item == "Manage Educational Programs" and user_type == "education_provider":
            manage_educational_programs(st.session_state.user, db)
        elif selected_menu_item == "Update Course" and user_type == "education_provider":
            manage_course_updates(st.session_state.user, db)
        elif selected_menu_item == "Refine Recommendation Algorithm" and user_type == "administrator":
            admin_refine_algorithm(db)
        elif selected_menu_item == "Manage Users" and user_type == "administrator":
            manage_user_accounts(db)
        elif selected_menu_item == "View Analytics":
            show_analytics()
        elif selected_menu_item == "Inquery" and user_type == "administrator":
            manage_user_inquiries(db)
        elif selected_menu_item == "Reply" and user_type == "administrator":
            show_feedbacks_for_admin(db)
        elif selected_menu_item == "Logout":
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    else:
        st.title("Migration Application System")

        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.user = None

        if st.session_state.logged_in:
            st.subheader(f"Welcome, {st.session_state.user['username']}!")
        else:
            if 'page' not in st.session_state:
                st.session_state.page = "login"

            if st.session_state.page == "login":
                login_form()
            elif st.session_state.page == "register":
                register_form()


def login_form():
    # st.markdown('<div class="auth-container"> Login', unsafe_allow_html=True)
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password, users_collection)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Logged in as {user['username']} ({user['user_type']})")
            st.rerun()
        else:
            st.error("Invalid username or password")

    # Properly trigger page change using session_state
    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def register_form():
    st.header("Register")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    user_type = st.selectbox("User Type", ["prospective_migrant", "migration_agent", "education_provider", "administrator"])

    # Email regex pattern for validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    def validate_password(password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not any(char.isupper() for char in password):
            return "Password must contain at least one uppercase letter."
        if not any(char.islower() for char in password):
            return "Password must contain at least one lowercase letter."
        if not any(char.isdigit() for char in password):
            return "Password must contain at least one number."
        if not any(char in "@$!%*?&" for char in password):
            return "Password must contain at least one special character (@, $, !, %, *, ?, &)."
        return None  # If all conditions are satisfied

    if st.button("Register"):
        # Check if username, email, and password are entered
        if not new_username:
            st.error("Please enter a username.")
        elif not new_email:
            st.error("Please enter an email.")
        elif not re.match(email_regex, new_email):
            st.error("Please enter a valid email address.")
        elif not new_password:
            st.error("Please enter a password.")
        else:
            password_error = validate_password(new_password)
            if password_error:
                st.error(password_error)
            else:
                # Check if username already exists
                if users_collection.find_one({"username": new_username}):
                    st.error("Username already exists.")
                elif users_collection.find_one({"email": new_email}):
                    st.error("Email already exists.")
                else:
                    # Create user if validation passes
                    create_user(new_username, new_password, user_type, users_collection)
                    st.success("Registration successful. Please login.")
                    st.session_state.page = "login"
                    st.rerun()

    # Button to switch back to login form
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()



def show_user_dashboard(user):
    st.subheader(f"Welcome, {user['username']}!")

    if user['user_type'] == "prospective_migrant":
        # st.write("Manage your migration profile from the sidebar.")
        # Show saved recommendations when the page loads
        rec_saved = show_saved_recommendations(user, db)
        # Show recommendations with a loading spinner
        with st.spinner('Loading recommendations...'):
            recommendations = recommend_pr_pathways(st.session_state.user, db)
            #             recommendations = {'fully_qualified': [], 'partially_qualified': [], 'potential_interest': [{'pathway_id': '66dfe2427ff7cf28671c4ad3', 'pathway_name': 'IT Specialist Pathway', 'score': 18.75, 'cost': 15000, 'duration':
            # 36, 'success_rate': 85, 'difficulty_level': 5, 'required_skills': ['IT', 'Software Development'], 'required_experience_years': 2, 'pr_points_threshold': 70, 'recommended_courses': ['Bachelor of IT', 'Master of Data Science'], 'locations': ['Sydney', 'Melbourne']}]}
            # keep only first 10 recommendations
            recommendations = {k: recommendations[k][:10] for k in recommendations}
            show_recommendations(recommendations, user, db, rec_saved)

        st.markdown("""
            ---
            **Disclaimer**: The recommendations provided by this system are based on the available data and algorithmic processing. 
            While we strive to ensure the accuracy and relevance of the information, we cannot guarantee that every recommendation 
            will be fully applicable to your situation. The system's results should be considered as guidance only and not as an 
            authoritative decision-making tool. 

            **Affiliation**: This system is not officially affiliated with any immigration authorities or government institutions. 
            All the data used is for educational and guidance purposes, and users should consult official resources for 
            detailed and legally binding information.
            """)

    elif user['user_type'] == "migration_agent":
        # st.write("Manage your clients:")
        show_migration_agent_statistics(db)
    elif user['user_type'] == "education_provider":
        # st.write("Manage your educational programs:")
        # manage_educational_programs(user, db)  # Call the educator function here
        show_full_anonymized_statistics(db)
    elif user['user_type'] == "administrator":
        # st.write("System administration:")
        # Add admin functionalities
        admin_report_page(db)


def update_profile_page(user):
    # st.subheader("Update Profile")
    update_profile(user, users_collection, db)


if __name__ == "__main__":
    main()
