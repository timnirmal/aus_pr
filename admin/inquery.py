from datetime import datetime
import streamlit as st
from bson import ObjectId
import pandas as pd

# Number of inquiries to display per page
INQUIRIES_PER_PAGE = 1

# Function for admins to view and reply to user inquiries
def manage_user_inquiries(db):
    st.subheader("User Inquiries")

    # Add a filter for searching inquiries by user name
    search_query = st.text_input("Search Inquiries by User Name")

    # Pagination: Get the current page from session_state (default is page 0)
    if 'inquiry_page' not in st.session_state:
        st.session_state.inquiry_page = 0

    current_page = st.session_state.inquiry_page

    # Fetch inquiries based on the search query
    if search_query:
        users = db["users"].find({"username": {"$regex": search_query, "$options": "i"}})
        user_ids = [str(user["_id"]) for user in users]
        inquiries = db["user_inquiries"].find({"user_id": {"$in": user_ids}, "status": "Pending"})
    else:
        inquiries = db["user_inquiries"].find({"status": "Pending"})

    inquiry_list = []
    # Prepare inquiries for display
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

    # Pagination logic
    total_inquiries = len(inquiries_df)
    total_pages = (total_inquiries - 1) // INQUIRIES_PER_PAGE + 1

    # Display inquiries for the current page
    start_index = current_page * INQUIRIES_PER_PAGE
    end_index = min(start_index + INQUIRIES_PER_PAGE, total_inquiries)

    for i, row in inquiries_df.iloc[start_index:end_index].iterrows():
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

    # Pagination controls (always show, even if only one page)
    col1, col2, col3 = st.columns(3)
    with col1:
        if current_page > 0:
            if st.button("Previous", key="prev_inquiry"):
                st.session_state.inquiry_page -= 1
                st.rerun()
    with col3:
        if current_page < total_pages - 1:
            if st.button("Next", key="next_inquiry"):
                st.session_state.inquiry_page += 1
                st.rerun()
