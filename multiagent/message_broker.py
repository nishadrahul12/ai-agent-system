from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
from message import Message, MessageStatus
from datetime import datetime
import threading

class MessageBroker:
    """
    Central message hub for agent-to-agent communication.
    Routes messages, manages queues, handles delivery.
    """
    
    def __init__(self, max_queue_size: int = 1000, message_ttl_seconds: int = 3600):
        """
        Initialize message broker.
        
        Args:
            max_queue_size: Maximum messages per agent queue
            message_ttl_seconds: Message time-to-live
        """
        self.max_queue_size = max_queue_size
        self.message_ttl_seconds = message_ttl_seconds
        self.agent_queues: Dict[str, deque] = defaultdict(deque)
        self.message_history: Dict[str, Message] = {}
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.Lock()
        self.stats = {
            "total_messages_sent": 0,
            "total_messages_delivered": 0,
            "total_messages_failed": 0
        }
    
    def send_message(self, message: Message) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: Message to send
            
        Returns:
            True if successful
        """
        with self.lock:
            # Check queue size
            if len(self.agent_queues[message.receiver_id]) >= self.max_queue_size:
                message.mark_failed()
                self.stats["total_messages_failed"] += 1
                return False
            
            # Add to queue
            message.mark_sent()
            self.agent_queues[message.receiver_id].append(message)
            self.message_history[message.message_id] = message
            self.stats["total_messages_sent"] += 1
            
            # Mark delivered
            message.mark_delivered()
            self.stats["total_messages_delivered"] += 1
            
            # Call handlers
            self._trigger_handlers(message.receiver_id, message)
            
            return True
    
    def receive_message(self, agent_id: str) -> Optional[Message]:
        """
        Receive next message for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Next message or None if queue empty
        """
        with self.lock:
            queue = self.agent_queues[agent_id]
            
            if queue:
                # Get and remove oldest message
                message = queue.popleft()
                message.mark_processed()
                return message
            
            return None
    
    def peek_messages(self, agent_id: str, max_count: int = 10) -> List[Message]:
        """
        Peek at messages without removing them.
        
        Args:
            agent_id: Agent ID
            max_count: Maximum messages to peek
            
        Returns:
            List of messages
        """
        with self.lock:
            queue = self.agent_queues[agent_id]
            return list(queue)[:max_count]
    
    def get_queue_size(self, agent_id: str) -> int:
        """Get number of pending messages for an agent."""
        with self.lock:
            return len(self.agent_queues[agent_id])
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a specific message by ID."""
        return self.message_history.get(message_id)
    
    def broadcast_message(self, message: Message, agent_ids: List[str]) -> int:
        """
        Send message to multiple agents.
        
        Args:
            message: Message to broadcast
            agent_ids: List of agent IDs
            
        Returns:
            Number of successful sends
        """
        success_count = 0
        
        for agent_id in agent_ids:
            # Create copy of message for each recipient
            msg_copy = Message(
                sender_id=message.sender_id,
                receiver_id=agent_id,
                message_type=message.message_type,
                payload=message.payload.copy(),
                priority=message.priority,
                task_id=message.task_id
            )
            
            if self.send_message(msg_copy):
                success_count += 1
        
        return success_count
    
    def register_handler(self, agent_id: str, handler: Callable):
        """
        Register a callback handler for messages to an agent.
        
        Args:
            agent_id: Agent ID
            handler: Callback function
        """
        self.message_handlers[agent_id].append(handler)
    
    def _trigger_handlers(self, agent_id: str, message: Message):
        """Trigger all handlers for an agent."""
        for handler in self.message_handlers[agent_id]:
            try:
                handler(message)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def cleanup_expired_messages(self) -> int:
        """Remove expired messages from queues."""
        expired_count = 0
        
        with self.lock:
            for queue in self.agent_queues.values():
                to_remove = []
                for msg in queue:
                    if msg.is_expired(self.message_ttl_seconds):
                        to_remove.append(msg)
                        expired_count += 1
                
                # Remove expired messages
                for msg in to_remove:
                    queue.remove(msg)
        
        return expired_count
    
    def get_statistics(self) -> Dict[str, any]:
        """Get message broker statistics."""
        with self.lock:
            queue_stats = {
                agent_id: len(queue)
                for agent_id, queue in self.agent_queues.items()
            }
            
            return {
                "total_messages_sent": self.stats["total_messages_sent"],
                "total_messages_delivered": self.stats["total_messages_delivered"],
                "total_messages_failed": self.stats["total_messages_failed"],
                "pending_messages_by_agent": queue_stats,
                "total_pending": sum(queue_stats.values()),
                "message_history_size": len(self.message_history)
            }


# Example usage
if __name__ == "__main__":
    from message import MessageType, PriorityLevel
    
    broker = MessageBroker()
    
    # Send a message
    msg = Message(
        sender_id="agent_001",
        receiver_id="agent_002",
        message_type=MessageType.REQUEST,
        payload={"action": "analyze", "data": [1, 2, 3]},
        priority=PriorityLevel.HIGH
    )
    
    broker.send_message(msg)
    print(f"Message sent: {msg.message_id}")
    
    # Receive message
    received = broker.receive_message("agent_002")
    print(f"Message received: {received.message_id}")
    
    # Statistics
    stats = broker.get_statistics()
    print(f"Broker stats: {stats}")
