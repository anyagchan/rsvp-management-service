from fastapi import Depends, FastAPI, HTTPException, status, Request
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


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

@app.post("/events/{event_id}/rsvps/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_event_rsvp(event_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):
    rsvp.event_id = event_id
    rsvp.event_name = "Event Name Placeholder"  # Replace with dynamic event name if needed
    db_rsvp = crud.create_rsvp(db=db, rsvp=rsvp)
    return crud.add_hateoas_to_rsvp({
        "id": db_rsvp.id,
        "event_id": db_rsvp.event_id,
        "event_name": db_rsvp.event_name,
        "name": db_rsvp.name,
        "email": db_rsvp.email,
        "status": db_rsvp.status
    })


@app.get("/events/{event_id}/rsvps/", response_model=list[dict], status_code=status.HTTP_200_OK)
def read_event_rsvps(event_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rsvps_with_links(db=db, event_id=event_id, skip=skip, limit=limit)


@app.get("/rsvps/{rsvp_id}", response_model=dict, status_code=status.HTTP_200_OK)
def read_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    db_rsvp = crud.get_rsvp(db=db, rsvp_id=rsvp_id)
    if not db_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return crud.add_hateoas_to_rsvp({
        "id": db_rsvp.id,
        "event_id": db_rsvp.event_id,
        "event_name": db_rsvp.event_name,
        "name": db_rsvp.name,
        "email": db_rsvp.email,
        "status": db_rsvp.status
    })


@app.put("/rsvps/{rsvp_id}", response_model=dict, status_code=status.HTTP_200_OK)
def update_rsvp(rsvp_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):
    updated_rsvp = crud.update_rsvp(db=db, rsvp_id=rsvp_id, rsvp=rsvp)
    if not updated_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return crud.add_hateoas_to_rsvp({
        "id": updated_rsvp.id,
        "event_id": updated_rsvp.event_id,
        "event_name": updated_rsvp.event_name,
        "name": updated_rsvp.name,
        "email": updated_rsvp.email,
        "status": updated_rsvp.status
    })

@app.delete("/rsvps/{rsvp_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_rsvp(rsvp_id: int, db: Session = Depends(get_db)):
    deleted_rsvp = crud.delete_rsvp(db=db, rsvp_id=rsvp_id)
    if not deleted_rsvp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSVP not found")
    return {
        "message": "RSVP deleted successfully",
        "_links": {
            "create": "/events/{event_id}/rsvps/",  
            "all": "/events/{event_id}/rsvps/"
        }
    }
