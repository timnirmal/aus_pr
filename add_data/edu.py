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
courses_collection = db["courses"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


exit()

# Educator user ID
institution_id = ObjectId("66d584f58111222f4c4617fa")

# Sample course data from different universities in Australia
courses = [
    {
        "course_name": "Bachelor of Information Technology",
        "institution_id": str(institution_id),
        "location": "University of Sydney, Sydney",
        "cost": 40000.00,
        "duration": 36,  # duration in months
        "pr_points": 60,
        "updated_at": datetime.now(datetime.UTC)
    },
    {
        "course_name": "Master of Data Science",
        "institution_id": str(institution_id),
        "location": "University of Melbourne, Melbourne",
        "cost": 45000.00,
        "duration": 24,
        "pr_points": 70,
        "updated_at": datetime.now(datetime.UTC)
    },
    {
        "course_name": "Diploma of Software Development",
        "institution_id": str(institution_id),
        "location": "TAFE Queensland, Brisbane",
        "cost": 25000.00,
        "duration": 18,
        "pr_points": 50,
        "updated_at": datetime.now(datetime.UTC)
    },
    {
        "course_name": "Bachelor of Engineering (Civil)",
        "institution_id": str(institution_id),
        "location": "University of Western Australia, Perth",
        "cost": 42000.00,
        "duration": 48,
        "pr_points": 65,
        "updated_at": datetime.now(datetime.UTC)
    },
    {
        "course_name": "Master of Business Administration",
        "institution_id": str(institution_id),
        "location": "University of Queensland, Brisbane",
        "cost": 50000.00,
        "duration": 24,
        "pr_points": 75,
        "updated_at": datetime.now(datetime.UTC)
    },
    {
        "course_name": "Graduate Diploma of Nursing",
        "institution_id": str(institution_id),
        "location": "Flinders University, Adelaide",
        "cost": 32000.00,
        "duration": 12,
        "pr_points": 55,
        "updated_at": datetime.now(datetime.UTC)
    }
]

# Insert courses into the collection
result = courses_collection.insert_many(courses)

# Print the inserted course IDs
print("Courses inserted with the following IDs:")
for course_id in result.inserted_ids:
    print(course_id)
