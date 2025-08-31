import streamlit as st

def check_authentication():
    """Check if user is authenticated, show login form if not"""
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Show login form
    st.title("Login")
    st.write("Please login to access the Activity Tracker")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            # Simple credential check (as specified in requirements)
            if username == "admin" and password == "password":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    return False

def logout():
    """Logout function to clear authentication state"""
    st.session_state.authenticated = False
    st.rerun()