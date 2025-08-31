import streamlit as st
from datetime import datetime, date, time as dt_time
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import check_authentication
from utils.data_handler import SupabaseHandler
from utils.location import location_handler, gps_location_handler, clear_location

# Page configuration
st.set_page_config(
    page_title="Historical Entry - Activity Tracker",
    page_icon="📅",
    layout="wide"
)

def main():
    # Check authentication
    if not check_authentication():
        return
    
    # Initialize data handler
    db_handler = SupabaseHandler()
    
    # Page header
    st.title("📅 Historical Activity Entry")
    st.write("Add past activities with custom dates and times.")
    
    # Clear location data when page loads (fresh start)
    if "historical_page_loaded" not in st.session_state:
        clear_location()
        st.session_state.historical_page_loaded = True
    
    # GPS Location Handler (outside form)
    gps_location_handler()
    st.divider()
    
    # Historical Activity Form
    with st.form("historical_activity_form"):
        st.subheader("🕐 Date & Time Selection")
        
        # Date and time inputs
        date_col, time_col = st.columns(2)
        
        with date_col:
            selected_date = st.date_input(
                "Activity Date",
                value=date.today(),
                max_value=date.today(),
                help="Select the date when this activity occurred"
            )
        
        with time_col:
            selected_time = st.time_input(
                "Activity Time",
                value=datetime.now().time(),
                help="Select the approximate time when this activity occurred"
            )
        
        # Combine date and time
        activity_datetime = datetime.combine(selected_date, selected_time)
        st.info(f"🕐 Activity will be logged for: **{activity_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}**")
        
        st.divider()
        
        # Location input
        location_data = location_handler()
        
        # Media upload
        st.subheader("📸 Media Upload")
        uploaded_files = st.file_uploader(
            "Upload photos or videos from this activity",
            type=["jpg", "jpeg", "png", "mp4", "mov"],
            accept_multiple_files=True,
            help="Upload images (JPG, PNG) or videos (MP4, MOV) from your past activity"
        )
        
        # Perception score
        st.subheader("🎯 Perception Score")
        perception_score = st.slider(
            "How did you feel about this activity?",
            min_value=-5,
            max_value=5,
            value=0,
            help="Rate your perception of the activity from -5 (very negative) to +5 (very positive)"
        )
        
        # Display perception labels
        score_labels = {
            -5: "Very Negative", -4: "Negative", -3: "Mostly Negative",
            -2: "Somewhat Negative", -1: "Slightly Negative", 0: "Neutral",
            1: "Slightly Positive", 2: "Somewhat Positive", 3: "Mostly Positive",
            4: "Positive", 5: "Very Positive"
        }
        st.write(f"**Selected:** {score_labels.get(perception_score, 'Neutral')}")
        
        # Tags
        st.subheader("🏷️ Tags")
        tags_input = st.text_input(
            "Add tags (comma-separated)",
            placeholder="work, meeting, productive, creative, exercise, family, travel...",
            help="Add tags to categorize your activity. Separate multiple tags with commas."
        )
        
        # Description
        st.subheader("📝 Description")
        description = st.text_area(
            "Describe your activity",
            placeholder="What did you do? Where were you? Who were you with? How did it go? Any memorable details...",
            help="Provide a detailed description of your past activity"
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Historical Activity", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not description.strip():
                st.error("❌ Description is required!")
                st.stop()
            
            # Validate date is not in the future
            if activity_datetime > datetime.now():
                st.error("❌ Activity date cannot be in the future!")
                st.stop()
            
            with st.spinner("💾 Saving your historical activity..."):
                try:
                    # Process tags
                    tags = []
                    if tags_input.strip():
                        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                    
                    # Process media uploads
                    media_urls = []
                    if uploaded_files:
                        media_urls = db_handler.process_media_uploads(uploaded_files)
                        if len(media_urls) != len(uploaded_files):
                            st.warning("⚠️ Some media files failed to upload.")
                    
                    # Prepare activity data
                    activity_data = {
                        "timestamp": activity_datetime.isoformat(),
                        "type": "historical",
                        "location": location_data,
                        "perception_score": perception_score,
                        "tags": tags,
                        "description": description.strip(),
                        "timer_duration": None,  # No timer for historical entries
                        "media_urls": media_urls
                    }
                    
                    # Save to database
                    activity_id = db_handler.add_activity(activity_data)
                    
                    if activity_id:
                        st.success("✅ Historical activity saved successfully!")
                        st.balloons()
                        
                        # Show summary
                        st.markdown("### 📋 Activity Summary")
                        summary_col1, summary_col2 = st.columns(2)
                        
                        with summary_col1:
                            st.write(f"📅 **Date & Time:** {activity_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}")
                            st.write(f"🎯 **Perception Score:** {perception_score} ({score_labels.get(perception_score)})")
                            st.write(f"📍 **Location:** {location_data['description']}")
                        
                        with summary_col2:
                            st.write(f"🏷️ **Tags:** {', '.join(tags) if tags else 'None'}")
                            st.write(f"📸 **Media Files:** {len(media_urls)} uploaded")
                            st.write(f"📝 **Description:** {description[:50]}{'...' if len(description) > 50 else ''}")
                        
                        # Option to add another activity or go to dashboard
                        st.markdown("### 🚀 What's Next?")
                        next_col1, next_col2, next_col3 = st.columns(3)
                        
                        with next_col1:
                            if st.button("➕ Add Another Activity", use_container_width=True):
                                clear_location()
                                st.rerun()
                        
                        with next_col2:
                            if st.button("📈 View Dashboard", use_container_width=True):
                                st.switch_page("pages/1_Dashboard.py")
                        
                        with next_col3:
                            if st.button("⏱️ Start Live Activity", use_container_width=True):
                                st.switch_page("pages/2_Live_Update.py")
                    
                    else:
                        st.error("❌ Failed to save activity. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error saving activity: {str(e)}")
    
    # Navigation buttons (outside the form)
    st.divider()
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("📈 View Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    
    with nav_col2:
        if st.button("⏱️ Live Update", use_container_width=True):
            st.switch_page("pages/2_Live_Update.py")
    
    with nav_col3:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    
    # Tips and examples section
    with st.expander("💡 Tips for Historical Entries"):
        st.markdown("""
        ### 📝 Writing Good Activity Descriptions
        
        **Great examples:**
        - "Had a productive 2-hour work session on the new project proposal. Managed to complete the research phase and started drafting the executive summary."
        - "Morning jog around Central Park. Weather was perfect, ran for about 45 minutes. Felt energized and accomplished."
        - "Family dinner at mom's house. Tried her new lasagna recipe - it was amazing! Great conversations about vacation plans."
        
        ### 🏷️ Useful Tags
        - **Work**: `work`, `meeting`, `productive`, `coding`, `writing`, `presentation`
        - **Health**: `exercise`, `running`, `gym`, `meditation`, `sleep`, `doctor`
        - **Social**: `family`, `friends`, `date`, `party`, `networking`, `community`
        - **Learning**: `reading`, `course`, `tutorial`, `research`, `study`, `skill`
        - **Personal**: `creative`, `hobby`, `cooking`, `travel`, `shopping`, `home`
        
        ### 🎯 Perception Score Guide
        - **+5 to +3**: Activities you loved and felt very positive about
        - **+2 to +1**: Generally positive experiences
        - **0**: Neutral activities (routine, neither good nor bad)
        - **-1 to -2**: Somewhat negative experiences
        - **-3 to -5**: Activities you disliked or felt negative about
        
        ### 📍 Location Tips
        - Use GPS for precise location when possible
        - For manual entry, be specific: "Home office", "Downtown gym", "Coffee shop on 5th St"
        - Include context that might be relevant later: "Mom's house", "New restaurant downtown"
        """)

if __name__ == "__main__":
    main()