from sqlalchemy.orm import Session
from . import models, schemas

def add_hateoas_to_rsvp(rsvp: dict):
    """Add HATEOAS links to RSVP dictionary."""
    return {
        **rsvp,
        "_links": {
            "self": f"/rsvps/{rsvp['id']}",
            "update": f"/rsvps/{rsvp['id']}",
            "delete": f"/rsvps/{rsvp['id']}",
            "event_rsvps": f"/events/{rsvp['event_id']}/rsvps/"
        }
    }

def get_rsvps_with_links(db: Session, event_id: int, skip: int = 0, limit: int = 100):
    """Fetch RSVPs for an event and add HATEOAS links."""
    rsvps = db.query(models.RSVP).filter(models.RSVP.event_id == event_id).offset(skip).limit(limit).all()
    return [
        add_hateoas_to_rsvp({
            "id": rsvp.id,
            "event_id": rsvp.event_id,
            "event_name": rsvp.event_name,
            "name": rsvp.name,
            "email": rsvp.email,
            "status": rsvp.status
        }) for rsvp in rsvps
    ]

def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()  # Ensure this exists

def get_rsvp(db: Session, rsvp_id: int):
    return db.query(models.RSVP).filter(models.RSVP.id == rsvp_id).first()

def get_rsvps_for_event(db: Session, event_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.RSVP).filter(models.RSVP.event_id == event_id).offset(skip).limit(limit).all()  # Corrected field name

def create_rsvp(db: Session, rsvp: schemas.RSVPCreate):
    db_rsvp = models.RSVP(**rsvp.dict())
    db.add(db_rsvp)
    db.commit()
    db.refresh(db_rsvp)
    return db_rsvp

def update_rsvp(db: Session, rsvp_id: int, rsvp: schemas.RSVPCreate):
    db_rsvp = db.query(models.RSVP).filter(models.RSVP.id == rsvp_id).first()
    if db_rsvp:
        for key, value in rsvp.dict().items():
            setattr(db_rsvp, key, value)
        db.commit()
        db.refresh(db_rsvp)
        return db_rsvp
    return None

def delete_rsvp(db: Session, rsvp_id: int):
    db_rsvp = db.query(models.RSVP).filter(models.RSVP.id == rsvp_id).first()
    if db_rsvp:
        db.delete(db_rsvp)
        db.commit()
        return db_rsvp
    return None