import streamlit as st
from sqlalchemy import create_engine, text

# -------------------------
# Database connection
# -------------------------
server = "PRINCY\\MSSQL"
database = "CabBookingDB"
username = "sa"
password = "2002"

connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
engine = create_engine(connection_string)

st.title("🚖 Cab Booking System")

# -------------------------
# User form
# -------------------------
with st.form("booking_form"):
    firstname = st.text_input("First Name")
    surname = st.text_input("Surname")
    address = st.text_input("Address")
    postcode = st.text_input("Postcode")
    telephone = st.text_input("Telephone")
    mobile = st.text_input("Mobile")
    email = st.text_input("Email")

    pickup = st.text_input("Pickup Location")
    drop = st.text_input("Drop Location")
    distance = st.number_input("Distance (km)", min_value=1.0, step=0.5)
    pooling = st.selectbox("Pooling?", ["Yes", "No"])
    cab_type = st.selectbox("Cab Type", ["Standard", "Galaxy", "Mondeo"])
    extra_luggage = st.number_input("Extra Luggage (₹)", min_value=0.0, step=5.0)

    submitted = st.form_submit_button("Book Cab")

# -------------------------
# Fare calculation + DB insert
# -------------------------
if submitted:
    try:
        # Cab rates
        cab_rates = {"Standard": 15, "Galaxy": 20, "Mondeo": 22}
        base_charge = 50
        insurance = 10.0

        rate = cab_rates.get(cab_type, 15)
        subtotal = base_charge + (distance * rate) + extra_luggage + insurance
        tax = subtotal * 0.09
        total = subtotal + tax

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO Bookings (
                    firstname, surname, address, postcode, telephone, mobile, email,
                    pickup, drop_location, pooling, cab_type, distance,
                    extra_luggage, insurance, subtotal, tax, total_cost
                ) VALUES (
                    :firstname, :surname, :address, :postcode, :telephone, :mobile, :email,
                    :pickup, :drop, :pooling, :cab_type, :distance,
                    :extra_luggage, :insurance, :subtotal, :tax, :total_cost
                )
            """), {
                "firstname": firstname,
                "surname": surname,
                "address": address,
                "postcode": postcode,
                "telephone": telephone,
                "mobile": mobile,
                "email": email,
                "pickup": pickup,
                "drop": drop,
                "pooling": pooling.lower() == "yes",
                "cab_type": cab_type,
                "distance": distance,
                "extra_luggage": extra_luggage,
                "insurance": insurance,
                "subtotal": subtotal,
                "tax": tax,
                "total_cost": total,
            })

        st.success(
            f"✅ Cab booked!\n\n"
            f"Subtotal: ₹{subtotal:.2f}\n"
            f"Tax: ₹{tax:.2f}\n"
            f"Total Fare: ₹{total:.2f}"
        )

    except Exception as e:
        st.error(f"❌ Could not connect to database: {e}")
