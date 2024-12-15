from pydantic import BaseModel

class RSVPBase(BaseModel):
    event_id: int
    event_name: str  
    email: str
    status: str

class RSVPCreate(RSVPBase):
    pass

class RSVPUpdate(BaseModel):
    status: str

class RSVP(RSVPBase):
    id: int

    class Config:
        orm_mode = True