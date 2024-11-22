import datetime
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# Title of the app
st.title("🚕 Taxi Fare Predictor Deluxe 🚀")
st.subheader("Where are you heading today?")

# Map for Pickup and Drop-off
st.markdown("### Select your pickup and drop-off locations on the map:")
map_center = [40.7831, -73.9712]  # NYC center
map_ = folium.Map(location=map_center, zoom_start=12)

# Add markers for user selection
folium.Marker(location=map_center, popup="Default Pickup Location", draggable=False).add_to(map_)

# Display the map and get user-selected data
location_data = st_folium(map_, width=700, height=500)

# Default pickup and dropoff coordinates (in case of no interaction)
pickup_coords = map_center
dropoff_coords = map_center

# Handle pickup coordinates from map interaction safely
if location_data:
    if "last_clicked" in location_data and location_data["last_clicked"]:
        pickup_coords = location_data["last_clicked"].get("lat_lng", map_center)

# Allow user to enter dropoff coordinates if needed
st.markdown("### Fine-tune your locations below:")
pickup_longitude = st.number_input("Pickup Longitude", value=pickup_coords[1])
pickup_latitude = st.number_input("Pickup Latitude", value=pickup_coords[0])
dropoff_longitude = st.number_input("Drop-off Longitude", value=-73.9857)
dropoff_latitude = st.number_input("Drop-off Latitude", value=40.7488)

# Input fields for date, time, and passenger count
pickup_date = st.date_input("📅 Enter date:", value=datetime.date.today())
pickup_time = st.time_input("⏰ Select the pickup time:", value=datetime.datetime.now().time())
passenger_count = st.slider("👥 Number of passengers:", min_value=1, max_value=6, value=1)

# Combine date and time into a single datetime string
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

# Dynamic fare estimate button
if st.button("✨ Get Your Funky Fare ✨"):
    # Build the dictionary for the API call
    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
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

    except requests.exceptions.RequestException as e:
        st.error("Error connecting to the prediction API.")
        st.error(str(e))
