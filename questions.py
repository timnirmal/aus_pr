from datetime import datetime
import streamlit as st
from pymongo import MongoClient  # Assuming you're using pymongo for MongoDB

def update_profile(user, users_collection, db):
    st.subheader("Update Profile")
    print(user)

    profile = user.get('profile', {})

    # Profile fields
    new_first_name = st.text_input("First Name", profile.get('first_name', ''))
    new_last_name = st.text_input("Last Name", profile.get('last_name', ''))

    # Set a wider date range for the date input, defaulting to January 1, 2000, if no date is provided
    new_date_of_birth = st.date_input("Date of Birth",
                                      value=profile.get('date_of_birth', datetime(2000, 1, 1)),
                                      min_value=datetime(1950, 1, 1),
                                      max_value=datetime.now())

    # Convert the date to a datetime object to avoid MongoDB errors
    if new_date_of_birth:  # Ensure new_date_of_birth is not None
        new_date_of_birth_datetime = datetime.combine(new_date_of_birth, datetime.min.time())
    else:
        new_date_of_birth_datetime = None  # Or you can set a default value if required

    gender_options = ["Male", "Female", "Other"]
    new_gender = st.selectbox("Gender", gender_options,
                              index=gender_options.index(profile.get('gender', 'Other'))
                              if profile.get('gender', 'Other') in gender_options else 2)
    new_location = st.text_input("Current Location", profile.get('location', ''))

    # Nationalities list
    nationalities = [
        "Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Antiguan", "Argentine", "Armenian",
        "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", "Bangladeshi", "Barbadian", "Belarusian",
        "Belgian", "Belizean", "Beninese", "Bhutanese", "Bolivian", "Bosnian", "Botswanan", "Brazilian", "British",
        "Bruneian", "Bulgarian", "Burkinabe", "Burmese", "Burundian", "Cambodian", "Cameroonian", "Canadian",
        "Cape Verdean", "Central African", "Chadian", "Chilean", "Chinese", "Colombian", "Comoran", "Congolese",
        "Costa Rican", "Croatian", "Cuban", "Cypriot", "Czech", "Danish", "Djiboutian", "Dominican", "Dutch",
        "East Timorese", "Ecuadorean", "Egyptian", "Emirati", "Equatorial Guinean", "Eritrean", "Estonian", "Ethiopian",
        "Fijian", "Filipino", "Finnish", "French", "Gabonese", "Gambian", "Georgian", "German", "Ghanaian", "Greek",
        "Grenadian", "Guatemalan", "Guinean", "Guinea-Bissauan", "Guyanese", "Haitian", "Herzegovinian", "Honduran",
        "Hungarian", "Icelander", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Ivorian",
        "Jamaican", "Japanese", "Jordanian", "Kazakhstani", "Kenyan", "Kiribati", "Korean", "Kosovar", "Kuwaiti",
        "Kyrgyz", "Lao", "Latvian", "Lebanese", "Liberian", "Libyan", "Liechtensteiner", "Lithuanian", "Luxembourger",
        "Macedonian", "Malagasy", "Malawian", "Malaysian", "Maldivian", "Malian", "Maltese", "Marshallese",
        "Mauritanian", "Mauritian", "Mexican", "Micronesian", "Moldovan", "Monacan", "Mongolian", "Moroccan",
        "Mozambican", "Namibian", "Nauruan", "Nepalese", "New Zealander", "Nicaraguan", "Nigerien", "Nigerian",
        "Norwegian", "Omani", "Pakistani", "Palauan", "Panamanian", "Papua New Guinean", "Paraguayan", "Peruvian",
        "Polish", "Portuguese", "Qatari", "Romanian", "Russian", "Rwandan", "Saint Lucian", "Salvadoran", "Samoan",
        "San Marinese", "Sao Tomean", "Saudi", "Senegalese", "Serbian", "Seychellois", "Sierra Leonean", "Singaporean",
        "Slovakian", "Slovenian", "Solomon Islander", "Somali", "South African", "Spanish", "Sri Lankan", "Sudanese",
        "Surinamer", "Swazi", "Swedish", "Swiss", "Syrian", "Taiwanese", "Tajik", "Tanzanian", "Thai", "Togolese",
        "Tongan", "Trinidadian", "Tunisian", "Turkish", "Tuvaluan", "Ugandan", "Ukrainian", "Uruguayan", "Uzbek",
        "Vanuatuan", "Venezuelan", "Vietnamese", "Yemeni", "Zambian", "Zimbabwean"
    ]

    # Convert to lowercase if required
    nationalities_lowercase = [nationality.lower() for nationality in nationalities]

    # Nationality select box with default set to "Sri Lankan"
    new_nationality = st.selectbox("Nationality", nationalities_lowercase,
                                   index=nationalities_lowercase.index(profile.get('nationality', '').lower())
                                   if profile.get('nationality', '').lower() in nationalities_lowercase
                                   else nationalities_lowercase.index("sri lankan"))

    # Skills
    available_skills = [skill['skill_name'] for skill in db["skills"].find()]
    current_skills = profile.get('skills', [])
    new_skills = st.multiselect("Skills", available_skills, default=current_skills)

    # Years of experience
    new_experience_years = st.number_input("Years of Experience", value=profile.get('experience_years', 0), min_value=0)

    # English proficiency
    english_proficiency_options = ["Beginner", "Intermediate", "Advanced", "Native"]
    current_proficiency = profile.get('english_proficiency', 'Beginner')
    new_english_proficiency = st.selectbox("English Proficiency", english_proficiency_options,
                                           index=english_proficiency_options.index(current_proficiency)
                                           if current_proficiency in english_proficiency_options else 0)

    st.subheader("Preferences")

    # Fetch available locations and institutions from MongoDB
    location_options = [f"{loc['location_name']} - {loc['state']}" for loc in db["locations"].find()]
    study_preferences = [f"{inst['institution_name']} - {inst['location']}" for inst in db["institutions"].find()]

    # Preferences
    current_location_preferences = profile.get('preferences', {}).get('location_preference', [])
    current_study_preferences = profile.get('preferences', {}).get('study_preference', [])
    valid_location_preferences = [loc for loc in current_location_preferences if loc in location_options]
    valid_study_preferences = [study for study in current_study_preferences if study in study_preferences]

    new_location_preference = st.multiselect("Preferred Locations", location_options, default=valid_location_preferences)
    new_study_preference = st.multiselect("Study Preferences", study_preferences, default=valid_study_preferences)

    # Cost and duration limits
    new_cost_limit = st.number_input("Cost Limit", value=profile.get('preferences', {}).get('cost_limit', 0), min_value=0)
    new_duration_limit = st.number_input("Duration Limit (months)", value=profile.get('preferences', {}).get('duration_limit', 0), min_value=0)

    if st.button("Save Changes"):
        updates = {
            "profile": {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "date_of_birth": new_date_of_birth_datetime,  # Using datetime for MongoDB compatibility
                "gender": new_gender,
                "location": new_location,
                "nationality": new_nationality,
                "skills": new_skills,
                "experience_years": new_experience_years,
                "english_proficiency": new_english_proficiency,
                "preferences": {
                    "location_preference": new_location_preference,
                    "study_preference": new_study_preference,
                    "cost_limit": new_cost_limit,
                    "duration_limit": new_duration_limit
                }
            },
            "updated_at": datetime.utcnow()
        }

        # Update the user in the database
        users_collection.update_one({"_id": user['_id']}, {"$set": updates})
        st.success("Profile updated successfully")
