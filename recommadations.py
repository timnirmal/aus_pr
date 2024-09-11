import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId  # Import ObjectId
import os
from dotenv import load_dotenv
import streamlit as st

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
    normalized_cost = normalize(cost, 0, 50000)
    normalized_duration = normalize(duration, 0, 60)

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
        pathway_courses = [course for course in pathway['recommended_courses']]  # Course IDs or names
        course_completion = calculate_course_completion(user_data['completed_courses'], pathway_courses)

        # Use the new fields for difficulty, success rate, cost, and duration
        success_rate = pathway.get('success_rate', 0)
        difficulty_level = pathway.get('difficulty_level', 10)
        cost = pathway.get('estimated_cost', 100000)  # Default high cost
        duration = pathway.get('estimated_duration', 60)  # Default long duration

        # Calculate total score for the pathway
        total_score = calculate_total_score(skill_match, experience_match, location_match, pr_points_match,
                                            course_completion, difficulty_level, success_rate, cost, duration, algorithm_parameters)

        # Categorize based on total score
        if total_score >= 80:
            recommendations['fully_qualified'].append({
                "pathway_name": pathway['pathway_name'],
                "score": total_score,
                "cost": pathway['estimated_cost'],
                "duration": pathway['estimated_duration'],
                "success_rate": pathway['success_rate'],
                "difficulty_level": pathway['difficulty_level']
            })
        elif total_score >= 40:
            recommendations['partially_qualified'].append({
                "pathway_name": pathway['pathway_name'],
                "score": total_score,
                "cost": pathway['estimated_cost'],
                "duration": pathway['estimated_duration'],
                "success_rate": pathway['success_rate'],
                "difficulty_level": pathway['difficulty_level']
            })
        else:
            recommendations['potential_interest'].append({
                "pathway_name": pathway['pathway_name'],
                "score": total_score,
                "cost": pathway['estimated_cost'],
                "duration": pathway['estimated_duration'],
                "success_rate": pathway['success_rate'],
                "difficulty_level": pathway['difficulty_level']
            })

    return recommendations


def recommend_pr_pathways(user, db):
    """Main recommendation function."""
    # Fetch user and pathway data
    user_data = fetch_user_data(user["_id"], db)
    pathways = fetch_pr_pathways(db)
    algorithm_parameters = fetch_algorithm_parameters(db)

    recommendations = rank_and_categorize_pathways(user_data, pathways, algorithm_parameters)

    return recommendations


def show_recommendations(recommendations):
    """Display recommendations in a user-friendly format using Streamlit."""
    for category, paths in recommendations.items():
        st.subheader(f"{category.upper()} PATHWAYS:")

        if paths:
            # Convert the list of pathways into a DataFrame for easier display
            df = pd.DataFrame(paths)
            df_display = df[['pathway_name', 'score', 'cost', 'duration', 'success_rate', 'difficulty_level']]

            # Display the DataFrame as a table
            st.table(df_display)
        else:
            st.write(f"No {category.lower()} pathways found.")