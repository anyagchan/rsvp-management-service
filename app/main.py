from fastapi import Depends, FastAPI, HTTPException, status, Request
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# # allow requests from frontend origin --> CORS errors 
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Allow your frontend's origin
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods
#     allow_headers=["*"],  # Allow all headers
# )

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
def create_event_rsvp(event_id: int, rsvp: schemas.RSVPCreate, db: Session = Depends(get_db)):

    # Create RSVP with associated event ID
    rsvp.event_id = event_id  # Set the event_id from the URL
    rsvp.event_name = "Event Name Placeholder"  # You may want to set this based on your external source
    return crud.create_rsvp(db=db, rsvp=rsvp)

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

## CQRS , graphql stuff using ariadne 
from ariadne import QueryType, make_executable_schema, graphql_sync, ObjectType
from ariadne.asgi import GraphQL

#ß GraphQL schema
type_defs = """
type User {
  id: Int!
  name: String
  email: String
}

type RSVP {
  id: Int!
  event_id: Int!
  event_name: String
  name: String
  email: String
  status: String
  user: User
}

type Query {
  rsvps: [RSVP]
  rsvp(id: Int!): RSVP
  users: [User]
  user(id: Int!): User
}
"""

query = QueryType()

from sqlalchemy.orm import joinedload

# RSVP resolvers
@query.field("rsvps")
def resolve_rsvps(*_):
    db = SessionLocal()
    try:
        # Eagerly load 'user' relationship, prevent lazy loading issues
        return db.query(models.RSVP).options(joinedload(models.RSVP.user)).all()
    finally:
        db.close()

@query.field("rsvp")
def resolve_rsvp(*_, id):
    db = SessionLocal()
    try:
        r = db.query(models.RSVP).options(joinedload(models.RSVP.user)).filter(models.RSVP.id == id).first()
        return r
    finally:
        db.close()

# User resolvers
@query.field("users")
def resolve_users(*_):
    db = SessionLocal()
    try:
        # Eagerly load 'rsvps' relationship
        return db.query(models.User).options(joinedload(models.User.rsvps)).all()
    finally:
        db.close()


@query.field("user")
def resolve_user(*_, id):
    db = SessionLocal()
    try:
        # Eagerly load 'rsvps' relationship for a specific user
        return db.query(models.User).options(joinedload(models.User.rsvps)).filter(models.User.id == id).first()
    finally:
        db.close()

rsvp_obj = ObjectType("RSVP")
user_obj = ObjectType("User")

@rsvp_obj.field("user")
def resolve_rsvp_user(obj, *_):
    return obj.user  

schema = make_executable_schema(type_defs, query, rsvp_obj, user_obj)

# Add GraphQL endpoint at /graphql
@app.api_route("/graphql", methods=["GET", "POST"])
async def graphql_endpoint(request: Request):
    # Handle GET requests
    if request.method == "GET":
        query = request.query_params.get("query")
        if not query:
            return {"error": "No query provided"}
        data = {"query": query}
    else:
        # Handle POST requests
        data = await request.json()

    success, result = graphql_sync(
        schema,
        data,
        context_value={},
        debug=False  
    )
    return result