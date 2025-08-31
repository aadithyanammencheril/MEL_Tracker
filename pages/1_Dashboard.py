import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import check_authentication
from utils.data_handler import SupabaseHandler

# Page configuration
st.set_page_config(
    page_title="Dashboard - Activity Tracker",
    page_icon="📈",
    layout="wide"
)

def main():
    # Check authentication
    if not check_authentication():
        return
    
    # Initialize data handler
    db_handler = SupabaseHandler()
    
    # Page header
    st.title("📈 Dashboard")
    st.write("Welcome back! Here's your activity overview.")
    
    # Quick navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏱️ Start Live Logging", type="primary", use_container_width=True):
            st.switch_page("pages/2_Live_Update.py")
    with col2:
        if st.button("📅 Add Historical Activity", use_container_width=True, key="historical_nav"):
            st.switch_page("pages/3_Historical.py")
    with col3:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Quick Stats Section
    st.subheader("📊 Quick Statistics")
    
    with st.spinner("Loading statistics..."):
        stats = db_handler.get_activity_stats()
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="📅 Activities Today", 
            value=stats["total_today"],
            help="Number of activities logged today"
        )
    
    with metric_col2:
        perception_color = "normal"
        if stats["avg_perception"] > 2:
            perception_color = "normal"  # Green would be ideal
        elif stats["avg_perception"] < -2:
            perception_color = "inverse"  # Red would be ideal
        
        st.metric(
            label="🎯 Avg Perception Score", 
            value=f"{stats['avg_perception']}",
            help="Average perception score across all activities (-5 to +5)"
        )
    
    with metric_col3:
        st.metric(
            label="📈 Total Activities", 
            value=stats["total_all_time"],
            help="Total number of activities logged"
        )
    
    st.divider()
    
    # Recent Activities Section
    st.subheader("🕐 Recent Activities")
    
    with st.spinner("Loading recent activities..."):
        activities = db_handler.get_recent_activities(limit=10)
    
    if activities:
        # Format activities for display
        formatted_activities = []
        for activity in activities:
            formatted = db_handler.format_activity_for_display(activity)
            formatted_activities.append({
                "Time": formatted.get("timestamp", "N/A"),
                "Type": formatted.get("type", "N/A").title(),
                "Location": formatted.get("location", "Not specified"),
                "Score": formatted.get("perception_score", "N/A"),
                "Description": formatted.get("description", "No description")[:50] + ("..." if len(str(formatted.get("description", ""))) > 50 else ""),
                "Tags": formatted.get("tags", "")
            })
        
        # Display as dataframe
        df = pd.DataFrame(formatted_activities)
        
        # Style the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.NumberColumn(
                    "Score",
                    help="Perception score (-5 to +5)",
                    min_value=-5,
                    max_value=5,
                    format="%d"
                ),
                "Type": st.column_config.TextColumn(
                    "Type",
                    help="Activity type (Live or Historical)"
                ),
                "Time": st.column_config.TextColumn(
                    "Time",
                    help="When the activity was logged"
                )
            }
        )
        
        # Show more details option
        with st.expander("🔍 View Full Activity Details"):
            selected_idx = st.selectbox(
                "Select activity to view details:",
                range(len(activities)),
                format_func=lambda x: f"{formatted_activities[x]['Time']} - {formatted_activities[x]['Description'][:30]}..."
            )
            
            if selected_idx is not None:
                selected_activity = activities[selected_idx]
                
                # Display full details
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.write("**Activity Details:**")
                    st.write(f"📅 **Timestamp:** {selected_activity.get('timestamp', 'N/A')}")
                    st.write(f"📍 **Location:** {selected_activity.get('location', {}).get('description', 'Not specified') if isinstance(selected_activity.get('location'), dict) else str(selected_activity.get('location', 'Not specified'))}")
                    st.write(f"🎯 **Perception Score:** {selected_activity.get('perception_score', 'N/A')}")
                    st.write(f"⏱️ **Timer Duration:** {selected_activity.get('timer_duration', 'N/A')} seconds" if selected_activity.get('timer_duration') else "⏱️ **Timer Duration:** Not applicable")
                
                with detail_col2:
                    st.write("**Additional Info:**")
                    st.write(f"🏷️ **Tags:** {', '.join(selected_activity.get('tags', [])) if selected_activity.get('tags') else 'None'}")
                    st.write(f"📝 **Description:** {selected_activity.get('description', 'No description provided')}")
                    
                    if selected_activity.get('media_urls'):
                        st.write("📸 **Media Files:**")
                        for i, url in enumerate(selected_activity['media_urls']):
                            st.write(f"- [Media {i+1}]({url})")
    else:
        st.info("📭 No activities logged yet. Start by adding your first activity!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏱️ Log Live Activity", type="primary", use_container_width=True):
                st.switch_page("pages/2_Live_Update.py")
        with col2:
            if st.button("📅 Add Historical Activity", use_container_width=True, key="historical_empty"):
                st.switch_page("pages/3_Historical.py")
    
    # Footer with helpful tips
    st.divider()
    st.markdown("""
    ### 💡 Tips
    - Use **Live Update** to track activities in real-time with a timer
    - Use **Historical Entry** to add past activities with specific dates
    - Perception scores help you understand your activity satisfaction over time
    - Add tags to categorize and analyze your activities better
    """)

if __name__ == "__main__":
    main()