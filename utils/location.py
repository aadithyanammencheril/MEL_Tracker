import streamlit as st
import geocoder
from streamlit_geolocation import streamlit_geolocation

def gps_location_handler():
    """Handle location detection using IP geolocation and GPS fallback"""
    st.subheader("📍 Auto Location Detection")
    st.write("Get your current location automatically (use this before filling the form)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌐 Get IP Location", help="Get location based on your IP address (fast & reliable)"):
            try:
                with st.spinner("🔄 Getting your location..."):
                    g = geocoder.ip('me')
                    
                if g.latlng and len(g.latlng) == 2:
                    # Successfully got IP-based location
                    if "location_data" not in st.session_state:
                        st.session_state.location_data = {"lat": None, "lng": None, "description": ""}
                    
                    st.session_state.location_data["lat"] = g.latlng[0]
                    st.session_state.location_data["lng"] = g.latlng[1]
                    
                    # Create a descriptive location string
                    location_desc = []
                    if g.city:
                        location_desc.append(g.city)
                    if g.state:
                        location_desc.append(g.state)
                    if g.country:
                        location_desc.append(g.country)
                    
                    description = ", ".join(location_desc) if location_desc else "Unknown Location"
                    st.session_state.location_data["description"] = description
                    
                    st.success(f"📍 Location detected: {description}")
                    st.success(f"🌍 Coordinates: {g.latlng[0]:.4f}, {g.latlng[1]:.4f}")
                    st.info("✅ Now you can proceed to fill the activity form below.")
                else:
                    st.error("❌ Could not determine location from IP address")
                    st.info("This might happen if you're using a VPN or proxy.")
                    
            except Exception as e:
                st.error(f"❌ IP location error: {str(e)}")
                st.info("Please use manual location entry or try GPS method.")
    
    with col2:
        if st.button("📡 Get GPS Location", help="Get precise GPS coordinates (requires permission)"):
            try:
                location = streamlit_geolocation()
                
                # Handle the different states of the geolocation component
                if location == "No Location Info":
                    st.warning("🔄 Waiting for location permission...")
                    st.info("Please allow location access in your browser and click the button again.")
                elif isinstance(location, dict) and location.get("latitude") is not None and location.get("longitude") is not None:
                    # Successfully got GPS coordinates
                    if "location_data" not in st.session_state:
                        st.session_state.location_data = {"lat": None, "lng": None, "description": ""}
                    st.session_state.location_data["lat"] = location["latitude"]
                    st.session_state.location_data["lng"] = location["longitude"]
                    st.success(f"📍 GPS location captured: {location['latitude']:.6f}, {location['longitude']:.6f}")
                    st.info("✅ Now you can proceed to fill the activity form below.")
                    
                    # Show accuracy info if available
                    if location.get("accuracy"):
                        st.info(f"🎯 GPS accuracy: ±{location['accuracy']:.0f} meters")
                elif isinstance(location, dict) and (location.get("latitude") is None or location.get("longitude") is None):
                    st.error("❌ GPS returned empty coordinates")
                    st.info("💡 Try the IP Location button instead - it's more reliable!")
                else:
                    st.warning("⚠️ GPS not available")
                    st.info("💡 Use IP Location instead!")
                    
            except Exception as e:
                st.error(f"❌ GPS error: {str(e)}")
                st.info("💡 Try the IP Location button instead!")

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