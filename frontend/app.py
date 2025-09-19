import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

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
# Show cab pricing details
# -------------------------
st.subheader("💰 Fare Pricing Details")
st.markdown("""
- **Base Charge:** ₹50  
- **Cab Rates per km:**  
  - 🚗 Standard Cab → ₹15/km  
  - 🚙 Galaxy Cab → ₹20/km  
  - 🚘 Mondeo Cab → ₹22/km  
- **Travelling Insurance:** ₹10  
- **Extra Luggage:** Custom (₹10/kg)  
- **Tax:** 9% on subtotal  
""")

# -------------------------
# Booking form
# -------------------------
with st.form("booking_form"):
    st.subheader("📋 Enter Customer & Trip Details")

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
        # Pricing details
        cab_rates = {"Standard": 15, "Galaxy": 20, "Mondeo": 22}
        base_charge = 50
        insurance = 10.0
        tax_rate = 0.09

        # Fare calculation
        rate = cab_rates.get(cab_type, 15)
        subtotal = base_charge + (distance * rate) + extra_luggage + insurance
        tax = subtotal * tax_rate
        total = subtotal + tax

        # Insert into database
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

        st.success("✅ Cab booked successfully!")

        # -------------------------
        # Show receipt table
        # -------------------------
        receipt_data = {
            "Field": [
                "Firstname", "Surname", "Address", "Postcode", "Telephone", "Mobile", "Email",
                "Pickup", "Drop", "Pooling", "Cab Type", "Distance (km)",
                "Extra Luggage", "Insurance", "Subtotal", "Tax (9%)", "Total Fare"
            ],
            "Value": [
                firstname, surname, address, postcode, telephone, mobile, email,
                pickup, drop, pooling, cab_type, distance,
                extra_luggage, insurance, f"₹{subtotal:.2f}", f"₹{tax:.2f}", f"₹{total:.2f}"
            ]
        }

        df = pd.DataFrame(receipt_data)
        st.subheader("🧾 Booking Receipt")
        st.table(df)

    except Exception as e:
        st.error(f"❌ Could not connect to database: {e}")
