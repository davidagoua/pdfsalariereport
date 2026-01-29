
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
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

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    matricule = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    documents = relationship("EmployeeDocument", back_populates="employee")

class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"))
    filename = Column(String)
    period = Column(String)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="documents")
