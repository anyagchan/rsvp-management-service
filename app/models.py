# app/models.py

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    rsvps = relationship("RSVP", back_populates="user")

class RSVP(Base):
    __tablename__ = "rsvps"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    event_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    status = Column(Enum('Going', 'Maybe', 'Not Going'), default='Going')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    user_id = Column(Integer, ForeignKey('users.id'))  # Assuming you want to link RSVP to a User
    user = relationship("User", back_populates="rsvps")