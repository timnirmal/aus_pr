import os
from datetime import datetime

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

# Load MongoDB URI from environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(uri)
db = client["aus-pr"]
institutions_collection = db["institutions"]
courses_collection = db["courses"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# User IDs
user_ids = [
    ObjectId("66d7f08fd3a444e42e6e708a"),
    ObjectId("66d800c6d3a444e42e6e709c")
]

# Create institutions with the updated schema, distributing user_ids between institutions
# Add 5 institutions
institutions = [
    {
        "institution_name": "University of Sydney",
        "location": "Sydney",
        "user_id": ObjectId("66d7f08fd3a444e42e6e708a"),
        "updated_at": datetime.utcnow()
    },
    {
        "institution_name": "University of Melbourne",
        "location": "Melbourne",
        "user_id": ObjectId("66d7f08fd3a444e42e6e708a"),
        "updated_at": datetime.utcnow()
    },
    {
        "institution_name": "TAFE Queensland",
        "location": "Brisbane",
        "user_id": ObjectId("66d800c6d3a444e42e6e709c"),
        "updated_at": datetime.utcnow()
    },
    {
        "institution_name": "University of Western Australia",
        "location": "Perth",
        "user_id": ObjectId("66d800c6d3a444e42e6e709c"),
        "updated_at": datetime.utcnow()
    },
    {
        "institution_name": "RMIT University",
        "location": "Melbourne",
        "user_id": ObjectId("66d800c6d3a444e42e6e709c"),
        "updated_at": datetime.utcnow()
    }
]

# Insert the institutions into the collection
institution_results = institutions_collection.insert_many(institutions)
institution_ids = institution_results.inserted_ids

# Print the inserted institution IDs
print("Institutions inserted with the following IDs:")
for inst_id in institution_ids:
    print(inst_id)

# Sample course data from the newly inserted institutions
# Create 20 courses
courses = [
    {"course_name": "Bachelor of IT", "institution_id": institution_ids[0], "location": "Sydney", "cost": 40000,
     "duration": 36, "pr_points": 60, "capacity": 50, "start_date": datetime(2024, 3, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Data Science", "institution_id": institution_ids[0], "location": "Sydney", "cost": 45000,
     "duration": 24, "pr_points": 70, "capacity": 40, "start_date": datetime(2024, 6, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Diploma of Software Development", "institution_id": institution_ids[1], "location": "Melbourne",
     "cost": 25000, "duration": 18, "pr_points": 50, "capacity": 30, "start_date": datetime(2024, 9, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Engineering (Civil)", "institution_id": institution_ids[2], "location": "Brisbane",
     "cost": 42000, "duration": 48, "pr_points": 65, "capacity": 50, "start_date": datetime(2024, 1, 15),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Business Administration", "institution_id": institution_ids[2], "location": "Brisbane",
     "cost": 50000, "duration": 24, "pr_points": 75, "capacity": 35, "start_date": datetime(2024, 5, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Graduate Diploma of Nursing", "institution_id": institution_ids[3], "location": "Perth",
     "cost": 32000, "duration": 12, "pr_points": 55, "capacity": 40, "start_date": datetime(2024, 8, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Accounting", "institution_id": institution_ids[1], "location": "Melbourne",
     "cost": 35000, "duration": 36, "pr_points": 60, "capacity": 60, "start_date": datetime(2024, 2, 15),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Engineering", "institution_id": institution_ids[0], "location": "Sydney", "cost": 47000,
     "duration": 24, "pr_points": 70, "capacity": 45, "start_date": datetime(2024, 7, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Diploma of Hospitality", "institution_id": institution_ids[3], "location": "Perth", "cost": 28000,
     "duration": 18, "pr_points": 50, "capacity": 20, "start_date": datetime(2024, 10, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Science", "institution_id": institution_ids[1], "location": "Melbourne", "cost": 38000,
     "duration": 36, "pr_points": 65, "capacity": 70, "start_date": datetime(2024, 3, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Public Health", "institution_id": institution_ids[4], "location": "Melbourne",
     "cost": 40000, "duration": 24, "pr_points": 60, "capacity": 30, "start_date": datetime(2024, 4, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Diploma of Graphic Design", "institution_id": institution_ids[4], "location": "Melbourne",
     "cost": 26000, "duration": 18, "pr_points": 50, "capacity": 20, "start_date": datetime(2024, 9, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Architecture", "institution_id": institution_ids[3], "location": "Perth",
     "cost": 45000, "duration": 48, "pr_points": 65, "capacity": 40, "start_date": datetime(2024, 6, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Marketing", "institution_id": institution_ids[4], "location": "Melbourne", "cost": 50000,
     "duration": 24, "pr_points": 70, "capacity": 30, "start_date": datetime(2024, 5, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Environmental Science", "institution_id": institution_ids[2], "location": "Brisbane",
     "cost": 40000, "duration": 36, "pr_points": 60, "capacity": 50, "start_date": datetime(2024, 7, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Diploma of Finance", "institution_id": institution_ids[3], "location": "Perth", "cost": 27000,
     "duration": 18, "pr_points": 50, "capacity": 25, "start_date": datetime(2024, 8, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Cybersecurity", "institution_id": institution_ids[0], "location": "Sydney",
     "cost": 48000, "duration": 24, "pr_points": 75, "capacity": 35, "start_date": datetime(2024, 3, 1),
     "updated_at": datetime.utcnow()},
    {"course_name": "Bachelor of Education", "institution_id": institution_ids[4], "location": "Melbourne",
     "cost": 35000, "duration": 36, "pr_points": 60, "capacity": 45, "start_date": datetime(2024, 2, 15),
     "updated_at": datetime.utcnow()},
    {"course_name": "Master of Civil Engineering", "institution_id": institution_ids[2], "location": "Brisbane",
     "cost": 47000, "duration": 24, "pr_points": 70, "capacity": 40, "start_date": datetime(2024, 1, 15),
     "updated_at": datetime.utcnow()},
    {"course_name": "Diploma of Event Management", "institution_id": institution_ids[1], "location": "Melbourne",
     "cost": 29000, "duration": 18, "pr_points": 50, "capacity": 30, "start_date": datetime(2024, 10, 1),
     "updated_at": datetime.utcnow()}
]

# Insert the courses into the collection
result = courses_collection.insert_many(courses)

# Print the inserted course IDs
print("Courses inserted with the following IDs:")
for course_id in result.inserted_ids:
    print(course_id)

# # Create 10 PR pathways
# pr_pathways = [
#     {"pathway_name": "IT Specialist Pathway", "required_skills": ["IT", "Software Development"], "required_experience_years": 2, "recommended_courses": [courses[0]["_id"], courses[1]["_id"], courses[17]["_id"]], "preferred_locations": ["Sydney", "Melbourne"], "pr_points_threshold": 70, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Business Management Pathway", "required_skills": ["Business", "Management"], "required_experience_years": 3, "recommended_courses": [courses[4]["_id"], courses[14]["_id"], courses[19]["_id"]], "preferred_locations": ["Brisbane", "Perth"], "pr_points_threshold": 75, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Engineering Pathway", "required_skills": ["Civil Engineering", "Mechanical Engineering"], "required_experience_years": 4, "recommended_courses": [courses[3]["_id"], courses[18]["_id"], courses[7]["_id"]], "preferred_locations": ["Brisbane", "Sydney"], "pr_points_threshold": 70, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Healthcare Pathway", "required_skills": ["Healthcare", "Nursing"], "required_experience_years": 3, "recommended_courses": [courses[5]["_id"], courses[10]["_id"]], "preferred_locations": ["Perth", "Melbourne"], "pr_points_threshold": 65, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Finance Specialist Pathway", "required_skills": ["Finance", "Accounting"], "required_experience_years": 3, "recommended_courses": [courses[6]["_id"], courses[16]["_id"]], "preferred_locations": ["Melbourne", "Sydney"], "pr_points_threshold": 65, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Education Specialist Pathway", "required_skills": ["Teaching", "Education"], "required_experience_years": 2, "recommended_courses": [courses[18]["_id"]], "preferred_locations": ["Melbourne"], "pr_points_threshold": 60, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Environmental Science Pathway", "required_skills": ["Environmental Science"], "required_experience_years": 2, "recommended_courses": [courses[15]["_id"]], "preferred_locations": ["Brisbane"], "pr_points_threshold": 65, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Cybersecurity Specialist Pathway", "required_skills": ["IT", "Cybersecurity"], "required_experience_years": 2, "recommended_courses": [courses[16]["_id"], courses[1]["_id"]], "preferred_locations": ["Sydney"], "pr_points_threshold": 75, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Architecture Pathway", "required_skills": ["Architecture"], "required_experience_years": 4, "recommended_courses": [courses[12]["_id"]], "preferred_locations": ["Perth"], "pr_points_threshold": 70, "updated_at": datetime.utcnow()},
#     {"pathway_name": "Marketing Specialist Pathway", "required_skills": ["Marketing"], "required_experience_years": 3, "recommended_courses": [courses[13]["_id"], courses[4]["_id"]], "preferred_locations": ["Melbourne", "Brisbane"], "pr_points_threshold": 70, "updated_at": datetime.utcnow()}
# ]

# # Insert the PR pathways into the collection
# db["pr_pathways"].insert_many(pr_pathways)
