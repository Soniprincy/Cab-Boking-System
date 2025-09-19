from pydantic import BaseModel

class BookingCreate(BaseModel):
    pickup: str
    drop_location: str
    distance: float
    time: float

class BookingResponse(BaseModel):
    fare: float
