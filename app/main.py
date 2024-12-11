from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
import httpx
import json  # Import JSON for serialization

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#connection to events:
EVENT_SERVICE_URL = "http://0.0.0.0:8001"


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the RSVP Management Service!"}

@app.post("/events/{event_id}/rsvps/", response_model=schemas.RSVP)
async def create_event_rsvp(event_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # Fetch the existing event data
        event_response = await client.get(f"{EVENT_SERVICE_URL}/events/{event_id}")
        event_data = event_response.json()

        rsvp.event_id = event_id
        rsvp.event_name = event_data.get("name", "Event Name Placeholder")

        # Create RSVP in our database
        created_rsvp = crud.create_rsvp(db=db, rsvp=rsvp)

        # Update RSVP count and structure the updated data
        updated_data = {
            "id": event_data['id'],
            "organizationId": event_data['organizationId'],
            "name": event_data['name'],
            "description": event_data['description'],
            "date": event_data['date'],
            "time": (str) (event_data['time']),
            "location": event_data['location'],
            "category": event_data['category'],
            "rsvpCount": event_data['rsvpCount'] + 1
        }
        
        with open("output.txt", "w") as file:
            json.dump(updated_data, file, indent=4)  # Writing JSON data with indentation for readability
            
        update_response = await client.put(f"{EVENT_SERVICE_URL}/events/{event_id}", json=updated_data)
        
        
        print("Status code:", update_response.status_code)
        print("Response content:", update_response.text)


    return created_rsvp


@app.get("/events/{event_id}/rsvps/", response_model=list[schemas.RSVP])
def read_event_rsvps(event_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rsvps_for_event(db=db, event_id=event_id, skip=skip, limit=limit)

@app.get("/rsvps/{rsvp_id}", response_model=schemas.RSVP)
def read_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    db_rsvp = crud.get_rsvp(db=db, rsvp_id=rsvp_id)
    if not db_rsvp:
        raise HTTPException(status_code=404, detail="RSVP not found")
    return db_rsvp

@app.put("/rsvps/{rsvp_id}", response_model=schemas.RSVP)
def update_rsvp(rsvp_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):
    updated_rsvp = crud.update_rsvp(db=db, rsvp_id=rsvp_id, rsvp=rsvp)
    if not updated_rsvp:
        raise HTTPException(status_code=404, detail="RSVP not found")
    return updated_rsvp

@app.delete("/rsvps/{rsvp_id}", response_model=schemas.RSVP)
def delete_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    deleted_rsvp = crud.delete_rsvp(db=db, rsvp_id=rsvp_id)
    if not deleted_rsvp:
        raise HTTPException(status_code=404, detail="RSVP not found")
    return deleted_rsvp