
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EmployeeSelection(BaseModel):
    id: str
    name: Optional[str] = None
    email: str
    filename: str
    path: str

class SendRequest(BaseModel):
    recipients: List[EmployeeSelection]
    subject: str = "Votre Bulletin de salaire"
    body: str = "Bonjour M ,Mme veuillez trouver en pièces vos bulletins de salaire .Bonne réception .Hervé KOFFI"

class DownloadRequest(BaseModel):
    files: List[str]

# Auth Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
