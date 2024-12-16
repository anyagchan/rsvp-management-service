from fastapi import Depends, FastAPI, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware


# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify allowed origins here
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

### middleware logging 
import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
logging.basicConfig(
    filename="app.log",               
    level=logging.INFO,                
    format="%(asctime)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)
models.Base.metadata.create_all(bind=engine)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4()
        request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info(f"[{request_id}] Request received at {request_time}: {request.method} {request.url.path}")

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info(
        f"[{request_id}] Response completed at {response_time}: "
        f"Status {response.status_code} {request.url.path}, "
        f"Processing time: {process_time:.2f} seconds"
        )
        return response
app.add_middleware(LoggingMiddleware)

### 

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": "Welcome to the RSVP Management Service!"}

@app.post("/events/{event_id}/rsvps/", response_model=schemas.RSVP, status_code=status.HTTP_201_CREATED)
def create_event_rsvp(event_id: int, rsvp: schemas.RSVPCreate, response: Response, db: Session = Depends(get_db)):
    # Create RSVP with associated event ID
    rsvp.event_id = event_id  # Set the event_id from the URL
    rsvp.event_name = "Event Name Placeholder"  # You may want to set this based on your external source

    new_rsvp = crud.create_rsvp(db=db, rsvp=rsvp)
    
    # Set the Link header pointing to the newly created resource
    response.headers["Link"] = f"</rsvps/{new_rsvp.id}>; rel=\"self\""

    return new_rsvp

@app.get("/events/{event_id}/rsvps/", response_model=list[schemas.RSVP], status_code=status.HTTP_200_OK)
def read_event_rsvps(event_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rsvps_for_event(db=db, event_id=event_id, skip=skip, limit=limit)

@app.get("/rsvps/{rsvp_id}", response_model=schemas.RSVP, status_code=status.HTTP_200_OK)
def read_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    db_rsvp = crud.get_rsvp(db=db, rsvp_id=rsvp_id)
    if not db_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return db_rsvp

@app.put("/rsvps/{rsvp_id}", response_model=schemas.RSVP, status_code=status.HTTP_200_OK)
def update_rsvp(rsvp_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):
    updated_rsvp = crud.update_rsvp(db=db, rsvp_id=rsvp_id, rsvp=rsvp)
    if not updated_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return updated_rsvp

@app.delete("/rsvps/{rsvp_id}", response_model=schemas.RSVP, status_code=status.HTTP_200_OK)
def delete_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    deleted_rsvp = crud.delete_rsvp(db=db, rsvp_id=rsvp_id)
    if not deleted_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return deleted_rsvp