
from pydantic import BaseModel
from typing import List, Optional

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
