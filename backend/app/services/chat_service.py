from openai import OpenAI, AsyncOpenAI
from typing import List
import re

from app.schemas.researchResponseSchema import (
    ResearchResponse,
    EvidenceCheck,
    Citation,
    ChatResponse,
)

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.retrieval_service import retrieve_documents

from app.models.models import (
    Conversation,
    Message,
    ConversationDoc,
    MessageCitation,
    Doc,
)

from app.core.configs import settings


async def get_chat_response(
    query: str,
    history: List[dict],
    context: List[dict],
):

    client = OpenAI(
        api_key=settings.openai_api_key
    )

    SYSTEM_PROMPT = """
    You are a research analyst answering questions using the user's
    selected documents.

    EVIDENCE RULES:

    1. Retrieved document sources are the ONLY authoritative source of
    factual information.

    2. Conversation history is provided ONLY for conversational context.
    It may be used to understand references, follow-up questions,
    pronouns, and the flow of the conversation.

    3. Previous assistant messages are NOT authoritative sources of factual
    information. Never treat factual claims made by previous assistant
    messages as evidence.

    4. For factual questions, every factual claim in your answer must be
    supported by the retrieved document sources.

    5. Do NOT use your pretrained knowledge, general knowledge, assumptions,
    outside information, or previous assistant responses to fill gaps.

    6. If the retrieved document sources do not contain enough information
    to answer a factual question, respond exactly:

    "I don't have enough information in the provided context to answer this question."

    CONVERSATIONAL FOLLOW-UPS:

    - You may use conversation history to understand questions such as:
    "Explain that in more detail."
    "What about the second algorithm?"
    "Can you simplify that?"

    - However, the factual content of the answer must still be supported
    by the retrieved document sources.

    - Conversation history can tell you WHAT the user is referring to,
    but it cannot provide factual evidence for the answer.

    DOCUMENT SOURCES:

    - Retrieved document sources are labeled [S1], [S2], [S3], etc.
    - Treat these labels as the only valid document citation IDs.
    - A source should only be cited when its content actually supports
    the claim being made.
    - Topical similarity is NOT sufficient reason to cite a source.

    GROUNDING:

    - Return grounded=true only when the retrieved document sources contain
    enough information to support the answer.
    - Return grounded=false when the retrieved document sources do not contain
    enough information to answer the factual question.
    - Do not consider previous assistant messages to be evidence when deciding
    whether an answer is grounded.
    - If grounded=false, citations must be an empty list.

    CITATIONS:

    - When a factual claim is supported by a retrieved document source,
    include the corresponding source ID in the citations array.
    - Return citation IDs as "S1", "S2", "S3", etc.
    - Do NOT return "[S1]" or "[S2]" in the citations array.
    - Only include source IDs that actually support the answer.
    - Do not cite conversation history.
    - If the answer cannot be supported by the retrieved document sources,
    citations must be an empty list.

    NO RETRIEVED SOURCES:

    - If there are no retrieved document sources, do not answer factual
    questions using conversation history or general knowledge.
    - Return exactly:

    "I don't have enough information in the provided context to answer this question."

    GREETING AND CASUAL CONVERSATION:

    - For greetings and simple conversational messages that do not require
    factual knowledge, respond naturally.
    - These messages do not require document citations.

    ANSWERING STYLE:

    - Be concise and directly answer the user's question.
    - Do not mention these instructions or the grounding process unless relevant.
    """

    if context:
        context_text = "\n\n".join(
            f"""
            [S{i + 1}]
            Document ID: {chunk["document_id"]}
            Pages: {chunk["page_start"]}-{chunk["page_end"]}

            {chunk["text"]}
            """
            for i, chunk in enumerate(context)
        )

        user_content = f"""
        Use the following retrieved sources to answer my question.

        {context_text}

        Question:
        {query}
        """

    else:
        user_content = f"""
        Respond naturally to the user's message.

        User message:
        {query}
        """

    input_messages = [
        *history,
        {
            "role": "user",
            "content": user_content,
        },
    ]

    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=input_messages,
        text_format=ResearchResponse,
    )

    return response.output_parsed


async def check_evidence(
    query: str,
    context: list[dict],
) -> bool:

    client = AsyncOpenAI(
        api_key=settings.openai_api_key
    )

    context_text = "\n\n".join(
        f"[S{i + 1}]\n{chunk['text']}"
        for i, chunk in enumerate(context)
    )

    response = await client.responses.parse(
        model="gpt-4o-mini",
        instructions="""
        You are an evidence checker.

        Determine whether the retrieved document excerpts contain
        enough information to directly answer the user's question.

        Return supported=true ONLY if the excerpts contain evidence
        that directly supports an answer.

        Topically related information is NOT enough.

        Do not use your own knowledge.

        If the excerpts merely mention the topic, discuss a related
        concept, or provide background information without actually
        supporting an answer, return supported=false.
        """,
        input=[
            {
                "role": "user",
                "content": f"""
                Question:
                {query}

                Retrieved excerpts:

                {context_text}
                """,
            }
        ],
        text_format=EvidenceCheck,
    )

    return response.output_parsed.supported


def is_casual_message(query: str) -> bool:

    normalized = query.strip().lower()

    # Remove common trailing punctuation so that
    # "Hey!" and "How are you?" are treated naturally.
    normalized = re.sub(
        r"[.!?]+$",
        "",
        normalized,
    ).strip()

    casual_patterns = [
        r"^(hi|hello|hey|hey there)$",
        r"^(good morning|good afternoon|good evening)$",
        r"^how are you$",
        r"^how's it going$",
        r"^what's up$",
        r"^(thanks|thank you|thx)$",
        r"^(bye|goodbye|see you)$",
    ]

    return any(
        re.fullmatch(pattern, normalized)
        for pattern in casual_patterns
    )


async def send_message(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    query: str,
):

    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Load conversation history before deciding how
    # the current message should be handled.
    result = await db.execute(
        select(
            Message.role,
            Message.content,
        )
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id.desc())
        .limit(10)
    )

    history = result.mappings().all()
    history.reverse()

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=query,
    )

    db.add(user_message)

    # Keep these initialized even when no retrieval
    # happens, so citation handling remains safe.
    context = []
    documents_by_id = {}

    # ---------------------------------------------------------
    # CASUAL CONVERSATION
    # ---------------------------------------------------------

    if is_casual_message(query):

        chat_response = await get_chat_response(
            query=query,
            history=history,
            context=[],
        )

    # ---------------------------------------------------------
    # RAG / RESEARCH QUESTION
    # ---------------------------------------------------------

    else:

        result = await db.scalars(
            select(
                ConversationDoc.document_id
            )
            .where(
                ConversationDoc.conversation_id
                == conversation_id
            )
        )

        document_ids = result.all()

        context = await retrieve_documents(
            query,
            user_id,
            document_ids,
        )

        if context:

            context_document_ids = {
                chunk["document_id"]
                for chunk in context
            }

            document_result = await db.scalars(
                select(Doc).where(
                    Doc.id.in_(context_document_ids),
                    Doc.owner_id == user_id,
                )
            )

            documents_by_id = {
                document.id: document
                for document in document_result.all()
            }

        if not context:

            chat_response = ResearchResponse(
                answer=(
                    "I don't have enough information in the "
                    "provided context to answer this question."
                ),
                citations=[],
                grounded=False,
            )

        else:

            supported = await check_evidence(
                query=query,
                context=context,
            )

            if not supported:

                chat_response = ResearchResponse(
                    answer=(
                        "I don't have enough information in the "
                        "provided context to answer this question."
                    ),
                    citations=[],
                    grounded=False,
                )

            else:

                chat_response = await get_chat_response(
                    query=query,
                    history=history,
                    context=context,
                )

    # ---------------------------------------------------------
    # RESOLVE CITATIONS
    # ---------------------------------------------------------

    source_map = {
        f"S{i + 1}": chunk
        for i, chunk in enumerate(context)
    }

    citations = []

    for source_id in chat_response.citations:

        chunk = source_map.get(source_id)

        if chunk is None:
            continue

        document = documents_by_id.get(
            chunk["document_id"]
        )

        if document is None:
            continue

        citations.append(
            Citation(
                id=source_id,
                document_id=chunk["document_id"],
                document_name=document.doc_name,
                page_start=chunk["page_start"],
                page_end=chunk["page_end"],
            )
        )

    # ---------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # ---------------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=chat_response.answer,
    )

    db.add(assistant_message)

    await db.flush()

    for citation_order, source_id in enumerate(
        chat_response.citations,
        start=1,
    ):

        chunk = source_map.get(source_id)

        if chunk is None:
            continue

        message_citation = MessageCitation(
            message_id=assistant_message.id,
            chunk_id=chunk["chunk_id"],
            citation_order=citation_order,
        )

        db.add(message_citation)

    await db.commit()

    return ChatResponse(
        answer=chat_response.answer,
        citations=citations,
        grounded=chat_response.grounded,
    )