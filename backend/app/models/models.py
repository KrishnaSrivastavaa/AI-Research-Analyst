from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime
from typing import List, Optional

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    avatar_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    docs: Mapped[List["Doc"]] = relationship(back_populates="user")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="user")

class Doc(Base):
    __tablename__ = "docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    doc_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False)
    content_hash: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )

    user: Mapped["User"] = relationship(back_populates="docs")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="doc")
    conversation_documents: Mapped[list["ConversationDoc"]] = relationship(back_populates="doc")
    ingestion_jobs: Mapped[list["IngestionJob"]] = relationship(back_populates="doc")


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("docs.id"))
    status: Mapped[str]
    total_chunks: Mapped[int]
    processed_chunks: Mapped[int]
    error_message: Mapped[str | None]
    started_at: Mapped[datetime | None]

    completed_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    doc: Mapped["Doc"] = relationship(back_populates="ingestion_jobs")

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("docs.id"))
    chunk_index:Mapped[int]
    content: Mapped[str]
    page_start: Mapped[int]
    page_end: Mapped[int]
    chunk_metadata: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    doc: Mapped["Doc"] = relationship(back_populates="chunks")
    message_citations: Mapped[list["MessageCitation"]] = relationship(back_populates="chunk")

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")
    conversation_documents: Mapped[list["ConversationDoc"]] = relationship(back_populates="conversation")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="conversation")


class ConversationDoc(Base):
    __tablename__ = "conversation_docs"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    document_id: Mapped[int] = mapped_column(ForeignKey("docs.id"))

    conversation: Mapped["Conversation"] = relationship(back_populates="conversation_documents")
    doc: Mapped["Doc"] = relationship(back_populates="conversation_documents")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="message")
    message_citations: Mapped[list["MessageCitation"]] = relationship(back_populates="message")


class MessageCitation(Base):
    __tablename__ = "message_citations"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    chunk_id: Mapped[int] = mapped_column(ForeignKey("chunks.id"))
    citation_order: Mapped[int]

    message: Mapped["Message"] = relationship(back_populates="message_citations")
    chunk: Mapped["Chunk"] = relationship(back_populates="message_citations")

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    status: Mapped[str]
    model: Mapped[str]
    input_tokens: Mapped[int]
    output_tokens: Mapped[int]
    latency_ms: Mapped[int]
    started_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]

    conversation: Mapped["Conversation"] = relationship(back_populates="agent_runs")
    message: Mapped["Message"] = relationship(back_populates="agent_runs")
    agent_events: Mapped[list["AgentEvent"]] = relationship(back_populates="agent_run")


class AgentEvent(Base):
    __tablename__ = "agent_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_run_id: Mapped[int] = mapped_column(ForeignKey("agent_runs.id"))
    event_type: Mapped[str]
    payload: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    agent_run: Mapped["AgentRun"] = relationship(back_populates="agent_events")