import datetime
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# Title of the app
st.title("Taxi Fare Prediction with Interactive Map")

# Input fields for the user
st.subheader("Select ride parameters")

# Set a default map center (New York City)
map_center = [40.7128, -74.0060]

# Initialize map
m = folium.Map(location=map_center, zoom_start=12)

# Add drawing capabilities to the map
folium.Marker(location=map_center, tooltip="Default pickup location").add_to(m)

# Render the map in Streamlit
location_data = st_folium(m, width=700, height=500)

# Handle pickup coordinates from map interaction
pickup_coords = map_center  # Default value

if location_data and "last_active_drawing" in location_data:
    if location_data["last_active_drawing"] and "geometry" in location_data["last_active_drawing"]:
        pickup_coords = location_data["last_active_drawing"]["geometry"].get("coordinates", map_center)

# Extract pickup latitude and longitude from coordinates
pickup_longitude, pickup_latitude = pickup_coords

# Additional inputs for the user
dropoff_longitude = st.number_input("Drop-off Longitude", value=-73.9857)
dropoff_latitude = st.number_input("Drop-off Latitude", value=40.7488)
pickup_date = st.date_input("Enter date", value=datetime.date.today())
pickup_time = st.time_input("Select the pickup time", value=datetime.datetime.now().time())
passenger_count = st.number_input("Enter passenger count", min_value=1, max_value=10, value=1)

# Combine date and time into a single datetime string
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

# Add a button to trigger the prediction
if st.button("Get Fare Prediction"):
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
        st.subheader("Predicted Fare:")
        st.write(f"${prediction['fare']:.2f}")

    except requests.exceptions.RequestException as e:
        st.error("Error connecting to the prediction API.")
        st.error(str(e))
