import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

from education import manage_educational_programs
from questions import update_profile
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
        st.write("Manage your migration profile:")
        update_profile(user, users_collection, db)
    elif user['user_type'] == "migration_agent":
        st.write("Manage your clients:")
        # Add client management options for agents
    elif user['user_type'] == "education_provider":
        st.write("Manage your educational programs:")
        # Add program management options for education providers
        manage_educational_programs(user, db)  # Call the educator function here
    elif user['user_type'] == "administrator":
        st.write("System administration:")
        # Add admin functionalities


if __name__ == "__main__":
    main()
