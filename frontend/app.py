import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

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

# ---------- PDF GENERATOR ----------
def generate_invoice_pdf(booking_data, invoice_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Cab Booking Invoice</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Customer Details
    customer_info = f"""
    <b>Customer:</b> {booking_data.get('firstname','')} {booking_data.get('surname','')}<br/>
    <b>Address:</b> {booking_data.get('address','')}, {booking_data.get('postcode','')}<br/>
    <b>Telephone:</b> {booking_data.get('telephone','')} | <b>Mobile:</b> {booking_data.get('mobile','')}<br/>
    <b>Email:</b> {booking_data.get('email','')}<br/>
    <b>Pickup:</b> {booking_data.get('pickup','')}<br/>
    <b>Drop:</b> {booking_data.get('drop_location','')}<br/>
    <b>Cab Type:</b> {booking_data.get('cab_type','')}<br/>
    """
    elements.append(Paragraph(customer_info, styles['Normal']))
    elements.append(Spacer(1, 20))

    # ✅ Format values as strings with ₹ symbol
    invoice_df["Amount (Rs)"] = invoice_df["Amount (Rs)"].apply(lambda x: f"Rs {x:.2f}")

    # Prepare table with fixed column widths
    data = [invoice_df.columns.tolist()] + invoice_df.values.tolist()
    table = Table(data, colWidths=[300, 100])  # force proper alignment

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    # Add heading + table
    elements.append(Paragraph("<b>Fare Breakdown</b>", styles['Heading2']))
    elements.append(table)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

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
        invoice_df = pd.DataFrame([
            {"Item": "Base Fare", "Amount (Rs)": round(base_charge)},
            {"Item": f"Distance Fare ({distance} km × Rs {rate}/km)", "Amount (Rs)": round(distance * rate)},
            {"Item": "Insurance", "Amount (Rs)": 10.0},
            {"Item": "Subtotal", "Amount (Rs)": round(subtotal)},
            {"Item": "Tax (9%)", "Amount (Rs)": round(tax)},
            {"Item": "Total Fare", "Amount (Rs)": round(total_cost)}
        ])
        st.table(invoice_df)

        # Generate invoice PDF
        pdf_data = generate_invoice_pdf(booking_data, invoice_df)

        # Download button
        st.download_button(
            label="📥 Download Invoice as PDF",
            data=pdf_data,
            file_name="cab_invoice.pdf",
            mime="application/pdf"
        )
