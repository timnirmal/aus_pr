import os
from datetime import datetime

import pandas as pd
import streamlit as st
from bson import ObjectId  # Import ObjectId
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
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

hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)


# Function to fetch user data
def fetch_user_data(user_id, db):
    print(user_id)
    # Convert user_id to ObjectId
    user = db['users'].find_one({"_id": ObjectId(user_id)})

    # Check if user exists
    if user is None:
        raise ValueError(f"No user found with _id: {user_id}")

    return {
        "skills": user.get('skills', []),
        "experience_years": sum([employment['years_in_current_role'] for employment in user.get('employment', [])]),
        "completed_courses": [education['degree_or_course_name'] for education in user.get('education', [])],
        "preferred_locations": user.get('preferences', {}).get('location_preference', []),
        "pr_points": user.get('pr_points', 0)
    }


# Function to fetch the name of courses, institutions, locations, and skills
def fetch_name(collection, object_ids):
    if not object_ids:
        return []
    results = db[collection].find({"_id": {"$in": object_ids}})
    return [result.get('course_name' if collection == 'courses' else
                       'institution_name' if collection == 'institutions' else
                       'location_name' if collection == 'locations' else 'skill_name', 'Unknown')
            for result in results]


# Function to fetch algorithm parameters
def fetch_algorithm_parameters(db):
    parameters = db["algorithm_parameters"].find_one({"_id": "default"})
    if parameters:
        return parameters
    else:
        # Default values if no parameters are set
        return {
            "skill_weight": 0.25,
            "experience_weight": 0.2,
            "course_completion_weight": 0.15,
            "location_weight": 0.1,
            "pr_points_weight": 0.1,
            "success_rate_weight": 0.1,
            "difficulty_weight": 0.05,
            "cost_weight": 0.05,
            "duration_weight": 0.05
        }


# Function to check if the user has completed recommended courses
def calculate_course_completion(user_courses, pathway_courses):
    """Check if user has completed any of the recommended courses."""
    matching_courses = set(user_courses).intersection(set(pathway_courses))
    match_percentage = len(matching_courses) / len(pathway_courses) * 100 if pathway_courses else 0
    return match_percentage


# Function to normalize values between 0 and 100
def normalize(value, min_value, max_value):
    """Normalize the value between 0 and 100 based on its min and max range."""
    return (value - min_value) / (max_value - min_value) * 100


# Updated total score calculation
def calculate_total_score(skill_match, experience_match, location_match, pr_points_match, course_completion,
                          difficulty_level, success_rate, cost, duration, algorithm_parameters):
    """Calculate the total score using dynamic weights from the admin panel."""
    skill_weight = algorithm_parameters["skill_weight"]
    experience_weight = algorithm_parameters["experience_weight"]
    course_completion_weight = algorithm_parameters["course_completion_weight"]
    location_weight = algorithm_parameters["location_weight"]
    pr_points_weight = algorithm_parameters["pr_points_weight"]
    success_rate_weight = algorithm_parameters["success_rate_weight"]
    difficulty_weight = algorithm_parameters["difficulty_weight"]
    cost_weight = algorithm_parameters["cost_weight"]
    duration_weight = algorithm_parameters["duration_weight"]

    # Normalize cost and duration to a percentage
    normalized_cost = (cost - 0) / (50000 - 0) * 100
    normalized_duration = (duration - 0) / (60 - 0) * 100
    # normalized_cost = normalize(cost, 0, 50000)
    # normalized_duration = normalize(duration, 0, 60)

    # Apply penalties for lower skill match, experience match, and PR points match
    skill_penalty = (100 - skill_match) * 0.05  # Penalty for skill match less than 100%
    experience_penalty = (100 - experience_match) * 0.05  # Penalty for less experience
    pr_points_penalty = (100 - pr_points_match) * 0.05  # Penalty for fewer PR points

    # Calculate the total score with increased weight for cost and duration
    total_score = (
            (skill_match * skill_weight) +
            (experience_match * experience_weight) +
            (course_completion * course_completion_weight) +
            (location_match * location_weight) +
            (pr_points_match * pr_points_weight) +
            (success_rate * success_rate_weight) +
            ((100 - difficulty_level) * difficulty_weight) +
            ((100 - normalized_cost) * cost_weight) +
            ((100 - normalized_duration) * duration_weight)
    )

    # # Apply penalties
    # total_score = total_score - skill_penalty - experience_penalty - pr_points_penalty

    # Ensure the score is between 0 and 100
    total_score = max(0, min(total_score, 100))

    return total_score


# Function to fetch PR pathways
def fetch_pr_pathways(db):
    pathways = db['pr_pathways'].find()
    return list(pathways)


def calculate_skill_match(user_skills, pathway_skills):
    """Calculate how well the user's skills match the pathway's required skills."""
    matching_skills = set(user_skills).intersection(set(pathway_skills))
    match_percentage = len(matching_skills) / len(pathway_skills) * 100 if pathway_skills else 0
    return match_percentage


def calculate_experience_match(user_experience, required_experience):
    """Calculate how well the user's experience matches the pathway's required experience."""
    if required_experience == 0:  # Handle case where no experience is required
        return 100
    return (min(user_experience, required_experience) / required_experience) * 100


def calculate_location_match(user_locations, pathway_locations):
    """Calculate how well the user's preferred locations match the pathway's preferred locations."""
    matching_locations = set(user_locations).intersection(set(pathway_locations))
    match_percentage = len(matching_locations) / len(pathway_locations) * 100 if pathway_locations else 0
    return match_percentage


def calculate_pr_points_match(user_points, pr_points_threshold):
    """Calculate how close the user's PR points are to the pathway's threshold."""
    if pr_points_threshold == 0:  # Handle case where no PR points threshold is set
        return 100
    return (min(user_points, pr_points_threshold) / pr_points_threshold) * 100


def rank_and_categorize_pathways(user_data, pathways, algorithm_parameters):
    """Rank and categorize pathways into fully qualified, partially qualified, and potential interest categories."""
    recommendations = {
        "fully_qualified": [],
        "partially_qualified": [],
        "potential_interest": []
    }

    for pathway in pathways:
        # Calculate match scores for skills, experience, location, and PR points
        skill_match = calculate_skill_match(user_data['skills'], pathway['required_skills'])
        experience_match = calculate_experience_match(user_data['experience_years'],
                                                      pathway['required_experience_years'])
        location_match = calculate_location_match(user_data['preferred_locations'], pathway['preferred_locations'])
        pr_points_match = calculate_pr_points_match(user_data['pr_points'], pathway['pr_points_threshold'])

        # Check if the user has completed recommended courses for this pathway
        pathway_courses = pathway['recommended_courses']  # Course IDs or names
        course_completion = calculate_course_completion(user_data['completed_courses'], pathway_courses)

        # Fetch names of required entities (skills, courses, locations)
        skill_names = fetch_name('skills', pathway['required_skills'])
        course_names = fetch_name('courses', pathway['recommended_courses'])
        location_names = fetch_name('locations', pathway.get('preferred_locations', []))

        # Use the new fields for difficulty, success rate, cost, and duration
        success_rate = pathway.get('success_rate', 0)
        difficulty_level = pathway.get('difficulty_level', 10)
        cost = pathway.get('estimated_cost', 100000)  # Default high cost
        duration = pathway.get('estimated_duration', 60)  # Default long duration

        # Calculate total score for the pathway
        total_score = calculate_total_score(skill_match, experience_match, location_match, pr_points_match,
                                            course_completion, difficulty_level, success_rate, cost, duration,
                                            algorithm_parameters)

        # Collect all the data for each pathway
        pathway_info = {
            "pathway_id": str(pathway['_id']),  # Convert ObjectId to string
            "pathway_name": pathway['pathway_name'],
            "score": total_score,
            "cost": cost,
            "duration": duration,
            "success_rate": success_rate,
            "difficulty_level": difficulty_level,
            "required_skills": skill_names,
            "required_experience_years": pathway['required_experience_years'],
            "pr_points_threshold": pathway['pr_points_threshold'],
            "recommended_courses": course_names,
            "locations": location_names
        }

        # Categorize based on total score
        if total_score >= 80:
            recommendations['fully_qualified'].append(pathway_info)
        elif total_score >= 40:
            recommendations['partially_qualified'].append(pathway_info)
        else:
            recommendations['potential_interest'].append(pathway_info)

    return recommendations


def recommend_pr_pathways(user, db):
    """Main recommendation function."""
    # Fetch user and pathway data
    print("Fetching user data...")
    user_data = fetch_user_data(user["_id"], db)
    pathways = fetch_pr_pathways(db)
    print("Fetching algorithm parameters...")
    algorithm_parameters = fetch_algorithm_parameters(db)

    print("Calculating pathway recommendations...")
    recommendations = rank_and_categorize_pathways(user_data, pathways, algorithm_parameters)
    print("Recommendations calculated successfully!")

    print(recommendations)

    return recommendations


# Function to save a preferred pathway to the database
# Function to save a preferred pathway to the database
def save_preferred_pathway(user_id, pathway, db):
    # Convert Pandas Series to dictionary if necessary
    if isinstance(pathway, pd.Series):
        pathway = pathway.to_dict()

    # Check if the user already has saved recommendations
    existing_record = db["saved_recommendations"].find_one({"user_id": ObjectId(user_id)})

    # Pathway details to be saved
    saved_recommendation = {
        "pathway_id": ObjectId(pathway['pathway_id']),
        "saved_at": datetime.utcnow(),
        "pathway_details": pathway  # Store the entire pathway details
    }

    print(saved_recommendation)

    # If the user has saved recommendations, append the new one
    if existing_record:
        print("Existing record found...")
        db["saved_recommendations"].update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"saved_recommendations": saved_recommendation}}
        )
    else:
        print("No existing record found...")
        # If no record exists for this user, create a new one
        db["saved_recommendations"].insert_one({
            "user_id": ObjectId(user_id),
            "saved_recommendations": [saved_recommendation]
        })

    return "Recommendation saved successfully!"


# Function to fetch saved recommendations
def fetch_saved_recommendations(user_id, db):
    saved = db["saved_recommendations"].find_one({"user_id": ObjectId(user_id)})
    return saved["saved_recommendations"] if saved else []


# Function to show recommendations with a save button
def show_recommendations(recommendations, user, db, rec_saved):
    """Display recommendations in a user-friendly format using Streamlit."""
    st.subheader("New Recommendations")

    if len(rec_saved) > 0:
        saved_pathway_ids = rec_saved['pathway_id']
        # convert to list
        saved_pathway_ids = saved_pathway_ids.tolist()
        # st.write(saved_pathway_ids)
    else:
        saved_pathway_ids = []

    for category, paths in recommendations.items():
        st.subheader(f"{category.upper()} PATHWAYS:")

        if paths:
            # Prepare the DataFrame with all the fields
            df = pd.DataFrame(paths)

            # st.write(df.columns)

            # Adjust the DataFrame display to remove the index and the pathway_id column
            df_display = df[['pathway_name', 'score', 'cost', 'duration', 'success_rate',
                             'difficulty_level', 'required_skills', 'required_experience_years',
                             'pr_points_threshold', 'recommended_courses', 'locations']]

            # Display the DataFrame without index
            st.table(df_display.reset_index(drop=True))

            # Save button for each recommendation, only show if the pathway is not already saved
            for i, path in df.iterrows():
                if path['pathway_id'] not in saved_pathway_ids:
                    if st.button(f"Save {path['pathway_name']}", key=f"save_{path['pathway_id']}"):
                        save_message = save_preferred_pathway(user["_id"], path, db)
                        st.success(save_message)
                        st.rerun()  # Refresh the page to show the saved recommendation
        else:
            st.write(f"No {category.lower()} pathways found.")


# Function to remove a saved pathway from the database
def remove_saved_pathway(user_id, pathway_id, db):
    # Remove the pathway from the user's saved recommendations
    db["saved_recommendations"].update_one(
        {"user_id": ObjectId(user_id)},
        {"$pull": {"saved_recommendations": {"pathway_id": ObjectId(pathway_id)}}}
    )
    return "Recommendation removed successfully!"


# Function to display saved recommendations
def show_saved_recommendations(user, db):
    st.subheader("Saved Pathways")

    # Fetch saved recommendations from the database
    saved_paths = fetch_saved_recommendations(user["_id"], db)

    if saved_paths:
        # Prepare the DataFrame for displaying saved recommendations
        saved_df = pd.DataFrame([path['pathway_details'] for path in saved_paths])

        # Adjust the DataFrame to show important fields
        saved_df_display = saved_df[['pathway_name', 'cost', 'duration', 'success_rate', 'difficulty_level',
                                     'required_skills', 'recommended_courses', 'locations', 'pr_points_threshold']]

        # # Display the saved recommendations as a table
        # st.table(saved_df_display.style.hide(axis="index"))
        # st.markdown(saved_df_display.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        # Display a static table
        st.table(saved_df_display)

        # Add "Remove" buttons for each saved recommendation
        for i, path in saved_df.iterrows():
            if st.button(f"Remove {path['pathway_name']}", key=f"remove_{path['pathway_id']}"):
                remove_message = remove_saved_pathway(user["_id"], path['pathway_id'], db)
                st.success(remove_message)
                st.rerun()  # Refresh the page to reflect the removal

        return saved_df
    else:
        st.write("No saved pathways yet.")

        return pd.DataFrame()

# # Main function to handle the page logic
# def main(user, db):
#     st.title("PR Pathway Recommendations")
#
#
#
#     # Fetch and show new recommendations
#     recommendations = recommend_pr_pathways(user, db)
#     show_recommendations(recommendations, user, db)

# # Test the recommendation function
# user_id = "66dfe4fc2315f2dbfb3d04d3"  # Replace with your actual user_id
# recommendations = recommend_pr_pathways({"_id": ObjectId(user_id)}, db)
#
# # Print the final recommendations
# for category, paths in recommendations.items():
#     print(f"\n{category.upper()} PATHWAYS:")
#     for path in paths:
#         print(path)
