import streamlit as st
import sqlite3

st.title("🚖 Cab Booking System")

# Database setup (SQLite)
conn = sqlite3.connect("cab_bookings.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS Bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT,
    surname TEXT,
    address TEXT,
    postcode TEXT,
    telephone TEXT,
    mobile TEXT,
    email TEXT,
    pickup TEXT,
    drop_location TEXT,
    pooling INTEGER,
    cab_type TEXT,
    distance REAL,
    time REAL,
    extra_luggage REAL,
    insurance REAL,
    subtotal REAL,
    tax REAL,
    total_cost REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Form inputs
firstname = st.text_input("First Name")
surname = st.text_input("Surname")
address = st.text_input("Address")
postcode = st.text_input("Postcode")
telephone = st.text_input("Telephone")
mobile = st.text_input("Mobile")
email = st.text_input("Email")

pickup = st.text_input("Pickup Location")
drop_location = st.text_input("Drop Location")
distance = st.number_input("Distance (km)", min_value=1.0, step=0.5)
time_val = st.number_input("Time (minutes)", min_value=1.0, step=1.0)
pooling = st.selectbox("Pooling?", ["Yes", "No"])
cab_type = st.selectbox("Cab Type", ["Sedan", "SUV", "Hatchback"])

extra_luggage = st.number_input("Extra Luggage Charge", min_value=0.0, step=1.0, value=0.0)
insurance = st.number_input("Insurance", min_value=0.0, step=1.0, value=10.0)

# Fare calculation function
def calculate_fare(data):
    cab_rates = {"Sedan": 15, "SUV": 20, "Hatchback": 12}
    base_charge = 50
    rate = cab_rates.get(data["cab_type"].capitalize(), 15)
    subtotal = base_charge + (data["distance"] * rate) + data["extra_luggage"] + data["insurance"]
    tax = subtotal * 0.09
    total = subtotal + tax
    return subtotal, tax, total

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
        "pooling": 1 if pooling.lower() == "yes" else 0,
        "cab_type": cab_type,
        "distance": distance,
        "time": time_val,
        "extra_luggage": extra_luggage,
        "insurance": insurance
    }

    subtotal, tax, total_cost = calculate_fare(payload)

    # Save to DB
    c.execute("""
        INSERT INTO Bookings (
            firstname, surname, address, postcode, telephone, mobile, email,
            pickup, drop_location, pooling, cab_type, distance, time, extra_luggage,
            insurance, subtotal, tax, total_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        firstname, surname, address, postcode, telephone, mobile, email,
        pickup, drop_location, payload["pooling"], cab_type, distance, time_val,
        extra_luggage, insurance, subtotal, tax, total_cost
    ))
    conn.commit()

    st.success(f"✅ Cab booked!\nSubtotal: ₹{subtotal}\nTax: ₹{tax}\nTotal Fare: ₹{total_cost}")
