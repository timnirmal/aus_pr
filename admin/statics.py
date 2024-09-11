import pandas as pd
import streamlit as st
from bson import ObjectId


# Function to generate usage and trend report for admins
def generate_admin_report(db):
    st.subheader("Admin Report: Usage and Trends")

    # Section 1: User Overview
    st.subheader("User Overview")
    total_users = db["users"].count_documents({})
    total_migrants = db["users"].count_documents({"user_type": "prospective_migrant"})
    total_agents = db["users"].count_documents({"user_type": "migration_agent"})
    total_educators = db["users"].count_documents({"user_type": "education_provider"})

    st.write(f"Total Users: {total_users}")
    st.write(f"Total Prospective Migrants: {total_migrants}")
    st.write(f"Total Migration Agents: {total_agents}")
    st.write(f"Total Education Providers: {total_educators}")

    # Section 2: Saved Recommendations Overview
    st.subheader("Saved Recommendations Overview")
    saved_recommendations = db["saved_recommendations"].aggregate([
        {"$unwind": "$saved_recommendations"},
        {"$group": {"_id": "$saved_recommendations.pathway_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    saved_recs_list = []
    for record in saved_recommendations:
        pathway = db["pr_pathways"].find_one({"_id": ObjectId(record["_id"])})
        if pathway:
            saved_recs_list.append({
                "pathway_name": pathway["pathway_name"],
                "times_saved": record["count"]
            })

    saved_recs_df = pd.DataFrame(saved_recs_list)
    if not saved_recs_df.empty:
        st.write("Top 10 Most Saved Pathways:")
        st.table(saved_recs_df)
    else:
        st.write("No saved recommendation data available.")

    # Section 3: Agent Feedback Overview
    st.subheader("Agent Feedback Overview")
    feedback_stats = db["agent_feedback"].aggregate([
        {"$group": {"_id": "$pathway_id",
                    "avg_accuracy": {"$avg": "$accuracy"},
                    "avg_feasibility": {"$avg": "$feasibility"},
                    "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    feedback_list = []
    for feedback in feedback_stats:
        pathway = db["pr_pathways"].find_one({"_id": ObjectId(feedback["_id"])})
        if pathway:
            feedback_list.append({
                "pathway_name": pathway["pathway_name"],
                "avg_accuracy": feedback["avg_accuracy"],
                "avg_feasibility": feedback["avg_feasibility"],
                "feedback_count": feedback["count"]
            })

    feedback_df = pd.DataFrame(feedback_list)
    if not feedback_df.empty:
        st.write("Top 10 Pathways by Agent Feedback:")
        st.table(feedback_df)
    else:
        st.write("No agent feedback data available.")

    # Section 4: User Trends - Locations and Courses
    st.subheader("User Trends - Preferred Locations and Courses")

    # Location trends
    location_trends = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},
        {"$unwind": "$profile.preferences.location_preference"},
        {"$group": {"_id": "$profile.preferences.location_preference", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    location_list = []
    for location in location_trends:
        location_list.append({
            "location": location["_id"],
            "user_count": location["count"]
        })

    location_df = pd.DataFrame(location_list)
    if not location_df.empty:
        st.write("Top 10 Preferred Locations by Migrants:")
        st.table(location_df)
    else:
        st.write("No location preference data available.")

    # Course trends
    course_trends = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},
        {"$unwind": "$profile.education"},
        {"$group": {"_id": "$profile.education.degree_or_course_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    course_list = []
    for course in course_trends:
        course_list.append({
            "course_name": course["_id"],
            "user_count": course["count"]
        })

    course_df = pd.DataFrame(course_list)
    if not course_df.empty:
        st.write("Top 10 Courses Taken by Migrants:")
        st.table(course_df)
    else:
        st.write("No course data available.")

    # Section 5: PR Pathway Trends
    st.subheader("PR Pathway Trends")
    pathway_trends = db["pr_pathways"].aggregate([
        {"$group": {"_id": "$pathway_name", "total_usage": {"$sum": 1}}},
        {"$sort": {"total_usage": -1}},
        {"$limit": 10}
    ])

    pathway_list = []
    for pathway in pathway_trends:
        pathway_list.append({
            "pathway_name": pathway["_id"],
            "total_usage": pathway["total_usage"]
        })

    pathway_df = pd.DataFrame(pathway_list)
    if not pathway_df.empty:
        st.write("Top 10 Most Popular PR Pathways:")
        st.table(pathway_df)
    else:
        st.write("No PR pathway data available.")

    # Section 6: User Sign-up Trends
    st.subheader("User Sign-up Trends Over Time")
    signup_trends = db["users"].aggregate([
        {"$group": {"_id": {"year": {"$year": "$created_at"}, "month": {"$month": "$created_at"}},
                    "count": {"$sum": 1}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ])

    signup_list = []
    for signup in signup_trends:
        signup_list.append({
            "year": signup["_id"]["year"],
            "month": signup["_id"]["month"],
            "user_count": signup["count"]
        })

    signup_df = pd.DataFrame(signup_list)
    if not signup_df.empty:
        st.write("User Sign-up Trends Over Time:")
        st.table(signup_df)
    else:
        st.write("No sign-up data available.")


# Call this function to generate and display the admin report
def admin_report_page(db):
    with st.spinner("Generating admin report..."):
        generate_admin_report(db)
