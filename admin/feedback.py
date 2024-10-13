from datetime import datetime
import streamlit as st
from bson import ObjectId
import pandas as pd

# Number of items to display per page
FEEDBACKS_PER_PAGE = 3

def show_feedbacks_for_admin(db):
    st.subheader("Feedbacks from Migration Agents")

    # Fetch all pathways for the dropdown menu
    pathways = list(db["pr_pathways"].find({}, {"_id": 1, "pathway_name": 1}))
    pathway_options = ["All Pathways"] + [pathway["pathway_name"] for pathway in pathways]

    # Map pathway_name to pathway_id (string)
    pathway_name_to_id = {pathway["pathway_name"]: str(pathway["_id"]) for pathway in pathways}

    # Dropdown menu for selecting pathway
    selected_pathway_name = st.selectbox("Filter Feedbacks by Pathway", pathway_options)

    # Pagination: Get the current page from session_state (default is page 0)
    if 'feedback_page' not in st.session_state:
        st.session_state.feedback_page = 0

    current_page = st.session_state.feedback_page

    # Fetch feedbacks from the database based on selected pathway
    if selected_pathway_name != "All Pathways":
        selected_pathway_id = pathway_name_to_id[selected_pathway_name]
        feedback_records = db["agent_feedback"].find({"pathway_id": selected_pathway_id})
    else:
        feedback_records = db["agent_feedback"].find()

    feedback_list = []

    # Prepare feedback list for display
    for record in feedback_records:
        pathway = db["pr_pathways"].find_one({"_id": ObjectId(record["pathway_id"])})
        user = db["users"].find_one({"_id": ObjectId(record["user_id"])})
        agent = db["users"].find_one({"_id": ObjectId(record["agent_id"])})

        user_id = str(user['_id']) if user else "Unknown User"
        agent_name = agent['username'] if agent else "Unknown Agent"
        pathway_name = pathway['pathway_name'] if pathway else "Unknown Pathway"

        feedback_list.append({
            "pathway_name": pathway_name,
            "agent_name": agent_name,
            "user_id": user_id,
            "accuracy": record["accuracy"],
            "feasibility": record["feasibility"],
            "comments": record["comments"],
            "submitted_at": record["submitted_at"],
            "reply": record.get("reply", ""),
            "feedback_id": str(record["_id"])
        })

    feedback_df = pd.DataFrame(feedback_list)

    # Pagination logic
    total_feedbacks = len(feedback_df)
    total_pages = (total_feedbacks - 1) // FEEDBACKS_PER_PAGE + 1

    # Adjust current_page if necessary
    if current_page >= total_pages:
        current_page = total_pages - 1
        st.session_state.feedback_page = current_page
    if current_page < 0:
        current_page = 0
        st.session_state.feedback_page = current_page

    # Display feedbacks for the current page
    start_index = current_page * FEEDBACKS_PER_PAGE
    end_index = min(start_index + FEEDBACKS_PER_PAGE, total_feedbacks)

    for i, row in feedback_df.iloc[start_index:end_index].iterrows():
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
            db["agent_feedback"].update_one(
                {"_id": ObjectId(row['feedback_id'])},
                {"$set": {"reply": reply, "replied_at": datetime.utcnow()}}
            )
            st.success(f"Reply for {row['pathway_name']} submitted successfully.")
            st.rerun()

    # Pagination controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if current_page > 0:
            if st.button("Previous", key="prev_feedback"):
                st.session_state.feedback_page -= 1
                st.rerun()
    with col2:
        st.write(f"Page {current_page + 1} of {total_pages}")
    with col3:
        if current_page < total_pages - 1:
            if st.button("Next", key="next_feedback"):
                st.session_state.feedback_page += 1
                st.rerun()
