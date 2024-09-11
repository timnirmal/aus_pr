from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId  # Import ObjectId
import os
from dotenv import load_dotenv

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
                          difficulty_level, success_rate, cost, duration):
    """Calculate the total score for a pathway based on various factors, with enhanced range control."""

    # Normalize cost and duration to a percentage (assuming max cost is 50,000 and max duration is 60 months)
    normalized_cost = normalize(cost, 0, 50000)  # Assume the max cost is 50,000
    normalized_duration = normalize(duration, 0, 60)  # Assume the max duration is 60 months

    # Apply penalties for lower skill match, experience match, and PR points match
    skill_penalty = (100 - skill_match) * 0.05  # Penalty for skill match less than 100%
    experience_penalty = (100 - experience_match) * 0.05  # Penalty for less experience
    pr_points_penalty = (100 - pr_points_match) * 0.05  # Penalty for fewer PR points

    # Calculate the total score with increased weight for cost and duration
    total_score = (
        (skill_match * 0.25) +  # Higher weight for skills
        (experience_match * 0.2) +  # Experience match is important
        (course_completion * 0.15) +  # Completed courses give extra credit
        (location_match * 0.1) +  # Location preferences have a smaller weight
        (pr_points_match * 0.1) +  # PR points match holds some weight
        (success_rate * 0.1) +  # Success rate holds a high weight
        ((100 - difficulty_level) * 0.05) +  # Lower difficulty will slightly increase the score
        ((100 - normalized_cost) * 0.05) +  # Lower normalized cost now has more weight
        ((100 - normalized_duration) * 0.05)  # Shorter normalized duration now has more weight
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


def rank_and_categorize_pathways(user_data, pathways):
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
                                            course_completion, difficulty_level, success_rate, cost, duration)

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
    user_data = fetch_user_data(user["_id"], db)  # Assume a function fetch_user_data exists
    pathways = fetch_pr_pathways(db)  # Assume a function fetch_pr_pathways exists

    # Rank and categorize pathways based on user data
    recommendations = rank_and_categorize_pathways(user_data, pathways)

    # Print or return recommendations as a list of dictionaries
    return recommendations


# Test the recommendation function
user_id = "66dfe4fc2315f2dbfb3d04d3"  # Replace with your actual user_id
recommendations = recommend_pr_pathways({"_id": ObjectId(user_id)}, db)

# Print the final recommendations
for category, paths in recommendations.items():
    print(f"\n{category.upper()} PATHWAYS:")
    for path in paths:
        print(path)
