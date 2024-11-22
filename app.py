import datetime
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# Initialize session state for coordinates
if "pickup_coords" not in st.session_state:
    st.session_state.pickup_coords = None

if "dropoff_coords" not in st.session_state:
    st.session_state.dropoff_coords = None

# Title of the app
st.title("🚕 Taxi Fare Predictor Deluxe 🚀")
st.subheader("Where are you heading today?")

# Map for Pickup and Drop-off
st.markdown("### Select your pickup and drop-off locations on the map:")
map_center = [40.7831, -73.9712]  # NYC center
map_ = folium.Map(location=map_center, zoom_start=12)

# Add existing markers to the map if set
if st.session_state.pickup_coords:
    folium.Marker(
        location=st.session_state.pickup_coords,
        popup="Pickup Location",
        icon=folium.Icon(color="green"),
    ).add_to(map_)

if st.session_state.dropoff_coords:
    folium.Marker(
        location=st.session_state.dropoff_coords,
        popup="Dropoff Location",
        icon=folium.Icon(color="red"),
    ).add_to(map_)

# Add map click functionality
map_.add_child(folium.ClickForMarker(popup="Click to set location"))

# Display the map and get user-selected data
location_data = st_folium(map_, width=700, height=500)

# Handle pickup and dropoff logic based on map clicks
if location_data and "last_clicked" in location_data and location_data["last_clicked"]:
    clicked_coords = location_data["last_clicked"]

    if clicked_coords and isinstance(clicked_coords, list) and len(clicked_coords) == 2:
        if st.session_state.pickup_coords is None:
            st.session_state.pickup_coords = [clicked_coords[0], clicked_coords[1]]
            st.success(f"Pickup location set to: {st.session_state.pickup_coords}")
        elif st.session_state.dropoff_coords is None:
            st.session_state.dropoff_coords = [clicked_coords[0], clicked_coords[1]]
            st.success(f"Dropoff location set to: {st.session_state.dropoff_coords}")

# Ensure only valid coordinates are processed
if st.session_state.pickup_coords and st.session_state.dropoff_coords:
    st.markdown("### Route Details")
    pickup = st.session_state.pickup_coords
    dropoff = st.session_state.dropoff_coords

    # Call Mapbox Directions API
    MAPBOX_ACCESS_TOKEN = "sk.eyJ1IjoiZ29udGlqbyIsImEiOiJjbTNzdXozNDYwMXUwMmxwY2V6YTlqN3A1In0.V01IDqMkfmgyB4Q0I7582g"
    directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pickup[1]},{pickup[0]};{dropoff[1]},{dropoff[0]}"
    params = {"access_token": MAPBOX_ACCESS_TOKEN, "geometries": "geojson"}
    response = requests.get(directions_url, params=params)

    if response.status_code == 200:
        route_data = response.json()
        route_geometry = route_data["routes"][0]["geometry"]["coordinates"]

        # Add route to the map
        folium.PolyLine(
            locations=[list(reversed(coord)) for coord in route_geometry],
            color="blue",
            weight=5,
            opacity=0.8,
        ).add_to(map_)
        st_folium(map_, width=700, height=500)

        # Predict the fare
        pickup_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passenger_count = st.slider("👥 Number of passengers:", min_value=1, max_value=6, value=1)
        prediction_params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup[1],
            "pickup_latitude": pickup[0],
            "dropoff_longitude": dropoff[1],
            "dropoff_latitude": dropoff[0],
            "passenger_count": passenger_count,
        }
        fare_response = requests.get("https://taxifare.lewagon.ai/predict", params=prediction_params)
        fare_response.raise_for_status()
        fare_prediction = fare_response.json()

        st.markdown("### 🤑 Your Estimated Fare is:")
        st.write(f"**${fare_prediction['fare']:.2f}**")
    else:
        st.error("Failed to retrieve route details. Please try again.")
