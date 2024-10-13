from datetime import datetime
import streamlit as st
from bson import ObjectId
import pandas as pd

# Number of inquiries to display per page
INQUIRIES_PER_PAGE = 3

# Function for admins to view and reply to user inquiries
def manage_user_inquiries(db):
    st.subheader("User Inquiries")

    # Add a search box for filtering inquiries by user name or message content
    search_query = st.text_input("Search Inquiries by User Name or Message")

    # Pagination: Get the current page from session_state (default is page 0)
    if 'inquiry_page' not in st.session_state:
        st.session_state.inquiry_page = 0

    current_page = st.session_state.inquiry_page

    # Build the query based on the search input
    if search_query:
        # Find users whose usernames match the search query
        user_cursor = db["users"].find({"username": {"$regex": search_query, "$options": "i"}}, {"_id": 1})
        user_ids = [user["_id"] for user in user_cursor]

        # Build the query to find inquiries where either the user_id matches or the message contains the search query
        inquiry_query = {
            "status": "Pending",
            "$or": [
                {"user_id": {"$in": user_ids}},
                {"message": {"$regex": search_query, "$options": "i"}}
            ]
        }
    else:
        # If no search query, fetch all pending inquiries
        inquiry_query = {"status": "Pending"}

    # Fetch inquiries based on the constructed query
    inquiries_cursor = db["user_inquiries"].find(inquiry_query)
    inquiries = list(inquiries_cursor)

    # Prepare inquiries for display
    inquiry_list = []
    for inquiry in inquiries:
        user = db["users"].find_one({"_id": ObjectId(inquiry["user_id"])})
        user_name = user["username"] if user else "Unknown User"

        inquiry_list.append({
            "user": user_name,
            "title": inquiry.get("title", "No Title"),
            "message": inquiry.get("message", ""),
            "submitted_at": inquiry.get("submitted_at", "Unknown Date"),
            "inquiry_id": str(inquiry["_id"]),
            "admin_reply": inquiry.get("admin_reply", "")
        })

    # Convert the list to a DataFrame for display
    inquiries_df = pd.DataFrame(inquiry_list)

    # Pagination logic
    total_inquiries = len(inquiries_df)
    total_pages = (total_inquiries - 1) // INQUIRIES_PER_PAGE + 1 if total_inquiries > 0 else 1

    # Adjust current_page if necessary
    if current_page >= total_pages:
        current_page = total_pages - 1
        st.session_state.inquiry_page = current_page
    if current_page < 0:
        current_page = 0
        st.session_state.inquiry_page = current_page

    # Display inquiries for the current page
    start_index = current_page * INQUIRIES_PER_PAGE
    end_index = min(start_index + INQUIRIES_PER_PAGE, total_inquiries)

    if total_inquiries == 0:
        st.info("No inquiries to display.")
    else:
        for i, row in inquiries_df.iloc[start_index:end_index].iterrows():
            st.write(f"Inquiry from {row['user']} ({row['submitted_at']}):")
            st.write(f"**Title**: {row['title']}")
            st.write(f"**Message**: {row['message']}")
            st.write(f"**Admin Reply**: {row['admin_reply']}")

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

    # Pagination controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if current_page > 0:
            if st.button("Previous", key="prev_inquiry"):
                st.session_state.inquiry_page -= 1
                st.rerun()
    with col2:
        st.write(f"Page {current_page + 1} of {total_pages}")
    with col3:
        if current_page < total_pages - 1:
            if st.button("Next", key="next_inquiry"):
                st.session_state.inquiry_page += 1
                st.rerun()
