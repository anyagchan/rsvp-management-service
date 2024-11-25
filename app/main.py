from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
def create_event_rsvp(event_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):

    # Create RSVP with associated event ID
    rsvp.event_id = event_id  # Set the event_id from the URL
    rsvp.event_name = "Event Name Placeholder"  # You may want to set this based on your external source
    return crud.create_rsvp(db=db, rsvp=rsvp)

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