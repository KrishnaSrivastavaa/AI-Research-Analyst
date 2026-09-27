from fastapi import APIRouter, Depends, File, HTTPException
from app.dependencies.auth_dependency import get_current_user
from app.core.database import get_db
from app.models.models import Conversation, Doc, ConversationDoc, Message

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chatSchema import CreateConversationRequest, MessageRequest, AddConversationDocRequest
from sqlalchemy import select

from app.services.retrieval_service import retrieve_documents
from app.services.chat_service import get_chat_response

router = APIRouter()


@router.post("/conversations")
async def create_conversation(
    request: CreateConversationRequest,
    current_user = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
    
    ):
        try: 
            conversation = Conversation(
                    user_id = current_user.id,
                    title = request.title,
            )

            db.add(conversation)
            await db.commit()

            await db.refresh(conversation)

            return conversation
        except Exception as e:
              print ({ "message": str(e) })
              raise 


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
                  Conversation.user_id == current_user.id
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
                  Doc.owner_id == current_user.id
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


      

@router.post("/conversations/{conversation_id}/messages")
async def chat(
      conversation_id: int, 
      request: MessageRequest,
      db: AsyncSession = Depends(get_db),
      current_user = Depends(get_current_user)
):
    conversation = await db.scalar(
    select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    document_ids = await db.scalars(
          select(ConversationDoc.document_id)
          .where(
                ConversationDoc.conversation_id == conversation_id
          )
    ).all()
      
    context = await retrieve_documents(request.query, current_user.id, document_ids)

    result = await db.execute(
          select(Message.role, Message.content)
          .where(
                Message.conversation_id == conversation_id
          ).order_by(Message.id.desc())
          .limit(10)
    )

    history = result.mappings().all()

    user_message = Message(
          conversation_id= conversation_id,
          role= "user",
          content= request.query
    )


    db.add(user_message)


    chat_response = await get_chat_response(request.query, history, context)

    analyst_message = Message(
              conversation_id= conversation_id,
              role= "assisstant",
              content= chat_response
        )
    
    
    db.add(analyst_message)



    await db.commit()



