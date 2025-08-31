import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase_client() -> Client:
    """Get cached Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase environment variables. Check your .env file.")
    
    return create_client(url, key)

def test_connection() -> bool:
    """Test connection to Supabase"""
    try:
        client = get_supabase_client()
        # Try a simple query to test connection
        result = client.table("activities").select("count").execute()
        return True
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return False