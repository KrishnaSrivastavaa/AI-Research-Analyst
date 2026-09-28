from pydantic import BaseModel


class ResearchResponse(BaseModel):
    answer: str
    citations: list[str]
    grounded: bool

class EvidenceCheck(BaseModel):
    supported: bool