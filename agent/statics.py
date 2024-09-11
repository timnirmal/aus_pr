import pandas as pd
import streamlit as st


# Function to show migration agent statistics and analysis
def show_migration_agent_statistics(db):
    st.subheader("Migration Agent Statistics and Analysis")

    # Top PR Pathways (most saved by prospective migrants)
    st.write("Top PR Pathways:")
    pathway_stats = db["saved_recommendations"].aggregate([
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$match": {"user_info.user_type": "prospective_migrant"}},  # Only prospective migrants
        {"$unwind": "$saved_recommendations"},  # Deconstruct saved_recommendations array
        {"$group": {"_id": "$saved_recommendations.pathway_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    pathway_stats_list = []
    for stat in pathway_stats:
        pathway = db["pr_pathways"].find_one({"_id": stat["_id"]})
        if pathway:
            pathway_stats_list.append({
                "pathway_name": pathway.get("pathway_name", "Unknown Pathway"),
                "times_saved": stat["count"]
            })

    pathway_stats_df = pd.DataFrame(pathway_stats_list)
    if not pathway_stats_df.empty:
        st.table(pathway_stats_df)
    else:
        st.write("No pathway statistics available.")

    # Top Skills among prospective migrants
    st.write("Top Skills:")
    skill_stats = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},
        {"$unwind": "$profile.skills"},  # Unwind skills
        {"$group": {"_id": "$profile.skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])

    skill_stats_list = []
    for stat in skill_stats:
        skill_stats_list.append({
            "skill": stat["_id"],
            "user_count": stat["count"]
        })

    skill_stats_df = pd.DataFrame(skill_stats_list)
    if not skill_stats_df.empty:
        st.table(skill_stats_df)
    else:
        st.write("No skill data available.")

    # Top Preferred Locations for Migration
    st.write("Top Preferred Locations:")
    location_pref_stats = db["users"].aggregate([
        {"$match": {"user_type": "prospective_migrant"}},
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

    # Cost and Duration Analysis
    st.write("Cost and Duration Analysis (Average for Saved Pathways):")
    cost_duration_stats = db["saved_recommendations"].aggregate([
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$match": {"user_info.user_type": "prospective_migrant"}},
        {"$unwind": "$saved_recommendations"},  # Unwind saved_recommendations
        {"$lookup": {
            "from": "pr_pathways",
            "localField": "saved_recommendations.pathway_id",
            "foreignField": "_id",
            "as": "pathway_details"
        }},
        {"$unwind": "$pathway_details"},  # Unwind pathway details
        {"$group": {
            "_id": None,
            "avg_cost": {"$avg": "$pathway_details.estimated_cost"},
            "avg_duration": {"$avg": "$pathway_details.estimated_duration"}
        }}
    ])

    cost_duration_stats_list = []
    for stat in cost_duration_stats:
        cost_duration_stats_list.append({
            "average_cost": stat["avg_cost"],
            "average_duration": stat["avg_duration"]
        })

    cost_duration_df = pd.DataFrame(cost_duration_stats_list)
    if not cost_duration_df.empty:
        st.table(cost_duration_df)
    else:
        st.write("No cost and duration data available.")


# Combine all insights into one function
def show_full_migration_agent_statistics(db):
    show_migration_agent_statistics(db)
