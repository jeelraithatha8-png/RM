from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer)
    occupation = Column(String(255))
    verification_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    preference = relationship("Preference", back_populates="user", uselist=False, cascade="all, delete")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # "Morning", "Night", "Evening"
    sleep_pref = Column(String(50))
    # "Light", "Heavy"
    sleep_sense = Column(String(50))
    # "Introvert", "Extrovert", "Ambivert"
    personality = Column(String(50))
    # "Organized", "Flexible", "Mixed"
    living_habit = Column(String(50))
    # "Quiet", "Moderate", "Noisy"
    noise_tolerance = Column(String(50))
    # "No Guests", "Occasional", "Male Allowed"
    guest_policy = Column(String(50))

    user = relationship("User", back_populates="preference")
