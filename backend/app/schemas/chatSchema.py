from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    title: str

class MessageRequest(BaseModel):
    query: str

class AddConversationDocRequest(BaseModel):
    document_id: int