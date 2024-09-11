import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

from admin.manage_user_account import manage_user_accounts
from admin.refine_algo import admin_refine_algorithm
from education import manage_educational_programs
from questions import update_profile
from recommadations import recommend_pr_pathways, show_recommendations
from user_management import create_user, authenticate_user

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
            menu = ["Dashboard", "Update Profile", "Logout"]
        elif user_type == "migration_agent":
            menu = ["Dashboard", "Manage Clients", "Logout"]
        elif user_type == "education_provider":
            menu = ["Dashboard", "Manage Educational Programs", "Logout"]
        elif user_type == "administrator":
            menu = ["Dashboard", "Refine Recommendation Algorithm", "Manage Users", "Logout"]

        choice = st.sidebar.selectbox("Navigation", menu)

        if choice == "Dashboard":
            show_user_dashboard(st.session_state.user)
        elif choice == "Update Profile":
            update_profile_page(st.session_state.user)
        elif choice == "Manage Clients" and user_type == "migration_agent":
            # Add logic to manage clients here
            st.write("Client Management Page for Migration Agents")
        elif choice == "Manage Educational Programs" and user_type == "education_provider":
            manage_educational_programs(st.session_state.user, db)
        elif choice == "Refine Recommendation Algorithm" and user_type == "administrator":
            admin_refine_algorithm(db)  # Admin function to refine recommendation algorithm
        elif choice == "Manage Users" and user_type == "administrator":
            # Admin function to manage users
            manage_user_accounts(db)
            # st.write("User Management for Admin")
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
        st.write("Manage your migration profile from the sidebar.")
        recommendations = recommend_pr_pathways(user, db)
        show_recommendations(recommendations)

    elif user['user_type'] == "migration_agent":
        st.write("Manage your clients:")
    elif user['user_type'] == "education_provider":
        st.write("Manage your educational programs:")
        manage_educational_programs(user, db)  # Call the educator function here
    elif user['user_type'] == "administrator":
        st.write("System administration:")
        # Add admin functionalities

def update_profile_page(user):
    st.subheader("Update Profile")
    update_profile(user, users_collection, db)

if __name__ == "__main__":
    main()
