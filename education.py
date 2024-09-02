from datetime import datetime

import streamlit as st
from bson import ObjectId
from pymongo import DESCENDING



def manage_educational_programs(user, db):
    st.subheader("Manage Your Educational Programs")

    # Fetch courses by this educator
    institution_id = user["_id"]
    courses = db["courses"].find({"institution_id": str(institution_id)}).sort("updated_at", DESCENDING)

    # Display existing courses
    st.write("Your Courses:")
    for course in courses:
        st.write(f"- {course['course_name']} at {course['location']}")
        st.write(f"  Cost: {course['cost']}, Duration: {course['duration']} months, PR Points: {course['pr_points']}")
        st.write("---")

    # Form to add a new course
    st.subheader("Add a New Course")
    new_course_name = st.text_input("Course Name")
    new_location = st.text_input("Location")
    new_cost = st.number_input("Cost", min_value=0.0, step=0.01)
    new_duration = st.number_input("Duration (months)", min_value=0)
    new_pr_points = st.number_input("PR Points", min_value=0)

    if st.button("Submit Course"):
        if new_course_name and new_location:
            new_course = {
                "course_name": new_course_name,
                "institution_id": str(institution_id),
                "location": new_location,
                "cost": new_cost,
                "duration": new_duration,
                "pr_points": new_pr_points,
                "updated_at": datetime.utcnow()
            }
            db["courses"].insert_one(new_course)
            st.success(f"Course '{new_course_name}' added successfully.")
            st.experimental_rerun()
        else:
            st.error("Course Name and Location are required.")

    # Display anonymized statistics on user interest
    st.subheader("Anonymized Interest Statistics")
    interest_stats = db["recommendations"].aggregate([
        {"$unwind": "$pathways"},
        {"$unwind": "$pathways.steps"},
        {"$match": {"pathways.steps.course_id": {"$exists": True}}},
        {"$group": {"_id": "$pathways.steps.course_id", "count": {"$sum": 1}}},
        {"$sort": {"count": DESCENDING}},
        {"$limit": 10}
    ])

    st.write("Top 10 Courses by User Interest:")
    for stat in interest_stats:
        course = db["courses"].find_one({"_id": ObjectId(stat["_id"])})
        if course:
            st.write(f"- {course['course_name']} at {course['location']}: {stat['count']} users interested")
