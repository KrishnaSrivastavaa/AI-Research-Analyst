from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 
from typing import List, Optional
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import DateTime, func, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
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
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
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

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
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

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"))
    document_id: Mapped[int] = mapped_column(ForeignKey("doc.id"))

    conversation: Mapped["Conversation"] = relationship(back_populates="conversation_documents")
    document: Mapped["Doc"] = relationship(back_populates="conversation_documents")