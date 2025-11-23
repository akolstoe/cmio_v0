"""SQLAlchemy models for CMIO digital care coordination platform."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base class."""


class MessageType(enum.Enum):
    CHANNEL = "channel"
    DIRECT = "direct"
    SELF_NOTE = "self_note"


class SecurityRating(enum.Enum):
    SHARED = "shared"
    SENSITIVE = "sensitive"
    PRIVATE = "private"


class FactStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NoteStatus(enum.Enum):
    DRAFT = "draft"
    READY_FOR_APPROVAL = "ready_for_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


message_clients = Table(
    "message_clients",
    Base.metadata,
    Column("message_id", ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True),
    Column("client_id", ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True),
    Column("context", String(255), nullable=True),
)


def utcnow() -> datetime:
    return datetime.utcnow()


class TeamChannel(Base):
    __tablename__ = "team_channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    messages: Mapped[List[Message]] = relationship(back_populates="channel")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))

    sent_messages: Mapped[List[Message]] = relationship(back_populates="sender")
    tasks: Mapped[List[Task]] = relationship(back_populates="assignee")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(32))
    preferred_language: Mapped[Optional[str]] = mapped_column(String(64))
    primary_contact: Mapped[Optional[str]] = mapped_column(String(64))

    messages: Mapped[List[Message]] = relationship(
        secondary=message_clients,
        back_populates="clients",
    )
    pending_facts: Mapped[List[PendingFact]] = relationship(back_populates="client")
    approved_facts: Mapped[List[ClientFact]] = relationship(back_populates="client")
    tasks: Mapped[List[Task]] = relationship(back_populates="client")
    encounter_notes: Mapped[List[EncounterNote]] = relationship(back_populates="client")
    case_notes: Mapped[List[CaseNote]] = relationship(back_populates="client")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "(channel_id IS NOT NULL) = (message_type = 'channel')",
            name="channel_message_type_check",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    channel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("team_channels.id"))

    sender: Mapped[User] = relationship(back_populates="sent_messages")
    channel: Mapped[Optional[TeamChannel]] = relationship(back_populates="messages")
    clients: Mapped[List[Client]] = relationship(
        secondary=message_clients,
        back_populates="messages",
    )
    pending_facts: Mapped[List[PendingFact]] = relationship(back_populates="source_message")
    encounter_notes: Mapped[List[EncounterNote]] = relationship(back_populates="source_message")


class PendingFact(Base):
    __tablename__ = "pending_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    source_message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    fact_type: Mapped[str] = mapped_column(String(64))
    fact_value: Mapped[str] = mapped_column(Text)
    security_rating: Mapped[SecurityRating] = mapped_column(Enum(SecurityRating))
    status: Mapped[FactStatus] = mapped_column(Enum(FactStatus), default=FactStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    client: Mapped[Client] = relationship(back_populates="pending_facts")
    source_message: Mapped[Message] = relationship(back_populates="pending_facts")
    reviewer: Mapped[Optional[User]] = relationship()
    approved_fact: Mapped[Optional[ClientFact]] = relationship(back_populates="pending_fact", uselist=False)


class ClientFact(Base):
    __tablename__ = "client_facts"
    __table_args__ = (
        UniqueConstraint("client_id", "fact_type", "fact_value", name="uq_client_fact"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    pending_fact_id: Mapped[int] = mapped_column(
        ForeignKey("pending_facts.id", ondelete="SET NULL"), nullable=True
    )
    fact_type: Mapped[str] = mapped_column(String(64))
    fact_value: Mapped[str] = mapped_column(Text)
    security_rating: Mapped[SecurityRating] = mapped_column(Enum(SecurityRating))
    approved_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    approved_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    client: Mapped[Client] = relationship(back_populates="approved_facts")
    pending_fact: Mapped[Optional[PendingFact]] = relationship(back_populates="approved_fact")
    approved_by: Mapped[User] = relationship()


class EncounterNote(Base):
    __tablename__ = "encounter_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    source_message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    summary: Mapped[str] = mapped_column(String(255))
    details: Mapped[str] = mapped_column(Text)
    note_type: Mapped[str] = mapped_column(String(64))  # encounter, care_coordination, etc.
    status: Mapped[NoteStatus] = mapped_column(Enum(NoteStatus), default=NoteStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    client: Mapped[Client] = relationship(back_populates="encounter_notes")
    source_message: Mapped[Optional[Message]] = relationship(back_populates="encounter_notes")
    author: Mapped[User] = relationship()
    case_note: Mapped[Optional[CaseNote]] = relationship(back_populates="encounter_note", uselist=False)


class CaseNote(Base):
    __tablename__ = "case_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_note_id: Mapped[int] = mapped_column(
        ForeignKey("encounter_notes.id", ondelete="CASCADE"), unique=True
    )
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    finalized_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    body: Mapped[str] = mapped_column(Text)

    client: Mapped[Client] = relationship(back_populates="case_notes")
    encounter_note: Mapped[EncounterNote] = relationship(back_populates="case_note")
    author: Mapped[User] = relationship()


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(32), default="pending")

    client: Mapped[Optional[Client]] = relationship(back_populates="tasks")
    assignee: Mapped[Optional[User]] = relationship(back_populates="tasks")
    steps: Mapped[List[TaskStep]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskStep(Base):
    __tablename__ = "task_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(String(255))
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    task: Mapped[Task] = relationship(back_populates="steps")


class ModelRun(Base):
    """Tracks which AI/regex model processed a message or fact."""

    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"))
    pending_fact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("pending_facts.id", ondelete="SET NULL")
    )

    message: Mapped[Optional[Message]] = relationship()
    pending_fact: Mapped[Optional[PendingFact]] = relationship()
