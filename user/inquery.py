import streamlit as st
from datetime import datetime
from bson import ObjectId

# Function for users to submit inquiries to the admin
def user_inquiry_section(user, db):
    st.subheader("Inquiry Section")

    # Input for user's inquiry
    inquiry_title = st.text_input("Inquiry Title")
    inquiry_message = st.text_area("Your Message")

    # Submit inquiry button
    if st.button("Submit Inquiry"):
        if inquiry_title and inquiry_message:
            inquiry = {
                "user_id": user["_id"],
                "username": user["username"],
                "title": inquiry_title,
                "message": inquiry_message,
                "submitted_at": datetime.utcnow(),
                "status": "Pending",  # Initially set the status to pending
                "admin_reply": ""
            }
            # Store the inquiry in the database
            db["user_inquiries"].insert_one(inquiry)
            st.success("Your inquiry has been submitted to the admin.")
        else:
            st.error("Please fill in both the title and message fields.")
