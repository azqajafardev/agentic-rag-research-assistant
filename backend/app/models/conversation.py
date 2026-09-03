"""Internal representation of conversation/message records."""

from dataclasses import dataclass
from datetime import datetime


class MessageRole:
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Conversation:
    id: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Message:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
