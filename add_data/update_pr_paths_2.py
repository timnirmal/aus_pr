from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load MongoDB URI from environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(uri)
db = client["aus-pr"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Fetch the courses, skills, and locations from the database
courses_data = db["courses"].find()
courses = list(courses_data)

skills_data = db["skills"].find()
skills_dict = {skill["skill_name"]: skill["_id"] for skill in skills_data}

locations_data = db["locations"].find()
locations_dict = {loc["location_name"]: loc["_id"] for loc in locations_data}

# Ensure courses are found
if not courses:
    raise Exception("No courses found in the database. Please insert courses first.")

# Update PR Pathways - Adding new fields: difficulty_level, success_rate, estimated_cost, estimated_duration
pr_pathways_updates = [
    # Technology Pathways
    {
        "pathway_name": "IT Specialist Pathway",
        "update_data": {
            "difficulty_level": 5,  # Example difficulty level
            "success_rate": 85,  # Example success rate
            "estimated_cost": 15000,  # Example cost
            "estimated_duration": 36  # Example duration in months
        }
    },
    {
        "pathway_name": "Cybersecurity Specialist Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 80,
            "estimated_cost": 12000,
            "estimated_duration": 24
        }
    },
    {
        "pathway_name": "Data Science Pathway",
        "update_data": {
            "difficulty_level": 7,
            "success_rate": 75,
            "estimated_cost": 18000,
            "estimated_duration": 36
        }
    },
    # Engineering Pathways
    {
        "pathway_name": "Civil Engineering Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 70,
            "estimated_cost": 20000,
            "estimated_duration": 48
        }
    },
    {
        "pathway_name": "Electrical Engineering Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 70,
            "estimated_cost": 16000,
            "estimated_duration": 36
        }
    },
    # Business & Finance Pathways
    {
        "pathway_name": "Business Management Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 80,
            "estimated_cost": 14000,
            "estimated_duration": 36
        }
    },
    {
        "pathway_name": "Finance Specialist Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 85,
            "estimated_cost": 12000,
            "estimated_duration": 30
        }
    },
    {
        "pathway_name": "Marketing Specialist Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 75,
            "estimated_cost": 13000,
            "estimated_duration": 36
        }
    },
    # Healthcare Pathways
    {
        "pathway_name": "Nursing Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 90,
            "estimated_cost": 10000,
            "estimated_duration": 24
        }
    },
    {
        "pathway_name": "Healthcare Management Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 80,
            "estimated_cost": 15000,
            "estimated_duration": 36
        }
    },
    {
        "pathway_name": "Medical Doctor Pathway",
        "update_data": {
            "difficulty_level": 8,
            "success_rate": 65,
            "estimated_cost": 50000,
            "estimated_duration": 60
        }
    },
    # Design & Architecture Pathways
    {
        "pathway_name": "Graphic Design Pathway",
        "update_data": {
            "difficulty_level": 4,
            "success_rate": 75,
            "estimated_cost": 9000,
            "estimated_duration": 18
        }
    },
    {
        "pathway_name": "Architecture Pathway",
        "update_data": {
            "difficulty_level": 7,
            "success_rate": 70,
            "estimated_cost": 25000,
            "estimated_duration": 48
        }
    },
    # Education Pathways
    {
        "pathway_name": "Education Specialist Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 85,
            "estimated_cost": 12000,
            "estimated_duration": 36
        }
    },
    # Science & Environmental Pathways
    {
        "pathway_name": "Environmental Science Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 80,
            "estimated_cost": 14000,
            "estimated_duration": 36
        }
    },
    {
        "pathway_name": "Biotechnology Pathway",
        "update_data": {
            "difficulty_level": 6,
            "success_rate": 75,
            "estimated_cost": 16000,
            "estimated_duration": 36
        }
    },
    # Law & Legal Pathways
    {
        "pathway_name": "Law Specialist Pathway",
        "update_data": {
            "difficulty_level": 7,
            "success_rate": 70,
            "estimated_cost": 20000,
            "estimated_duration": 48
        }
    },
    # Miscellaneous
    {
        "pathway_name": "Project Management Pathway",
        "update_data": {
            "difficulty_level": 5,
            "success_rate": 80,
            "estimated_cost": 12000,
            "estimated_duration": 36
        }
    },
    {
        "pathway_name": "Hospitality Management Pathway",
        "update_data": {
            "difficulty_level": 4,
            "success_rate": 85,
            "estimated_cost": 10000,
            "estimated_duration": 24
        }
    }
]

# Iterate over each pathway and update it
for pathway_update in pr_pathways_updates:
    pathway_name = pathway_update["pathway_name"]
    update_data = pathway_update["update_data"]

    # Update the PR pathway by matching the pathway_name
    result = db["pr_pathways"].update_many(
        {"pathway_name": pathway_name},
        {"$set": update_data}
    )
    print(f"Updated {result.matched_count} document(s) for pathway '{pathway_name}'")

print("All PR pathways have been successfully updated.")
