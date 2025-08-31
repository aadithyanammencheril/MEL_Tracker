import streamlit as st
from datetime import datetime, date
from .supabase_client import get_supabase_client
import uuid
import io

class SupabaseHandler:
    def __init__(self):
        self.client = get_supabase_client()
    
    def add_activity(self, activity_data):
        """Add new activity to database"""
        try:
            # Ensure required fields are present
            if not activity_data.get('timestamp'):
                activity_data['timestamp'] = datetime.now().isoformat()
            
            result = self.client.table("activities").insert(activity_data).execute()
            
            if result.data:
                return result.data[0]['id']
            else:
                raise Exception("Failed to insert activity")
                
        except Exception as e:
            st.error(f"Error adding activity: {str(e)}")
            return None
    
    def get_recent_activities(self, limit=10):
        """Get recent activities ordered by created_at DESC"""
        try:
            result = self.client.table("activities").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            st.error(f"Error fetching activities: {str(e)}")
            return []
    
    def upload_media_file(self, file_bytes, filename, file_type):
        """Upload media file to Supabase storage"""
        try:
            # Create path structure: {file_type}s/{date}/{filename}
            today = date.today().strftime("%Y-%m-%d")
            file_path = f"{file_type}s/{today}/{filename}"
            
            # Upload to storage bucket
            result = self.client.storage.from_("activity-media").upload(
                file_path, 
                file_bytes,
                {"content-type": f"{file_type}/*"}
            )
            
            if result:
                # Get public URL
                public_url = self.client.storage.from_("activity-media").get_public_url(file_path)
                return public_url
            else:
                raise Exception("Upload failed")
                
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return None
    
    def get_activity_stats(self):
        """Get activity statistics"""
        try:
            # Total activities today
            today = date.today().isoformat()
            today_result = self.client.table("activities").select("id").gte("created_at", today).execute()
            total_today = len(today_result.data) if today_result.data else 0
            
            # Average perception score (all time)
            perception_result = self.client.table("activities").select("perception_score").execute()
            perception_scores = [row['perception_score'] for row in perception_result.data if row['perception_score'] is not None] if perception_result.data else []
            avg_perception = sum(perception_scores) / len(perception_scores) if perception_scores else 0
            
            # Total activities all time
            total_result = self.client.table("activities").select("id").execute()
            total_all_time = len(total_result.data) if total_result.data else 0
            
            return {
                "total_today": total_today,
                "avg_perception": round(avg_perception, 2),
                "total_all_time": total_all_time
            }
            
        except Exception as e:
            st.error(f"Error fetching stats: {str(e)}")
            return {
                "total_today": 0,
                "avg_perception": 0,
                "total_all_time": 0
            }
    
    def process_media_uploads(self, uploaded_files):
        """Process multiple uploaded files and return their URLs"""
        media_urls = []
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Read file bytes
                file_bytes = uploaded_file.read()
                
                # Determine file type
                file_extension = uploaded_file.name.lower().split('.')[-1]
                if file_extension in ['jpg', 'jpeg', 'png']:
                    file_type = 'image'
                elif file_extension in ['mp4', 'mov']:
                    file_type = 'video'
                else:
                    continue  # Skip unsupported files
                
                # Generate unique filename
                unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
                
                # Upload file
                public_url = self.upload_media_file(file_bytes, unique_filename, file_type)
                if public_url:
                    media_urls.append(public_url)
        
        return media_urls
    
    def format_activity_for_display(self, activity):
        """Format activity data for display in tables"""
        formatted_activity = activity.copy()
        
        # Format timestamp
        if 'timestamp' in formatted_activity:
            try:
                dt = datetime.fromisoformat(formatted_activity['timestamp'].replace('Z', '+00:00'))
                formatted_activity['timestamp'] = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        # Format location
        if 'location' in formatted_activity and formatted_activity['location']:
            location = formatted_activity['location']
            if isinstance(location, dict):
                if location.get('description'):
                    formatted_activity['location'] = location['description']
                elif location.get('lat') and location.get('lng'):
                    formatted_activity['location'] = f"{location['lat']:.4f}, {location['lng']:.4f}"
                else:
                    formatted_activity['location'] = "Not specified"
            else:
                formatted_activity['location'] = str(location)
        else:
            formatted_activity['location'] = "Not specified"
        
        # Format tags
        if 'tags' in formatted_activity and formatted_activity['tags']:
            if isinstance(formatted_activity['tags'], list):
                formatted_activity['tags'] = ", ".join(formatted_activity['tags'])
        
        return formatted_activity