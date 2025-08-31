import streamlit as st
from streamlit_geolocation import streamlit_geolocation

def gps_location_handler():
    """Handle GPS location outside of forms"""
    st.subheader("📡 GPS Location")
    st.write("Get your current GPS coordinates (use this before filling the form)")
    
    if st.button("📡 Get GPS Location", help="Click to get your current GPS coordinates"):
        try:
            location = streamlit_geolocation()
            if location and location.get("latitude") and location.get("longitude"):
                if "location_data" not in st.session_state:
                    st.session_state.location_data = {"lat": None, "lng": None, "description": ""}
                st.session_state.location_data["lat"] = location["latitude"]
                st.session_state.location_data["lng"] = location["longitude"]
                st.success(f"GPS location captured: {location['latitude']:.4f}, {location['longitude']:.4f}")
                st.info("Now you can proceed to fill the activity form below.")
            else:
                st.error("Could not get GPS location. Please use manual entry in the form.")
        except Exception as e:
            st.error(f"GPS error: {str(e)}. Please use manual entry in the form.")

def location_handler():
    """Handle location input with GPS + manual fallback - Form compatible version"""
    
    st.subheader("📍 Location")
    
    # Initialize location in session state
    if "location_data" not in st.session_state:
        st.session_state.location_data = {"lat": None, "lng": None, "description": ""}
    
    # Manual location input (form-compatible)
    manual_location = st.text_input(
        "Location Description",
        value=st.session_state.location_data["description"],
        placeholder="Home, Office, Central Park...",
        help="Enter a description of your location"
    )
    st.session_state.location_data["description"] = manual_location
    
    # GPS coordinates (manual entry for form compatibility)
    col1, col2 = st.columns(2)
    with col1:
        lat_input = st.number_input(
            "Latitude (optional)",
            value=st.session_state.location_data["lat"] if st.session_state.location_data["lat"] else 0.0,
            format="%.6f",
            help="Enter latitude if you have GPS coordinates"
        )
        if lat_input != 0.0:
            st.session_state.location_data["lat"] = lat_input
    
    with col2:
        lng_input = st.number_input(
            "Longitude (optional)",
            value=st.session_state.location_data["lng"] if st.session_state.location_data["lng"] else 0.0,
            format="%.6f", 
            help="Enter longitude if you have GPS coordinates"
        )
        if lng_input != 0.0:
            st.session_state.location_data["lng"] = lng_input
    
    # Display current location status
    if st.session_state.location_data["lat"] and st.session_state.location_data["lng"]:
        st.info(f"🌍 GPS: {st.session_state.location_data['lat']:.4f}, {st.session_state.location_data['lng']:.4f}")
    
    if st.session_state.location_data["description"]:
        st.info(f"📝 Description: {st.session_state.location_data['description']}")
    
    if not st.session_state.location_data["lat"] and not st.session_state.location_data["description"]:
        st.info("📍 Location: Not specified")
    
    return get_location_data()

def get_location_data():
    """Get formatted location data for database storage"""
    location_data = st.session_state.get("location_data", {"lat": None, "lng": None, "description": ""})
    
    return {
        "lat": location_data["lat"],
        "lng": location_data["lng"], 
        "description": location_data["description"] if location_data["description"] else "Not specified"
    }

def clear_location():
    """Clear location data from session state"""
    st.session_state.location_data = {"lat": None, "lng": None, "description": ""}