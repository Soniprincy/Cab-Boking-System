import streamlit as st
import requests

st.title("🚖 Cab Booking System")

# Required fields
firstname = st.text_input("First Name")
surname = st.text_input("Surname")
address = st.text_input("Address")
postcode = st.text_input("Postcode")
telephone = st.text_input("Telephone")
mobile = st.text_input("Mobile")
email = st.text_input("Email")

# Booking info
pickup = st.text_input("Pickup Location")
drop_location = st.text_input("Drop Location")
distance = st.number_input("Distance (km)", min_value=1.0, step=0.5)
time = st.number_input("Time (minutes)", min_value=1.0, step=1.0)
pooling = st.selectbox("Pooling?", ["Yes", "No"])
cab_type = st.selectbox("Cab Type", ["Sedan", "SUV", "Hatchback"])

if st.button("Book Cab"):
    payload = {
        "firstname": firstname,
        "surname": surname,
        "address": address,
        "postcode": postcode,
        "telephone": telephone,
        "mobile": mobile,
        "email": email,
        "pickup": pickup,
        "drop_location": drop_location,
        "drop": drop_location,
        "distance": distance,
        "time": time,
        "pooling": pooling.lower() == "yes",
        "cab_type": cab_type.lower()
    }

    try:
        res = requests.post("http://127.0.0.1:8000/calculate_fare/", json=payload)
        if res.status_code == 200:
            res_data = res.json()
            subtotal = res_data["subtotal"]
            tax = res_data["tax"]
            total_cost = res_data["total_cost"]
            st.success(f"✅ Cab booked!\nSubtotal: ₹{subtotal}\nTax: ₹{tax}\nTotal Fare: ₹{total_cost}")
        else:
            st.error(f"Error: {res.text}")
    except Exception as e:
        st.error(f"❌ Could not connect to backend: {e}")
