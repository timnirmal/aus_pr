import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

from admin.manage_user_account import manage_user_accounts
from admin.refine_algo import admin_refine_algorithm
from admin.reply import show_feedbacks_for_admin, manage_user_inquiries
from admin.statics import admin_report_page
from agent.feedback import show_past_feedback, show_agent_feedbacks
from agent.statics import show_migration_agent_statistics
from education.education import manage_educational_programs

from education.statics import show_full_anonymized_statistics
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

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def main():
    st.title("Migration Application System")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if st.session_state.logged_in:
        # User is logged in, show sidebar menu for navigation based on user type
        user_type = st.session_state.user['user_type']

        if user_type == "prospective_migrant":
            menu = ["Dashboard", "Update Profile", "Inquery", "Logout"]
        elif user_type == "migration_agent":
            menu = ["Dashboard", "Feedbacks", "Logout"]
        elif user_type == "education_provider":
            menu = ["Dashboard", "Manage Educational Programs", "Logout"]
        elif user_type == "administrator":
            menu = ["Dashboard", "Refine Recommendation Algorithm", "Manage Users", "Reply", "Inquery", "Logout"]

        choice = st.sidebar.selectbox("Navigation", menu)

        if choice == "Dashboard":
            show_user_dashboard(st.session_state.user)
        elif choice == "Update Profile":
            update_profile_page(st.session_state.user)
        elif choice == "Inquery" and user_type == "prospective_migrant":
            user_inquiry_section(st.session_state.user, db)
        elif choice == "Feedbacks" and user_type == "migration_agent":
            # Add logic to Feedbacks here
            st.write("Client Management Page for Migration Agents")
            show_past_feedback(st.session_state.user, db)
            show_agent_feedbacks(db)
        elif choice == "Manage Educational Programs" and user_type == "education_provider":
            manage_educational_programs(st.session_state.user, db)
        elif choice == "Refine Recommendation Algorithm" and user_type == "administrator":
            admin_refine_algorithm(db)  # Admin function to refine recommendation algorithm
        elif choice == "Manage Users" and user_type == "administrator":
            # Admin function to manage users
            manage_user_accounts(db)
            # st.write("User Management for Admin")
        elif choice == "Inquery" and user_type == "administrator":
            # Admin function to reply to user queries
            # st.write("Reply to User Queries")
            manage_user_inquiries(db)
        elif choice == "Reply" and user_type == "administrator":
            # Admin function to reply to user queries
            show_feedbacks_for_admin(db)
        elif choice == "Logout":
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    else:
        # User is not logged in, show login/register menu
        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            st.subheader("Login")
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
                    create_user(new_username, new_password, user_type, users_collection)
                    st.success("Registration successful. Please login.")


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
