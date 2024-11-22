import datetime
import streamlit as st
import requests

# Title of the app
st.title("Taxi Fare Model Prediction")
st.subheader("Select ride parameters")

# Input fields for the user
pickup_date = st.date_input("Enter date", value=datetime.date.today())
pickup_time = st.time_input("Select the pickup time", value=datetime.datetime.now().time())
pickup_longitude = st.number_input("Pickup Longitude")
pickup_latitude = st.number_input("Pickup Latitude")
dropoff_longitude = st.number_input("Drop-off Longitude")
dropoff_latitude = st.number_input("Drop-off Latitude")
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

    # Call the API
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    prediction = response.json()

    # Display the prediction
    st.subheader("Predicted Fare:")
    st.write(f"${prediction['fare']}")
