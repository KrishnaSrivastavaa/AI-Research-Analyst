from fastapi import APIRouter, Depends, File, HTTPException
from app.dependencies.auth_dependency import get_current_user
from app.core.database import get_db
from app.models.models import (
    Conversation,
    Doc,
    ConversationDoc,
    Message,
    MessageCitation,
    Chunk,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.docSchema import ConversationDocumentResponse
from app.schemas.chatSchema import (
    CreateConversationRequest,
    MessageRequest,
    AddConversationDocRequest,
    MessageResponse,
)

from sqlalchemy import select

from app.services.retrieval_service import retrieve_documents
from app.services.chat_service import send_message

router = APIRouter()


@router.get("/conversations")
async def get_conversations(
      current_user = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
):
      all_conversations = await db.scalars(
            select(Conversation)
            .where(Conversation.user_id == current_user["sub"])
      )

      return all_conversations.all()





@router.post("/conversations")
async def create_conversation(
    request: CreateConversationRequest,
    current_user = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
    
    ):
        try: 
            conversation = Conversation(
                    user_id = current_user["sub"],
                    title = request.title,
            )

            db.add(conversation)
            await db.commit()

            await db.refresh(conversation)

            return conversation
        except Exception as e:
              print ({ "message": str(e) })
              raise 

@router.get(
    "/conversations/{conversation_id}/documents",
    response_model=list[ConversationDocumentResponse]
)
async def get_connected_documents(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["sub"]
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    documents = await db.scalars(
        select(Doc)
        .join(
            ConversationDoc,
            ConversationDoc.document_id == Doc.id
        )
        .where(
            ConversationDoc.conversation_id == conversation_id
        )
    )

    return documents.all()



@router.post("/conversations/{conversation_id}/documents")
async def add_conversation_document(
      conversation_id: int,
      request: AddConversationDocRequest,
      db: AsyncSession = Depends(get_db),
      current_user = Depends(get_current_user)
):
      conversation = await db.scalar(
            select(Conversation)
            .where(
                  Conversation.id == conversation_id,
                  Conversation.user_id == current_user["sub"]
            )
      )

      if conversation is None:
            raise HTTPException(
                  status_code=404,
                  detail="Conversation not found"
            )

      document = await db.scalar(
            select(Doc)
            .where(
                  Doc.id == request.document_id,
                  Doc.owner_id == current_user["sub"]
            )
      )

      if document is None:
            raise HTTPException(
                  status_code=404,
                  detail="Document not found"
            )

      conversation_document = ConversationDoc(
            conversation_id =  conversation_id,
            document_id = request.document_id
      )

      db.add(conversation_document)
      await db.commit()

      return {
            "message": f"Document: {document.doc_name} connected with conversation {conversation.title}"
      }

@router.get("/conversations/{conversation_id}/messages",
            response_model=list[MessageResponse]
            )
async def get_messages(
      conversation_id: int,
      current_user = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
):
      conversation = await db.scalar(
           select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user["sub"]
           )
      )

      if conversation is None:
           raise HTTPException(
                status_code=404,
                detail = "Conversation not found"
           )

      
      messages = await db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id).order_by(Message.id)
      )

      all_messages = messages.all()

      response = []

      for message in all_messages:
           citations = []

           if message.role == "assistant":
                citation_rows = await db.execute(
                     select(
                          MessageCitation,
                          Chunk,
                          Doc
                     )
                     .join(
                          Chunk,
                          MessageCitation.chunk_id == Chunk.id
                     )
                     .join(
                          Doc,
                          Chunk.doc_id == Doc.id
                     )
                     .where(
                          MessageCitation.message_id == message.id
                     )
                     .order_by(
                          MessageCitation.citation_order
                     )
                )

                for message_citation, chunk, document in citation_rows.all():
                     citations.append(
                          {
                               "id": f"S{message_citation.citation_order}",
                               "document_id": document.id,
                               "document_name": document.doc_name,
                               "page_start": chunk.page_start,
                               "page_end": chunk.page_end,
                              
                          }
                     )
            
           response.append(
                        {
                              "id": message.id,
                              "conversation_id": message.conversation_id,
                              "role": message.role,
                              "content": message.content,
                              "created_at": message.created_at,
                              "citations": citations
                        }
                  )

      return response

@router.post("/conversations/{conversation_id}/messages")
async def chat(
      conversation_id: int, 
      request: MessageRequest,
      db: AsyncSession = Depends(get_db),
      current_user = Depends(get_current_user)
):
    return await send_message(
          db = db,
          conversation_id = conversation_id,
          user_id = current_user["sub"],
          query= request.query
    )



