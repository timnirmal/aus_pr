from datetime import datetime
import streamlit as st
from bson.objectid import ObjectId

# Set the number of users to display per page
ITEMS_PER_PAGE = 5

def manage_user_accounts(db):
    st.title("Admin - Manage User Accounts")

    # Search for users by username or email
    search_query = st.text_input("Search Users by Username or Email")

    # Pagination: Get the current page from session_state (default is page 0)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    current_page = st.session_state.current_page

    # Find users based on the search query or list all users
    if search_query:
        users = list(db["users"].find({
            "$or": [
                {"username": {"$regex": search_query, "$options": "i"}},
                {"profile.email": {"$regex": search_query, "$options": "i"}}
            ]
        }))
    else:
        # List all users if no search query
        users = list(db["users"].find())

    # Pagination: Slice the user list to display only the users for the current page
    total_pages = (len(users) - 1) // ITEMS_PER_PAGE + 1
    paginated_users = users[current_page * ITEMS_PER_PAGE:(current_page + 1) * ITEMS_PER_PAGE]

    # Display user list
    st.subheader(f"User List (Page {current_page + 1} of {total_pages})")
    for user in paginated_users:
        st.write(
            f"Username: {user['username']}, Email: {user.get('profile', {}).get('email', 'N/A')}, Status: {'Disabled' if user.get('disabled', False) else 'Active'}")
        if st.button(f"View Details of {user['username']}", key=f"view_{user['_id']}"):
            view_user_details(user, db)
        if st.button(f"Delete {user['username']}", key=f"delete_{user['_id']}"):
            delete_user(user['_id'], db)
            st.success(f"Deleted user: {user['username']}")
        if user.get('disabled', False):
            if st.button(f"Enable {user['username']}", key=f"enable_{user['_id']}"):
                enable_disable_user(user['_id'], db, disable=False)
                st.success(f"Enabled user: {user['username']}")
        else:
            if st.button(f"Disable {user['username']}", key=f"disable_{user['_id']}"):
                enable_disable_user(user['_id'], db, disable=True)
                st.success(f"Disabled user: {user['username']}")

    # Pagination controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if current_page > 0:
            if st.button("Previous"):
                st.session_state.current_page -= 1
                st.rerun()  # Refresh the page to show the previous page
    with col3:
        if current_page < total_pages - 1:
            if st.button("Next"):
                st.session_state.current_page += 1
                st.rerun()  # Refresh the page to show the next page

# View user details
def view_user_details(user, db):
    st.subheader(f"Details of {user['username']}")
    st.write(f"Username: {user['username']}")
    st.write(f"Email: {user.get('profile', {}).get('email', 'N/A')}")
    st.write(f"Full Name: {user.get('profile', {}).get('first_name', '')} {user.get('profile', {}).get('last_name', '')}")
    st.write(f"Date of Birth: {user.get('profile', {}).get('date_of_birth', 'N/A')}")
    st.write(f"Skills: {', '.join(user.get('skills', []))}")
    st.write(f"Location: {user.get('profile', {}).get('location', 'N/A')}")

    # Option to edit user details
    if st.button(f"Edit Details of {user['username']}"):
        edit_user_details(user, db)

# Edit user details
def edit_user_details(user, db):
    st.subheader(f"Edit User: {user['username']}")
    new_first_name = st.text_input("First Name", value=user.get('profile', {}).get('first_name', ''))
    new_last_name = st.text_input("Last Name", value=user.get('profile', {}).get('last_name', ''))
    new_email = st.text_input("Email", value=user.get('profile', {}).get('email', ''))
    new_location = st.text_input("Location", value=user.get('profile', {}).get('location', ''))

    if st.button(f"Save Changes for {user['username']}"):
        updates = {
            "profile.first_name": new_first_name,
            "profile.last_name": new_last_name,
            "profile.email": new_email,
            "profile.location": new_location,
            "updated_at": datetime.utcnow()
        }
        db["users"].update_one({"_id": user["_id"]}, {"$set": updates})
        st.success(f"Updated details for {user['username']}")

# Delete user
def delete_user(user_id, db):
    db["users"].delete_one({"_id": ObjectId(user_id)})

# Enable or disable user
def enable_disable_user(user_id, db, disable=True):
    db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"disabled": disable, "updated_at": datetime.utcnow()}})
