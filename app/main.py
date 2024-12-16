from fastapi import Depends, FastAPI, HTTPException, status, Request
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from .auth import create_jwt_token, verify_jwt_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx




# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

async def call_protected_service(token: str, url: str, method: str = 'GET', data: dict = None):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        if method == 'GET':
            response = await client.get(url, headers=headers)
        elif method == 'PUT':
            response = await client.put(url, headers=headers, json=data)
        # Return the entire response object
        return response  # Return the full response object

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
async def create_event_rsvp(
    event_id: int,
    rsvp: schemas.RSVPCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    payload = verify_jwt_token(token)
    rsvp.event_id = event_id
    rsvp.event_name = "Event Name Placeholder"
    
    # Create the RSVP
    created_rsvp = crud.create_rsvp(db=db, rsvp=rsvp)
    
    # Retrieve the current RSVP count for the event
    event_url = f"http://3.219.96.214:8001/events/{event_id}"
    event_response = await call_protected_service(token, event_url, 'GET')
    
    if event_response.status_code == 200:
        event_data = event_response.json()
        
        current_rsvp_count = event_data[8]  # Default to 0 if not provided
        
        # Increment the RSVP count
        updated_rsvp_count = current_rsvp_count + 1
        
        # Update the RSVP count for the event
        update_url = f"http://3.219.96.214:8001/events/{event_id}"
        update_data = {"rsvpCount": updated_rsvp_count}
        await call_protected_service(token, update_url, 'PUT', update_data)
    else:
        raise HTTPException(
            status_code=event_response.status_code,
            detail=f"Failed to retrieve event data: {event_response.json()}"
        )
    
    return created_rsvp


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

@app.post('/auth/google/callback')
async def google_callback(user_info: dict):  # Assume user_info is obtained from Google login response
    token_data = {
    "sub": user_info['email'],
    "user_id": user_info['id'],
    "role": "user",  # Example of a grant
}
    
    access_token = create_jwt_token(token_data)
    return {"access_token": access_token}


