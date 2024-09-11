import os

from dotenv import load_dotenv
from pymongo import MongoClient

# Load MongoDB URI from environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(uri)
db = client["aus-pr"]
# show existing collections
print(db.list_collection_names())

institutions_collection = db["institutions"]
courses_collection = db["courses"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create 35 skills (added 5 more skills)
skills = [
    {"skill_name": "IT", "category": "Technology"},
    {"skill_name": "Software Development", "category": "Technology"},
    {"skill_name": "Data Science", "category": "Technology"},
    {"skill_name": "Cybersecurity", "category": "Technology"},
    {"skill_name": "Artificial Intelligence", "category": "Technology"},
    {"skill_name": "Civil Engineering", "category": "Engineering"},
    {"skill_name": "Mechanical Engineering", "category": "Engineering"},
    {"skill_name": "Electrical Engineering", "category": "Engineering"},
    {"skill_name": "Environmental Science", "category": "Science"},
    {"skill_name": "Biotechnology", "category": "Science"},
    {"skill_name": "Nursing", "category": "Healthcare"},
    {"skill_name": "Public Health", "category": "Healthcare"},
    {"skill_name": "Pharmacy", "category": "Healthcare"},
    {"skill_name": "Business Management", "category": "Business"},
    {"skill_name": "Finance", "category": "Business"},
    {"skill_name": "Marketing", "category": "Business"},
    {"skill_name": "Accounting", "category": "Business"},
    {"skill_name": "Graphic Design", "category": "Design"},
    {"skill_name": "Architecture", "category": "Architecture"},
    {"skill_name": "Interior Design", "category": "Design"},
    {"skill_name": "Education", "category": "Education"},
    {"skill_name": "Teaching", "category": "Education"},
    {"skill_name": "Law", "category": "Legal"},
    {"skill_name": "Human Resources", "category": "Business"},
    {"skill_name": "Supply Chain Management", "category": "Business"},
    {"skill_name": "Tourism Management", "category": "Business"},
    {"skill_name": "Event Management", "category": "Management"},
    {"skill_name": "Hospitality Management", "category": "Management"},
    {"skill_name": "Project Management", "category": "Business"},
    {"skill_name": "Urban Planning", "category": "Planning"},
    {"skill_name": "Medicine", "category": "Healthcare"},
    {"skill_name": "Dentistry", "category": "Healthcare"},
    {"skill_name": "Physiotherapy", "category": "Healthcare"},
    {"skill_name": "Veterinary Science", "category": "Healthcare"},
    {"skill_name": "Optometry", "category": "Healthcare"}
]

# Insert the skills into the skills collection
db["skills"].insert_many(skills)

# Create 20 main locations in Australia
locations = [
    {"location_name": "Sydney", "state": "New South Wales"},
    {"location_name": "Melbourne", "state": "Victoria"},
    {"location_name": "Brisbane", "state": "Queensland"},
    {"location_name": "Perth", "state": "Western Australia"},
    {"location_name": "Adelaide", "state": "South Australia"},
    {"location_name": "Canberra", "state": "Australian Capital Territory"},
    {"location_name": "Hobart", "state": "Tasmania"},
    {"location_name": "Darwin", "state": "Northern Territory"},
    {"location_name": "Gold Coast", "state": "Queensland"},
    {"location_name": "Newcastle", "state": "New South Wales"},
    {"location_name": "Wollongong", "state": "New South Wales"},
    {"location_name": "Geelong", "state": "Victoria"},
    {"location_name": "Sunshine Coast", "state": "Queensland"},
    {"location_name": "Cairns", "state": "Queensland"},
    {"location_name": "Townsville", "state": "Queensland"},
    {"location_name": "Toowoomba", "state": "Queensland"},
    {"location_name": "Ballarat", "state": "Victoria"},
    {"location_name": "Bendigo", "state": "Victoria"},
    {"location_name": "Launceston", "state": "Tasmania"},
    {"location_name": "Alice Springs", "state": "Northern Territory"}
]

# Insert the locations into the locations collection
db["locations"].insert_many(locations)

# Fetch the courses from the database
courses_data = db["courses"].find()
courses = list(courses_data)  # Convert to a list for easy access

# Ensure courses are found
if not courses:
    raise Exception("No courses found in the database. Please insert courses first.")

# Fetch the skills and locations from the database
skills_data = db["skills"].find()
skills_dict = {skill["skill_name"]: skill["_id"] for skill in skills_data}

locations_data = db["locations"].find()
locations_dict = {loc["location_name"]: loc["_id"] for loc in locations_data}

# Create 25 PR pathways (added 5 more pathways)
from datetime import datetime

pr_pathways = [
    # Technology Pathways
    {
        "pathway_name": "IT Specialist Pathway",
        "required_skills": [skills_dict["IT"], skills_dict["Software Development"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[0]["_id"], courses[1]["_id"]],  # Bachelor of IT, Master of Data Science
        "preferred_locations": [locations_dict["Sydney"], locations_dict["Melbourne"]],
        "pr_points_threshold": 70,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Cybersecurity Specialist Pathway",
        "required_skills": [skills_dict["Cybersecurity"], skills_dict["IT"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[16]["_id"]],  # Master of Cybersecurity
        "preferred_locations": [locations_dict["Sydney"]],
        "pr_points_threshold": 75,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Data Science Pathway",
        "required_skills": [skills_dict["Data Science"], skills_dict["Artificial Intelligence"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[1]["_id"]],  # Master of Data Science
        "preferred_locations": [locations_dict["Sydney"]],
        "pr_points_threshold": 70,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Engineering Pathways
    {
        "pathway_name": "Civil Engineering Pathway",
        "required_skills": [skills_dict["Civil Engineering"], skills_dict["Mechanical Engineering"]],
        "required_experience_years": 4,
        "recommended_courses": [courses[3]["_id"], courses[18]["_id"]],
        # Bachelor of Engineering, Master of Civil Engineering
        "preferred_locations": [locations_dict["Brisbane"], locations_dict["Sydney"]],
        "pr_points_threshold": 70,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Electrical Engineering Pathway",
        "required_skills": [skills_dict["Electrical Engineering"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[0]["_id"]],  # Bachelor of IT
        "preferred_locations": [locations_dict["Perth"]],
        "pr_points_threshold": 65,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },

    # Business & Finance Pathways
    {
        "pathway_name": "Business Management Pathway",
        "required_skills": [skills_dict["Business Management"], skills_dict["Finance"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[4]["_id"], courses[14]["_id"]],
        # Master of Business Administration, Master of Marketing
        "preferred_locations": [locations_dict["Brisbane"], locations_dict["Melbourne"]],
        "pr_points_threshold": 75,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Finance Specialist Pathway",
        "required_skills": [skills_dict["Finance"], skills_dict["Accounting"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[6]["_id"], courses[16]["_id"]],
        # Bachelor of Accounting, Master of Cybersecurity
        "preferred_locations": [locations_dict["Sydney"]],
        "pr_points_threshold": 65,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Marketing Specialist Pathway",
        "required_skills": [skills_dict["Marketing"], skills_dict["Business Management"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[13]["_id"], courses[4]["_id"]],
        # Master of Marketing, Master of Business Administration
        "preferred_locations": [locations_dict["Melbourne"], locations_dict["Brisbane"]],
        "pr_points_threshold": 70,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Healthcare Pathways
    {
        "pathway_name": "Nursing Pathway",
        "required_skills": [skills_dict["Nursing"], skills_dict["Medicine"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[5]["_id"]],  # Graduate Diploma of Nursing
        "preferred_locations": [locations_dict["Perth"]],
        "pr_points_threshold": 65,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Healthcare Management Pathway",
        "required_skills": [skills_dict["Public Health"], skills_dict["Business Management"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[10]["_id"]],  # Master of Public Health
        "preferred_locations": [locations_dict["Melbourne"]],
        "pr_points_threshold": 65,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Medical Doctor Pathway",
        "required_skills": [skills_dict["Medicine"]],
        "required_experience_years": 5,
        "recommended_courses": [courses[10]["_id"]],  # Master of Public Health
        "preferred_locations": [locations_dict["Sydney"], locations_dict["Melbourne"]],
        "pr_points_threshold": 80,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Design & Architecture Pathways
    {
        "pathway_name": "Graphic Design Pathway",
        "required_skills": [skills_dict["Graphic Design"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[11]["_id"]],  # Diploma of Graphic Design
        "preferred_locations": [locations_dict["Melbourne"]],
        "pr_points_threshold": 60,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Architecture Pathway",
        "required_skills": [skills_dict["Architecture"]],
        "required_experience_years": 4,
        "recommended_courses": [courses[12]["_id"]],  # Bachelor of Architecture
        "preferred_locations": [locations_dict["Perth"]],
        "pr_points_threshold": 70,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Education Pathways
    {
        "pathway_name": "Education Specialist Pathway",
        "required_skills": [skills_dict["Teaching"], skills_dict["Education"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[18]["_id"]],  # Bachelor of Education
        "preferred_locations": [locations_dict["Melbourne"]],
        "pr_points_threshold": 60,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },

    # Science & Environmental Pathways
    {
        "pathway_name": "Environmental Science Pathway",
        "required_skills": [skills_dict["Environmental Science"], skills_dict["Biotechnology"]],
        "required_experience_years": 2,
        "recommended_courses": [courses[15]["_id"]],  # Bachelor of Environmental Science
        "preferred_locations": [locations_dict["Brisbane"]],
        "pr_points_threshold": 65,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Biotechnology Pathway",
        "required_skills": [skills_dict["Biotechnology"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[15]["_id"]],  # Bachelor of Environmental Science
        "preferred_locations": [locations_dict["Sydney"]],
        "pr_points_threshold": 65,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Law & Legal Pathways
    {
        "pathway_name": "Law Specialist Pathway",
        "required_skills": [skills_dict["Law"], skills_dict["Business Management"]],
        "required_experience_years": 4,
        "recommended_courses": [courses[4]["_id"]],  # Master of Business Administration
        "preferred_locations": [locations_dict["Melbourne"]],
        "pr_points_threshold": 75,
        "visa_subclass": "189",
        "processing_time": "12-16 months",
        "updated_at": datetime.utcnow()
    },

    # Miscellaneous
    {
        "pathway_name": "Project Management Pathway",
        "required_skills": [skills_dict["Project Management"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[6]["_id"]],  # Bachelor of Accounting
        "preferred_locations": [locations_dict["Sydney"]],
        "pr_points_threshold": 65,
        "visa_subclass": "190",
        "processing_time": "9-12 months",
        "updated_at": datetime.utcnow()
    },
    {
        "pathway_name": "Hospitality Management Pathway",
        "required_skills": [skills_dict["Hospitality Management"], skills_dict["Tourism Management"]],
        "required_experience_years": 3,
        "recommended_courses": [courses[9]["_id"], courses[10]["_id"]],
        # Diploma of Event Management, Diploma of Hospitality
        "preferred_locations": [locations_dict["Gold Coast"]],
        "pr_points_threshold": 70,
        "updated_at": datetime.utcnow()
    }
]

# Insert the PR pathways into the collection
db["pr_pathways"].insert_many(pr_pathways)
