from datetime import datetime
import streamlit as st

def manage_course_updates(user, db):
    st.subheader("Update a Course")

    # Fetch the institution based on the user's ID (educator)
    institution = db["institutions"].find_one({"user_id": user["_id"]})

    if not institution:
        st.error("No institution found for this user.")
        return

    institution_id = institution["_id"]

    # Fetch courses associated with this educator's institution
    courses = list(db["courses"].find({"institution_id": institution_id}))

    # If no courses exist
    if not courses:
        st.error("No courses found for this institution.")
        return

    # Dropdown for selecting a course
    course_names = [course["course_name"] for course in courses]
    selected_course_name = st.selectbox("Select Course to Update", course_names)

    # Get the selected course details
    selected_course = next(course for course in courses if course["course_name"] == selected_course_name)

    # Prefill the course details for editing
    new_course_name = st.text_input("Course Name", value=selected_course["course_name"])
    new_location = st.text_input("Location", value=selected_course["location"])
    new_cost = st.number_input("Cost", min_value=0, step=5000, value=selected_course["cost"])
    new_duration = st.number_input("Duration (months)", min_value=0, value=selected_course["duration"])
    new_pr_points = st.number_input("PR Points", min_value=0, value=selected_course["pr_points"])
    new_capacity = st.number_input("Capacity", min_value=1, step=1, value=selected_course["capacity"])
    new_start_date = st.date_input("Start Date", value=selected_course["start_date"].date())

    if st.button("Submit Updates"):
        # Convert datetime.date to datetime.datetime before updating MongoDB
        new_start_datetime = datetime.combine(new_start_date, datetime.min.time())

        # Update course details in the database
        db["courses"].update_one(
            {"_id": selected_course["_id"]},
            {
                "$set": {
                    "course_name": new_course_name,
                    "location": new_location,
                    "cost": new_cost,
                    "duration": new_duration,
                    "pr_points": new_pr_points,
                    "capacity": new_capacity,
                    "start_date": new_start_datetime,  # Store as datetime.datetime
                    "updated_at": datetime.utcnow()
                }
            }
        )
        st.success(f"Course '{new_course_name}' updated successfully.")
        st.session_state.page = "manage_courses"  # Go back to course management page
        st.rerun()
