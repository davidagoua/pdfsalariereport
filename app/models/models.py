
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    email_logs = relationship("EmailLog", back_populates="job")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"))
    recipient_email = Column(String)
    status = Column(String) # sent, failed, skipped
    error_message = Column(Text, nullable=True)
    filename = Column(String, nullable=True)
    
    job = relationship("Job", back_populates="email_logs")
