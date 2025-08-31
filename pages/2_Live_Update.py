import streamlit as st
import time
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import check_authentication
from utils.data_handler import SupabaseHandler
from utils.location import location_handler, gps_location_handler, clear_location

# Page configuration
st.set_page_config(
    page_title="Live Update - Activity Tracker",
    page_icon="⏱️",
    layout="wide"
)

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def main():
    # Check authentication
    if not check_authentication():
        return
    
    # Initialize data handler
    db_handler = SupabaseHandler()
    
    # Initialize session state
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "timer_stopped" not in st.session_state:
        st.session_state.timer_stopped = False
    if "final_duration" not in st.session_state:
        st.session_state.final_duration = 0
    
    # Page header
    st.title("⏱️ Live Activity Tracker")
    st.write("Track your activities in real-time with the built-in timer.")
    
    # Timer Section
    st.subheader("⏰ Activity Timer")
    
    timer_col1, timer_col2, timer_col3 = st.columns([2, 2, 2])
    
    with timer_col1:
        if not st.session_state.timer_running and not st.session_state.timer_stopped:
            if st.button("▶️ Start Timer", type="primary", use_container_width=True):
                st.session_state.timer_start = time.time()
                st.session_state.timer_running = True
                st.session_state.timer_stopped = False
                clear_location()  # Clear previous location data
                st.rerun()
    
    with timer_col2:
        if st.session_state.timer_running:
            if st.button("⏹️ Stop Timer", type="secondary", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_stopped = True
                st.session_state.final_duration = time.time() - st.session_state.timer_start
                st.rerun()
    
    with timer_col3:
        if st.session_state.timer_stopped or st.session_state.timer_running:
            if st.button("🔄 Reset Timer", use_container_width=True):
                st.session_state.timer_start = None
                st.session_state.timer_running = False
                st.session_state.timer_stopped = False
                st.session_state.final_duration = 0
                clear_location()
                st.rerun()
    
    # Display current timer status
    if st.session_state.timer_running:
        # Real-time timer display
        placeholder = st.empty()
        current_time = time.time()
        elapsed = current_time - st.session_state.timer_start
        
        with placeholder.container():
            st.success(f"🟢 **Timer Running**: {format_duration(elapsed)}")
            st.info("⏱️ Timer is actively running. Click 'Stop Timer' when your activity is complete.")
        
        # Auto-refresh every second for real-time updates
        time.sleep(1)
        st.rerun()
    
    elif st.session_state.timer_stopped:
        st.success(f"✅ **Activity Completed**: Duration {format_duration(st.session_state.final_duration)}")
        st.info("👇 Please fill out the activity form below to log your activity.")
    
    else:
        st.info("⏳ Click 'Start Timer' to begin tracking your activity.")
    
    # Activity Form - Show only when timer is stopped
    if st.session_state.timer_stopped:
        st.divider()
        st.subheader("📝 Log Your Activity")
        
        # GPS Location Handler (outside form)
        gps_location_handler()
        st.divider()
        
        with st.form("live_activity_form"):
            # Location input
            location_data = location_handler()
            
            # Media upload
            st.subheader("📸 Media Upload")
            uploaded_files = st.file_uploader(
                "Upload photos or videos",
                type=["jpg", "jpeg", "png", "mp4", "mov"],
                accept_multiple_files=True,
                help="Upload images (JPG, PNG) or videos (MP4, MOV) related to your activity"
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
                placeholder="work, meeting, productive, creative, exercise...",
                help="Add tags to categorize your activity. Separate multiple tags with commas."
            )
            
            # Description
            st.subheader("📝 Description")
            description = st.text_area(
                "Describe your activity",
                placeholder="What did you do during this activity? How did it go? Any notable details...",
                help="Provide a detailed description of your activity"
            )
            
            # Submit button
            submitted = st.form_submit_button("💾 Log Activity", type="primary", use_container_width=True)
            
            if submitted:
                # Validate required fields
                if not description.strip():
                    st.error("❌ Description is required!")
                    return
                
                with st.spinner("💾 Saving your activity..."):
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
                            "timestamp": datetime.now().isoformat(),
                            "type": "live",
                            "location": location_data,
                            "perception_score": perception_score,
                            "tags": tags,
                            "description": description.strip(),
                            "timer_duration": int(st.session_state.final_duration),
                            "media_urls": media_urls
                        }
                        
                        # Save to database
                        activity_id = db_handler.add_activity(activity_data)
                        
                        if activity_id:
                            st.success("✅ Activity logged successfully!")
                            st.balloons()
                            
                            # Show summary
                            st.markdown("### 📋 Activity Summary")
                            summary_col1, summary_col2 = st.columns(2)
                            
                            with summary_col1:
                                st.write(f"⏱️ **Duration:** {format_duration(st.session_state.final_duration)}")
                                st.write(f"🎯 **Perception Score:** {perception_score} ({score_labels.get(perception_score)})")
                                st.write(f"📍 **Location:** {location_data['description']}")
                            
                            with summary_col2:
                                st.write(f"🏷️ **Tags:** {', '.join(tags) if tags else 'None'}")
                                st.write(f"📸 **Media Files:** {len(media_urls)} uploaded")
                                st.write(f"📝 **Description:** {description[:50]}{'...' if len(description) > 50 else ''}")
                            
                            # Reset timer after successful save
                            time.sleep(2)
                            st.session_state.timer_start = None
                            st.session_state.timer_running = False
                            st.session_state.timer_stopped = False
                            st.session_state.final_duration = 0
                            clear_location()
                            st.rerun()
                        else:
                            st.error("❌ Failed to log activity. Please try again.")
                    
                    except Exception as e:
                        st.error(f"❌ Error logging activity: {str(e)}")
    
    # Navigation buttons
    st.divider()
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("📈 View Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    
    with nav_col2:
        if st.button("📅 Historical Entry", use_container_width=True):
            st.switch_page("pages/3_Historical.py")
    
    with nav_col3:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    
    # Tips section
    if not st.session_state.timer_running and not st.session_state.timer_stopped:
        st.markdown("""
        ### 💡 How to Use Live Tracking
        
        1. **Start Timer** - Click the start button when you begin your activity
        2. **Do Your Activity** - The timer runs in the background while you work/exercise/etc.
        3. **Stop Timer** - Click stop when you finish your activity
        4. **Fill Form** - Add location, perception score, tags, and description
        5. **Save** - Your activity will be logged with the exact duration tracked
        
        **💡 Tip:** The timer provides accurate duration tracking for better activity insights!
        """)

if __name__ == "__main__":
    main()