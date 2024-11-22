import datetime
import requests
import streamlit as st
from streamlit_folium import st_folium
import folium

# Mapbox API key
mapbox_api_key = "sk.eyJ1IjoiZ29udGlqbyIsImEiOiJjbTNzdXozNDYwMXUwMmxwY2V6YTlqN3A1In0.V01IDqMkfmgyB4Q0I7582g"

# Title of the app
st.title("🚕 Taxi Fare Predictor Deluxe 🚀")
st.subheader("Where are you heading today?")

# Map for Pickup and Drop-off
st.markdown("### Select your pickup and drop-off locations on the map:")
map_center = [40.7831, -73.9712]  # NYC center
map_ = folium.Map(location=map_center, zoom_start=12)

# Display the map and get user-selected data
location_data = st_folium(map_, width=700, height=500)

# Session state for pickup and dropoff
if "pickup_coords" not in st.session_state:
    st.session_state["pickup_coords"] = None

if "dropoff_coords" not in st.session_state:
    st.session_state["dropoff_coords"] = None

# Check for map clicks to capture coordinates
if location_data and "last_active_drawing" in location_data:
    if location_data["last_active_drawing"] and "geometry" in location_data["last_active_drawing"]:
        if not pickup_set:
            pickup = location_data["last_active_drawing"]["geometry"]["coordinates"]
            pickup_set = True
            st.success("Pickup location set!")
        else:
            dropoff = location_data["last_active_drawing"]["geometry"]["coordinates"]
            st.success("Dropoff location set!")
            # Make sure to validate the coordinates
            if len(pickup) == 2 and len(dropoff) == 2:
                route_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pickup[1]},{pickup[0]};{dropoff[1]},{dropoff[0]}"
            else:
                st.error("Invalid coordinates for pickup or dropoff!")

# Show selected pickup and dropoff
if st.session_state["pickup_coords"]:
    st.write(f"**Pickup Coordinates:** {st.session_state['pickup_coords']}")

if st.session_state["dropoff_coords"]:
    st.write(f"**Dropoff Coordinates:** {st.session_state['dropoff_coords']}")

# Calculate and show route
if st.session_state["pickup_coords"] and st.session_state["dropoff_coords"]:
    pickup = st.session_state["pickup_coords"]
    dropoff = st.session_state["dropoff_coords"]

    # Use Mapbox Directions API
    mapbox_url = (
        f"https://api.mapbox.com/directions/v5/mapbox/driving/"
        f"{pickup[1]},{pickup[0]};{dropoff[1]},{dropoff[0]}"
        f"?geometries=geojson&access_token={mapbox_api_key}"
    )
    response = requests.get(mapbox_url)

    if response.status_code == 200:
        data = response.json()
        route = data["routes"][0]["geometry"]["coordinates"]
        st.session_state["route"] = route

        # Draw the route on the map
        folium.PolyLine(
            locations=[[point[1], point[0]] for point in route],
            color="blue",
            weight=5,
        ).add_to(map_)

        # Update map display
        st_folium(map_, width=700, height=500)
    else:
        st.error("Failed to retrieve route. Please try again.")
else:
    st.info("Click on the map to select both Pickup and Dropoff locations.")

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
        "pickup_longitude": st.session_state["pickup_coords"][1],
        "pickup_latitude": st.session_state["pickup_coords"][0],
        "dropoff_longitude": st.session_state["dropoff_coords"][1],
        "dropoff_latitude": st.session_state["dropoff_coords"][0],
        "passenger_count": passenger_count,
    }

    # Define the API endpoint
    url = 'https://taxifare.lewagon.ai/predict'

    # Call the API
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    prediction = response.json()

    # Display the prediction
    st.markdown("### 🤑 Your Estimated Fare is:")
    st.write(f"**${prediction['fare']:.2f}**")

    # Fun add-ons: emoji and dynamic fun facts
    st.markdown("🚀 **Did you know?** Taxi fares in NYC are highest during peak hours!")
