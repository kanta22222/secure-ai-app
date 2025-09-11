from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime)
    last_login = Column(DateTime)

class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    storage_name = Column(String, unique=True)
    user_id = Column(Integer)
    uploaded_at = Column(DateTime)
    file_size = Column(Integer)
    file_type = Column(String)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String)
    timestamp = Column(DateTime)
    details = Column(Text)

class ThreatDetection(Base):
    __tablename__ = "threat_detections"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer)
    threat_type = Column(String)
    confidence = Column(Float)
    detected_at = Column(DateTime)
    status = Column(String)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime)

class AdminAction(Base):
    __tablename__ = "admin_actions"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer)
    action = Column(String)
    target_user_id = Column(Integer)
    timestamp = Column(DateTime)
    details = Column(Text)
