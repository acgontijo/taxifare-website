import datetime
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# Title of the app
st.title("🚕 Taxi Fare Predictor Deluxe 🚀")
st.subheader("Where are you heading today?")

# Initialize state variables for pickup and dropoff
if "pickup_set" not in st.session_state:
    st.session_state.pickup_set = False
    st.session_state.pickup_coords = None
    st.session_state.dropoff_coords = None

# Map for Pickup and Drop-off
st.markdown("### Select your pickup and drop-off locations on the map:")
map_center = [40.7831, -73.9712]  # NYC center
map_ = folium.Map(location=map_center, zoom_start=12)

# Display the map and get user-selected data
location_data = st_folium(map_, width=700, height=500)

# Handle pickup and dropoff logic based on map clicks
if location_data and "last_active_drawing" in location_data:
    if location_data["last_active_drawing"] and "geometry" in location_data["last_active_drawing"]:
        clicked_coords = location_data["last_active_drawing"]["geometry"]["coordinates"]
        if not st.session_state.pickup_set:
            st.session_state.pickup_coords = clicked_coords
            st.session_state.pickup_set = True
            st.success(f"Pickup location set to: {st.session_state.pickup_coords}")
        else:
            st.session_state.dropoff_coords = clicked_coords
            st.success(f"Dropoff location set to: {st.session_state.dropoff_coords}")

# Retrieve pickup and dropoff coordinates
pickup = st.session_state.pickup_coords or map_center
dropoff = st.session_state.dropoff_coords or map_center

# Input fields for date, time, and passenger count
pickup_date = st.date_input("📅 Enter date:", value=datetime.date.today())
pickup_time = st.time_input("⏰ Select the pickup time:", value=datetime.datetime.now().time())
passenger_count = st.slider("👥 Number of passengers:", min_value=1, max_value=6, value=1)

# Combine date and time into a single datetime string
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

# Dynamic fare estimate button
if st.button("✨ Get Your Funky Fare ✨"):
    # Validate coordinates before making API call
    if not pickup or not dropoff or len(pickup) != 2 or len(dropoff) != 2:
        st.error("Invalid coordinates for pickup or dropoff. Please select both locations on the map.")
    else:
        # Build the dictionary for the API call
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup[0],
            "pickup_latitude": pickup[1],
            "dropoff_longitude": dropoff[0],
            "dropoff_latitude": dropoff[1],
            "passenger_count": passenger_count
        }

        # Define the API endpoint
        url = 'https://taxifare.lewagon.ai/predict'

        try:
            # Call the API
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            prediction = response.json()

            # Display the prediction
            st.markdown("### 🤑 Your Estimated Fare is:")
            st.write(f"**${prediction['fare']:.2f}**")

            # Fun add-ons: emoji and dynamic fun facts
            st.markdown("🚀 **Did you know?** Taxi fares in NYC are highest during peak hours!")

            # Mapbox Directions API
            mapbox_token = "sk.eyJ1IjoiZ29udGlqbyIsImEiOiJjbTNzdXozNDYwMXUwMmxwY2V6YTlqN3A1In0.V01IDqMkfmgyB4Q0I7582g"  # Replace with your Mapbox token
            directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pickup[0]},{pickup[1]};{dropoff[0]},{dropoff[1]}"
            params = {"access_token": mapbox_token}
            directions_response = requests.get(directions_url, params=params)

            if directions_response.ok:
                st.success("Route successfully fetched!")
            else:
                st.error("Unable to fetch route directions.")

        except requests.RequestException as e:
            st.error(f"Error fetching data from the API: {e}")
