from datetime import datetime
import streamlit as st
from bson import ObjectId
from pymongo import DESCENDING

def manage_educational_programs(user, db):
    st.subheader("Manage Your Educational Programs")

    # Fetch the institution based on the user's ID (educator)
    institution = db["institutions"].find_one({"user_id": user["_id"]})
    
    if not institution:
        st.error("No institution found for this user.")
        return
    
    institution_id = institution["_id"]
    
    # Fetch courses associated with this educator's institution
    courses = db["courses"].find({"institution_id": institution_id}).sort("updated_at", DESCENDING)

    # Display existing courses
    st.write(f"Courses for {institution['institution_name']}:")
    for course in courses:
        st.write(f"- {course['course_name']} at {course['location']}")
        st.write(f"  Cost: {course['cost']}, Duration: {course['duration']} months, PR Points: {course['pr_points']}")
        st.write(f"  Capacity: {course['capacity']}, Start Date: {course['start_date']}")
        st.write("---")

    # Form to add a new course
    st.subheader("Add a New Course")
    new_course_name = st.text_input("Course Name")
    new_location = st.text_input("Location")
    new_cost = st.number_input("Cost", min_value=0.0, step=0.01)
    new_duration = st.number_input("Duration (months)", min_value=0)
    new_pr_points = st.number_input("PR Points", min_value=0)
    new_capacity = st.number_input("Capacity", min_value=1, step=1)
    new_start_date = st.date_input("Start Date")

    if st.button("Submit Course"):
        if new_course_name and new_location:
            new_course = {
                "course_name": new_course_name,
                "institution_id": institution_id,  # Link to the institution
                "location": new_location,
                "cost": new_cost,
                "duration": new_duration,
                "pr_points": new_pr_points,
                "capacity": new_capacity,
                "start_date": new_start_date,
                "updated_at": datetime.utcnow()
            }
            db["courses"].insert_one(new_course)
            st.success(f"Course '{new_course_name}' added successfully.")
            st.rerun()  # Refresh the page to show new course
        else:
            st.error("Course Name and Location are required.")


