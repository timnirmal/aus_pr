from datetime import datetime

import bcrypt
from bson import ObjectId
import streamlit as st


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


def create_user(username, password, user_type, users_collection):
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


def authenticate_user(username, password, users_collection):
    user = users_collection.find_one({"username": username})
    if user:
        # Check if the user is disabled
        if user.get('disabled', False):
            st.error("This account has been disabled. Please contact support.")
            return None
        elif verify_password(user["password"], password):
            return user
        else:
            return None
    else:
        return None


