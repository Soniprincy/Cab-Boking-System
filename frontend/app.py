import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# ---------- DB CONNECTION ----------
engine = create_engine("sqlite:///cab_booking.db")

# ---------- INIT DATABASE ----------
with engine.begin() as conn:
    conn.execute(text("""
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
            subtotal REAL,
            tax REAL,
            total_cost REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

# ---------- SAVE BOOKING ----------
def save_booking(data):
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO Bookings (
                    firstname, surname, address, postcode, telephone, mobile, email,
                    pickup, drop_location, pooling, cab_type, distance,
                    subtotal, tax, total_cost
                ) VALUES (
                    :firstname, :surname, :address, :postcode, :telephone, :mobile, :email,
                    :pickup, :drop_location, :pooling, :cab_type, :distance,
                    :subtotal, :tax, :total_cost
                )
            """), data)
        return True
    except Exception as e:
        st.error(f"❌ Database insert error: {e}")
        return False

# ---------- FETCH BOOKINGS ----------
def fetch_bookings():
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT * FROM Bookings ORDER BY created_at DESC"))
            rows = result.fetchall()
            if rows:
                return pd.DataFrame(rows, columns=result.keys())
            else:
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Could not fetch bookings: {e}")
        return pd.DataFrame()

# ---------- STREAMLIT UI ----------
st.title("🚖 Cab Booking System")

# Cab pricing table
st.subheader("📌 Cab Pricing Details")
cab_rates = {"Standard": 15, "Galaxy": 20, "Mondeo": 22}
base_charge = 50
st.table(pd.DataFrame([
    {"Cab Type": "Standard", "Rate/km": 15},
    {"Cab Type": "Galaxy", "Rate/km": 20},
    {"Cab Type": "Mondeo", "Rate/km": 22}
]))

# Booking form
st.subheader("📝 Enter Your Booking Details")
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
pooling = st.selectbox("Pooling?", ["Yes", "No"])
cab_type = st.selectbox("Cab Type", ["Standard", "Galaxy", "Mondeo"])

# Book cab button
if st.button("Book Cab"):
    rate = cab_rates.get(cab_type, 15)
    subtotal = base_charge + (distance * rate) + 10.0  # includes insurance
    tax = subtotal * 0.09
    total_cost = subtotal + tax

    booking_data = {
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
        "subtotal": subtotal,
        "tax": tax,
        "total_cost": total_cost
    }

    if save_booking(booking_data):
        st.success("✅ Cab booked successfully!")

        # Fare breakdown
        st.subheader("💰 Fare Breakdown")
        st.table(pd.DataFrame([
            {"Item": "Base Fare", "Amount (₹)": round(base_charge)},
            {"Item": f"Distance Fare ({distance} km × ₹{rate}/km)", "Amount (₹)": round(distance * rate)},
            {"Item": "Insurance", "Amount (₹)": 10.0},
            {"Item": "Subtotal", "Amount (₹)": round(subtotal)},
            {"Item": "Tax (9%)", "Amount (₹)": round(tax)},
            {"Item": "Total Fare", "Amount (₹)": round(total_cost)}
        ]))
