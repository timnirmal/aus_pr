import streamlit as st
from datetime import datetime
import pandas as pd
from bson import ObjectId


# Function to display feedbacks and allow admin to reply
def show_feedbacks_for_admin(db):
    st.subheader("Feedbacks from Migration Agents")

    # Fetch all feedbacks from the database
    feedback_records = db["agent_feedback"].find()

    if feedback_records:
        feedback_list = []

        # Loop through each feedback and prepare it for display
        for record in feedback_records:
            pathway = db["pr_pathways"].find_one({"_id": ObjectId(record["pathway_id"])})
            user = db["users"].find_one({"_id": ObjectId(record["user_id"])})
            agent = db["users"].find_one({"_id": ObjectId(record["agent_id"])})

            feedback_list.append({
                "pathway_name": pathway['pathway_name'],
                "agent_name": agent['username'],
                "user_id": str(user['_id']),
                "accuracy": record["accuracy"],
                "feasibility": record["feasibility"],
                "comments": record["comments"],
                "submitted_at": record["submitted_at"],
                "reply": record.get("reply", ""),
                "feedback_id": str(record["_id"])
            })

        # Convert the feedback list into a DataFrame for easier display
        feedback_df = pd.DataFrame(feedback_list)

        # Display feedbacks
        for i, row in feedback_df.iterrows():
            st.write(f"Pathway: {row['pathway_name']}, User: {row['user_id']}, Agent: {row['agent_name']}")
            st.write(f"Accuracy: {row['accuracy']}, Feasibility: {row['feasibility']}")
            st.write(f"Comments: {row['comments']}")
            st.write(f"Submitted at: {row['submitted_at']}")
            st.write(f"Admin Reply: {row['reply']}")

            # Input for admin reply
            reply = st.text_area(f"Reply to feedback for {row['pathway_name']}", value=row['reply'],
                                 key=f"reply_{row['feedback_id']}")

            # Submit button to save the reply
            if st.button(f"Submit Reply for {row['pathway_name']}", key=f"submit_reply_{row['feedback_id']}"):
                # Update the feedback entry with the admin's reply
                db["agent_feedback"].update_one(
                    {"_id": ObjectId(row['feedback_id'])},
                    {"$set": {"reply": reply, "replied_at": datetime.utcnow()}}
                )
                st.success(f"Reply for {row['pathway_name']} submitted successfully.")
                st.rerun()  # Refresh the page to show the updated reply
    else:
        st.write("No feedback found.")


import pandas as pd


# Function for admins to view and reply to user inquiries
def manage_user_inquiries(db):
    st.subheader("User Inquiries")

    # Fetch all inquiries from the database
    inquiries = db["user_inquiries"].find({"status": "Pending"})

    if inquiries:
        inquiry_list = []
        # Loop through each inquiry and prepare it for display
        for inquiry in inquiries:
            user = db["users"].find_one({"_id": ObjectId(inquiry["user_id"])})
            inquiry_list.append({
                "user": user["username"] if user else "Unknown User",
                "title": inquiry["title"],
                "message": inquiry["message"],
                "submitted_at": inquiry["submitted_at"],
                "inquiry_id": str(inquiry["_id"]),
                "admin_reply": inquiry.get("admin_reply", "")
            })

        # Convert the list to a DataFrame for display
        inquiries_df = pd.DataFrame(inquiry_list)

        for i, row in inquiries_df.iterrows():
            st.write(f"Inquiry from {row['user']} ({row['submitted_at']}):")
            st.write(f"**Title**: {row['title']}")
            st.write(f"**Message**: {row['message']}")

            # Admin reply section
            reply = st.text_area(f"Reply to {row['user']}'s inquiry", value=row['admin_reply'],
                                 key=f"reply_{row['inquiry_id']}")

            # Submit reply button
            if st.button(f"Submit Reply for {row['user']}'s inquiry", key=f"submit_reply_{row['inquiry_id']}"):
                # Update the inquiry with the admin's reply and mark it as resolved
                db["user_inquiries"].update_one(
                    {"_id": ObjectId(row['inquiry_id'])},
                    {"$set": {"admin_reply": reply, "status": "Resolved", "replied_at": datetime.utcnow()}}
                )
                st.success(f"Reply to {row['user']}'s inquiry submitted successfully.")
                st.rerun()  # Refresh the page to show the updated reply
    else:
        st.write("No pending inquiries.")
