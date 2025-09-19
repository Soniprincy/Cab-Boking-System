import streamlit as st
import pyodbc

st.title("🚖 Cab Booking System")

# Database connection
def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=PRINCY\\MSSQL;"  # adjust your SQL Server instance
        "DATABASE=CabBookingDB;"
        "UID=sa;"                # your SQL username
        "PWD=2002;"              # your SQL password
    )
    return conn

# Insert booking into DB
def save_booking(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Bookings (
            firstname, surname, address, postcode, telephone, mobile, email,
            pickup, drop_location, pooling, cab_type, distance,
            subtotal, tax, total_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["firstname"], data["surname"], data["address"], data["postcode"],
        data["telephone"], data["mobile"], data["email"], data["pickup"],
        data["drop_location"], int(data["pooling"]), data["cab_type"],
        data["distance"], data["subtotal"], data["tax"], data["total_cost"]
    ))
    conn.commit()
    conn.close()

# --- Streamlit form ---
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

if st.button("Book Cab"):
    # Fare calculation
    cab_rates = {"Standard": 15, "Galaxy": 20, "Mondeo": 22}
    base_charge = 50
    rate = cab_rates.get(cab_type, 15)

    subtotal = base_charge + (distance * rate) + 10.0  # default insurance
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
        "pooling": pooling.lower() == "yes",
        "cab_type": cab_type,
        "distance": distance,
        "subtotal": subtotal,
        "tax": tax,
        "total_cost": total_cost
    }

    try:
        save_booking(booking_data)
        st.success(f"✅ Cab booked!\nSubtotal: ₹{subtotal}\nTax: ₹{tax}\nTotal Fare: ₹{total_cost}")
    except Exception as e:
        st.error(f"❌ Database error: {e}")
