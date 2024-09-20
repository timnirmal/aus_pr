import pandas as pd
import streamlit as st

hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)


# Function to aggregate and display anonymized interest statistics for "prospective_migrant" users
def show_anonymized_interest_statistics(db):
    st.subheader("Anonymized Interest Statistics")

    # Aggregate statistics on saved recommendations, filtering by user_type = "prospective_migrant"
    interest_stats = db["saved_recommendations"].aggregate([
        {"$lookup": {
            "from": "users",  # Join with the users collection
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$match": {"user_info.user_type": "prospective_migrant"}},  # Only count prospective migrants
        {"$unwind": "$saved_recommendations"},  # Deconstruct saved_recommendations array
        {"$group": {"_id": "$saved_recommendations.pathway_id", "count": {"$sum": 1}}},  # Group by pathway_id and count
        {"$sort": {"count": -1}},  # Sort by count in descending order
        {"$limit": 10}  # Limit to top 10
    ])

    # Prepare the data for display
    stats_list = []
    for stat in interest_stats:
        # Fetch the pathway details for each pathway_id
        pathway = db["pr_pathways"].find_one({"_id": stat["_id"]})
        if pathway:
            stats_list.append({
                "pathway_name": pathway.get("pathway_name", "Unknown Pathway"),
                "times_saved": stat["count"]
            })

    # Convert the list to a DataFrame for easier display
    stats_df = pd.DataFrame(stats_list)

    # Display the statistics in a table
    if not stats_df.empty:
        st.table(stats_df)
    else:
        st.write("No interest statistics available.")


# Function to fetch and aggregate user preferences, filtering by "prospective_migrant"
def aggregate_user_preferences(db):
    st.subheader("User Preferences Insights")

    # Location preferences (only prospective migrants)
    st.write("Top Location Preferences:")
    location_pref_stats = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},  # Only prospective migrants
        {"$unwind": "$profile.preferences.location_preference"},  # Unwind the location preferences
        {"$group": {"_id": "$profile.preferences.location_preference", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    location_stats_list = []
    for stat in location_pref_stats:
        location_stats_list.append({
            "location": stat["_id"],
            "user_count": stat["count"]
        })
    location_stats_df = pd.DataFrame(location_stats_list)

    if not location_stats_df.empty:
        st.table(location_stats_df)
    else:
        st.write("No location preference data available.")

    # Course preferences (only prospective migrants)
    st.write("Top Course Preferences:")
    course_pref_stats = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},  # Only prospective migrants
        {"$unwind": "$profile.preferences.study_preference"},  # Unwind the study preferences
        {"$group": {"_id": "$profile.preferences.study_preference", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    course_stats_list = []
    for stat in course_pref_stats:
        course_stats_list.append({
            "course": stat["_id"],
            "user_count": stat["count"]
        })
    course_stats_df = pd.DataFrame(course_stats_list)

    if not course_stats_df.empty:
        st.table(course_stats_df)
    else:
        st.write("No course preference data available.")

    # Institution preferences (only prospective migrants)
    st.write("Top Institution Preferences:")
    institution_pref_stats = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},  # Only prospective migrants
        {"$unwind": "$profile.preferences.study_preference"},  # Unwind the study preferences
        {"$group": {"_id": "$profile.preferences.study_preference", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    institution_stats_list = []
    for stat in institution_pref_stats:
        institution_stats_list.append({
            "institution": stat["_id"].split(" - ")[0],  # Extract institution name from preference string
            "user_count": stat["count"]
        })
    institution_stats_df = pd.DataFrame(institution_stats_list)

    if not institution_stats_df.empty:
        st.table(institution_stats_df)
    else:
        st.write("No institution preference data available.")


# Combine all insights into one function
def show_full_anonymized_statistics(db):
    show_anonymized_interest_statistics(db)
    aggregate_user_preferences(db)
