from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Booking(Base):
    __tablename__ = "Bookings"   # Make sure this table exists in CabBookingDB

    id = Column(Integer, primary_key=True, index=True)
    pickup = Column(String(255))
    drop_location = Column(String(255))
    distance = Column(Float)
    time = Column(Float)
    fare = Column(Float)
