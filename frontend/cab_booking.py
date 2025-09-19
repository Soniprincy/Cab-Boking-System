import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///cab_booking.db")

# Fetch all bookings
df = pd.read_sql("SELECT * FROM Bookings ORDER BY created_at DESC", engine)

print(df)  # or df.head() to see first few rows
