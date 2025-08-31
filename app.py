import streamlit as st
from utils.auth import check_authentication, logout

# Page configuration
st.set_page_config(
    page_title="Activity Tracker",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Check authentication first
    if not check_authentication():
        return
    
    # Main app content
    st.title("Activity Tracker")
    st.write("Welcome to your personal activity tracking dashboard!")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        # Navigation buttons
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📈")
        st.page_link("pages/2_Live_Update.py", label="Live Update", icon="⏱️") 
        st.page_link("pages/3_Historical.py", label="Historical Entry", icon="📅")
        
        st.divider()
        
        # User info and logout
        st.write("**Logged in as:** admin")
        if st.button("Logout", type="secondary"):
            logout()
    
    # Main content area
    st.markdown("""
    ## Quick Start
    
    Choose one of the options below to get started:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Dashboard
        View your recent activities and statistics
        """)
        if st.button("Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    
    with col2:
        st.markdown("""
        ### Live Update
        Log activities in real-time with timer
        """)
        if st.button("Start Live Logging", type="primary", use_container_width=True):
            st.switch_page("pages/2_Live_Update.py")
    
    with col3:
        st.markdown("""
        ### Historical Entry
        Add past activities with custom dates
        """)
        if st.button("Add Historical Activity", type="primary", use_container_width=True):
            st.switch_page("pages/3_Historical.py")
    
    # Quick info section
    st.markdown("---")
    st.markdown("""
    ## About Activity Tracker
    
    This application helps you track your daily activities with:
    - **Real-time logging** with built-in timer
    - **Location tracking** (GPS + manual entry)
    - **Perception scoring** (-5 to +5 scale)
    - **Tag system** for categorization
    - **Media uploads** (images and videos)
    - **Statistics and insights**
    """)

if __name__ == "__main__":
    main()