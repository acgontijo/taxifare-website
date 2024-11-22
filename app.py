import datetime
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

# Title of the app
st.title("🚕 Taxi Fare Predictor Deluxe 🚀")
st.subheader("Where are you heading today?")

# Initialize state variables for pickup and dropoff
if "pickup_coords" not in st.session_state:
    st.session_state.pickup_coords = None
    st.session_state.dropoff_coords = None

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
if location_data and "last_clicked" in location_data:
    clicked_coords = location_data["last_clicked"]

    if clicked_coords and isinstance(clicked_coords, list) and len(clicked_coords) == 2:
        if st.session_state.pickup_coords is None:
            st.session_state.pickup_coords = [clicked_coords[0], clicked_coords[1]]
            st.success(f"Pickup location set to: {st.session_state.pickup_coords}")
        elif st.session_state.dropoff_coords is None:
            st.session_state.dropoff_coords = [clicked_coords[0], clicked_coords[1]]
            st.success(f"Dropoff location set to: {st.session_state.dropoff_coords}")
    else:
        st.error("Invalid coordinates. Please click again.")
# Input fields for date, time, and passenger count
pickup_date = st.date_input("📅 Enter date:", value=datetime.date.today())
pickup_time = st.time_input("⏰ Select the pickup time:", value=datetime.datetime.now().time())
passenger_count = st.slider("👥 Number of passengers:", min_value=1, max_value=6, value=1)

# Combine date and time into a single datetime string
pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

# Dynamic fare estimate button
if st.button("✨ Get Your Funky Fare ✨"):
    # Validate coordinates before making API call
    if not st.session_state.pickup_coords or not st.session_state.dropoff_coords:
        st.error("Please select both pickup and dropoff locations on the map.")
    else:
        # Build the dictionary for the API call
        pickup = st.session_state.pickup_coords
        dropoff = st.session_state.dropoff_coords
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup[1],
            "pickup_latitude": pickup[0],
            "dropoff_longitude": dropoff[1],
            "dropoff_latitude": dropoff[0],
            "passenger_count": passenger_count
        }

        # Define the API endpoint
        url = 'https://taxifare.lewagon.ai/predict'

        try:
            # Call the Taxi Fare Prediction API
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            prediction = response.json()

            # Display the prediction
            st.markdown("### 🤑 Your Estimated Fare is:")
            st.write(f"**${prediction['fare']:.2f}**")

            # Mapbox Directions API for the route
            mapbox_token = "sk.eyJ1IjoiZ29udGlqbyIsImEiOiJjbTNzdXozNDYwMXUwMmxwY2V6YTlqN3A1In0.V01IDqMkfmgyB4Q0I7582g"  # Replace with your Mapbox token
            directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pickup[1]},{pickup[0]};{dropoff[1]},{dropoff[0]}"
            directions_params = {"access_token": mapbox_token, "geometries": "geojson"}
            directions_response = requests.get(directions_url, params=directions_params)

            if directions_response.ok:
                route = directions_response.json()
                if route and "routes" in route and len(route["routes"]) > 0:
                    route_coords = route["routes"][0]["geometry"]["coordinates"]
                    st.success("Route successfully fetched!")

                    # Add the route to the map
                    folium.PolyLine(
                        locations=[[lat, lon] for lon, lat in route_coords],
                        color="blue",
                        weight=5,
                        opacity=0.7,
                    ).add_to(map_)
                    st_folium(map_, width=700, height=500)
                else:
                    st.error("No route found.")
            else:
                st.error("Unable to fetch route directions.")

        except requests.RequestException as e:
            st.error(f"Error fetching data from the API: {e}")
