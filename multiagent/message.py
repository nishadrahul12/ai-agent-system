from .typing import Dict, Any, Optional
from .datetime import datetime
from .enum import Enum
import uuid
import json

class MessageType(Enum):
    """Message types for agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HEALTH_CHECK = "health_check"
    ERROR = "error"
    ACKNOWLEDGEMENT = "ack"

class MessageStatus(Enum):
    """Message status throughout its lifecycle."""
    CREATED = "created"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"

class PriorityLevel(Enum):
    """Message priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Message:
    """
    Represents a message between agents.
    Defines the protocol for agent-to-agent communication.
    """
    
    def __init__(self,
                 sender_id: str,
                 receiver_id: str,
                 message_type: MessageType,
                 payload: Dict[str, Any],
                 priority: PriorityLevel = PriorityLevel.MEDIUM,
                 task_id: Optional[str] = None,
                 parent_message_id: Optional[str] = None):
        """
        Initialize a message.
        
        Args:
            sender_id: ID of sending agent
            receiver_id: ID of receiving agent
            message_type: Type of message
            payload: Message content
            priority: Priority level
            task_id: Related task ID
            parent_message_id: ID of parent message (for message chains)
        """
        self.message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.payload = payload
        self.priority = priority
        self.task_id = task_id
        self.parent_message_id = parent_message_id
        self.status = MessageStatus.CREATED
        self.created_at = datetime.now()
        self.sent_at = None
        self.delivered_at = None
        self.processed_at = None
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "priority": self.priority.name,
            "task_id": self.task_id,
            "parent_message_id": self.parent_message_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None
        }
    
    def mark_sent(self):
        """Mark message as sent."""
        self.status = MessageStatus.SENT
        self.sent_at = datetime.now()
    
    def mark_delivered(self):
        """Mark message as delivered."""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.now()
    
    def mark_processed(self):
        """Mark message as processed."""
        self.status = MessageStatus.PROCESSED
        self.processed_at = datetime.now()
    
    def mark_failed(self):
        """Mark message as failed."""
        self.status = MessageStatus.FAILED
    
    def is_expired(self, ttl_seconds: int = 3600) -> bool:
        """
        Check if message has expired.
        
        Args:
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if message is older than TTL
        """
        age_seconds = (datetime.now() - self.created_at).total_seconds()
        return age_seconds > ttl_seconds
    
    def __repr__(self) -> str:
        return f"Message(id={self.message_id}, from={self.sender_id}, to={self.receiver_id}, type={self.message_type.value})"
