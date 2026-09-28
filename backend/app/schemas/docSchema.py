from pydantic import BaseModel
from datetime import datetime


class ConversationDocumentResponse(BaseModel):
    id: int
    doc_name: str
    mime_type: str
    page_count: int
    status: str
    created_at: datetime