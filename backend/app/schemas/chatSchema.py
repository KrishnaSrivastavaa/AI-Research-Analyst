from pydantic import BaseModel, Field
from datetime import datetime

class CreateConversationRequest(BaseModel):
    title: str

class MessageRequest(BaseModel):
    query: str

class AddConversationDocRequest(BaseModel):
    document_id: int


class MessageCitationResponse(BaseModel):
    id: str
    document_id: int
    document_name: str
    page_start: int
    page_end: int


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    citations: list[MessageCitationResponse] = Field(
        default_factory=list
    )