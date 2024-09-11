from datetime import datetime

import streamlit as st


def update_profile(user, users_collection, db):
    st.subheader("Update Profile")
    profile = user.get('profile', {})

    # Fetch available courses from the courses table
    available_courses = [course['course_name'] for course in db["courses"].find()]

    # Profile fields
    new_first_name = st.text_input("First Name", profile.get('first_name', ''))
    new_last_name = st.text_input("Last Name", profile.get('last_name', ''))

    # Set a wider date range for the date input, defaulting to January 1, 2000, if no date is provided
    new_date_of_birth = st.date_input("Date of Birth",
                                      value=profile.get('date_of_birth', datetime(2000, 1, 1)),
                                      min_value=datetime(1950, 1, 1),
                                      max_value=datetime.now())

    # Convert the date to a datetime object for MongoDB
    new_date_of_birth_datetime = datetime.combine(new_date_of_birth, datetime.min.time()) if new_date_of_birth else None

    # Gender
    gender_options = ["Male", "Female", "Other"]
    new_gender = st.selectbox("Gender", gender_options,
                              index=gender_options.index(profile.get('gender', 'Other'))
                              if profile.get('gender', 'Other') in gender_options else 2)

    # Current Location
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

    # Convert to lowercase
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

    # English proficiency
    english_proficiency_options = ["Beginner", "Intermediate", "Advanced", "Native"]
    current_proficiency = profile.get('english_proficiency', 'Beginner')
    new_english_proficiency = st.selectbox("English Proficiency", english_proficiency_options,
                                           index=english_proficiency_options.index(current_proficiency)
                                           if current_proficiency in english_proficiency_options else 0)

    st.divider()

    # Employment (Multiple Entries)
    employment_entries = profile.get('employment', [])
    employment_count = st.number_input("Number of Employment Entries", min_value=1,
                                       value=len(employment_entries) if len(employment_entries) > 0 else 1)

    new_employment = []
    for i in range(employment_count):
        st.write(f"Employment #{i + 1}")
        job_title = st.text_input(f"Job Title #{i + 1}",
                                  employment_entries[i].get('job_title', '') if i < len(employment_entries) else "")
        company = st.text_input(f"Company #{i + 1}",
                                employment_entries[i].get('company', '') if i < len(employment_entries) else "")
        years_in_role = st.number_input(f"Years in Current Role #{i + 1}", min_value=0,
                                        value=employment_entries[i].get('years_in_current_role', 0) if i < len(
                                            employment_entries) else 0)
        new_employment.append({
            "job_title": job_title,
            "company": company,
            "years_in_current_role": years_in_role
        })

    st.divider()

    # Education (Multiple Entries)
    education_entries = profile.get('education', [])
    education_count = st.number_input("Number of Education Entries", min_value=1,
                                      value=len(education_entries) if len(education_entries) > 0 else 1)

    new_education = []
    for i in range(education_count):
        st.write(f"Education #{i + 1}")

        # Use selectbox to select courses from the available courses in the courses table
        degree_or_course_name = st.selectbox(f"Degree or Course Name #{i + 1}", available_courses,
                                             index=available_courses.index(
                                                 education_entries[i].get('degree_or_course_name', ''))
                                             if i < len(education_entries) and education_entries[i].get(
                                                 'degree_or_course_name', '') in available_courses
                                             else 0)

        institution = st.text_input(f"Institution #{i + 1}",
                                    education_entries[i].get('institution', '') if i < len(education_entries) else "")

        completion_year = st.number_input(f"Completion Year #{i + 1}", min_value=1950, max_value=datetime.now().year,
                                          value=education_entries[i].get('completion_year',
                                                                         datetime.now().year) if i < len(
                                              education_entries) else datetime.now().year)

        new_education.append({
            "degree_or_course_name": degree_or_course_name,
            "institution": institution,
            "completion_year": completion_year
        })

    st.divider()

    st.subheader("Preferences")

    # Fetch available locations and institutions from MongoDB
    location_options = [f"{loc['location_name']} - {loc['state']}" for loc in db["locations"].find()]
    study_preferences = [f"{inst['institution_name']} - {inst['location']}" for inst in db["institutions"].find()]

    # Preferences
    current_location_preferences = profile.get('preferences', {}).get('location_preference', [])
    current_study_preferences = profile.get('preferences', {}).get('study_preference', [])
    valid_location_preferences = [loc for loc in current_location_preferences if loc in location_options]
    valid_study_preferences = [study for study in current_study_preferences if study in study_preferences]

    new_location_preference = st.multiselect("Preferred Locations", location_options,
                                             default=valid_location_preferences)
    new_study_preference = st.multiselect("Study Preferences", study_preferences, default=valid_study_preferences)

    # Cost and duration limits
    new_cost_limit = st.number_input("Cost Limit", value=profile.get('preferences', {}).get('cost_limit', 0),
                                     min_value=0)
    new_duration_limit = st.number_input("Duration Limit (months)",
                                         value=profile.get('preferences', {}).get('duration_limit', 0), min_value=0)

    if st.button("Save Changes"):
        updates = {
            "profile": {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "date_of_birth": new_date_of_birth_datetime,
                "gender": new_gender,
                "location": new_location,
                "nationality": new_nationality,
                "skills": new_skills,
                "employment": new_employment,  # Multiple employment entries
                "education": new_education,  # Consolidated education and courses
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
