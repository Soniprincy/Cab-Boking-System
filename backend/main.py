from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

app = FastAPI()

# DB connection
server = "PRINCY%5CMSSQL"   # 👈 encoded backslash
database = "CabBookingDB"
username = "sa"
password = "2002"

connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(connection_string)

# Booking model
class BookingRequest(BaseModel):
    firstname: str
    surname: str
    address: str
    postcode: str
    telephone: str
    mobile: str
    email: str
    pickup: str
    drop: str
    pooling: bool
    cab_type: str
    distance: float
    extra_luggage: float = 0.0
    insurance: float = 10.0

@app.post("/calculate_fare/")
def calculate_fare(req: BookingRequest):
    try:
        cab_rates = {"Standard": 15, "Galaxy": 20, "Mondeo": 22}
        base_charge = 50

        rate = cab_rates.get(req.cab_type.capitalize(), 15)
        subtotal = base_charge + (req.distance * rate) + req.extra_luggage + req.insurance
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
            """), {**req.dict(), "subtotal": subtotal, "tax": tax, "total_cost": total})

        return {"subtotal": subtotal, "tax": tax, "total_cost": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
