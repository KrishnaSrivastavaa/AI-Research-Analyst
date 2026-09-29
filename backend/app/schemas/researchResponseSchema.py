from pydantic import BaseModel


class ResearchResponse(BaseModel):
    answer: str
    citations: list[str]
    grounded: bool

class EvidenceCheck(BaseModel):
    supported: bool



class Citation(BaseModel):
    id: str
    document_id: int
    document_name: str
    page_start: int 
    page_end: int

class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    grounded: bool