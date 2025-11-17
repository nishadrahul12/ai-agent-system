from typing import Dict, Any, Optional, Callable, List
from .message import Message, MessageType, PriorityLevel
from .message_broker import MessageBroker

class AgentCommunication:
    """
    Communication interface for individual agents.
    Each agent uses this to send/receive messages.
    """
    
    def __init__(self, agent_id: str, broker: MessageBroker):
        """
        Initialize agent communication.
        
        Args:
            agent_id: ID of this agent
            broker: Shared message broker
        """
        self.agent_id = agent_id
        self.broker = broker
        self.sent_messages: Dict[str, Message] = {}
        self.received_messages: Dict[str, Message] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
    
    def send_request(self, 
                    receiver_id: str, 
                    action: str, 
                    data: Dict[str, Any] = None,
                    priority: PriorityLevel = PriorityLevel.MEDIUM) -> Optional[str]:
        """
        Send a request to another agent.
        
        Args:
            receiver_id: ID of receiving agent
            action: Action to request
            data: Data to send
            priority: Message priority
            
        Returns:
            message_id or None if failed
        """
        payload = {
            "action": action,
            "data": data or {}
        }
        
        message = Message(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            payload=payload,
            priority=priority
        )
        
        if self.broker.send_message(message):
            self.sent_messages[message.message_id] = message
            return message.message_id
        
        return None
    
    def send_response(self, 
                     receiver_id: str, 
                     result: Any,
                     parent_message_id: Optional[str] = None) -> Optional[str]:
        """
        Send a response to another agent.
        
        Args:
            receiver_id: ID of receiving agent
            result: Result data
            parent_message_id: ID of request message
            
        Returns:
            message_id or None if failed
        """
        payload = {"result": result}
        
        message = Message(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=MessageType.RESPONSE,
            payload=payload,
            parent_message_id=parent_message_id
        )
        
        if self.broker.send_message(message):
            self.sent_messages[message.message_id] = message
            return message.message_id
        
        return None
    
    def receive_message(self) -> Optional[Message]:
        """
        Receive next message from queue.
        
        Returns:
            Message or None
        """
        message = self.broker.receive_message(self.agent_id)
        
        if message:
            self.received_messages[message.message_id] = message
        
        return message
    
    def peek_messages(self, max_count: int = 10) -> List[Message]:
        """Peek at pending messages without removing them."""
        return self.broker.peek_messages(self.agent_id, max_count)
    
    def get_pending_count(self) -> int:
        """Get number of pending messages."""
        return self.broker.get_queue_size(self.agent_id)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """
        Register handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Callback function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
    
    def handle_incoming_messages(self):
        """Process all pending messages."""
        while True:
            msg = self.receive_message()
            if not msg:
                break
            
            # Call appropriate handler
            handlers = self.message_handlers.get(msg.message_type, [])
            for handler in handlers:
                try:
                    handler(msg)
                except Exception as e:
                    print(f"Error handling message: {e}")
    
    def get_communication_status(self) -> Dict[str, Any]:
        """Get communication status."""
        return {
            "agent_id": self.agent_id,
            "sent_messages": len(self.sent_messages),
            "received_messages": len(self.received_messages),
            "pending_messages": self.get_pending_count()
        }


# Example usage
if __name__ == "__main__":
    broker = MessageBroker()
    
    # Create agents with communication
    agent1 = AgentCommunication("agent_001", broker)
    agent2 = AgentCommunication("agent_002", broker)
    
    # Agent 1 sends request to Agent 2
    msg_id = agent1.send_request(
        receiver_id="agent_002",
        action="analyze_data",
        data={"values": [1, 2, 3]}
    )
    print(f"Request sent: {msg_id}")
    
    # Agent 2 receives
    msg = agent2.receive_message()
    print(f"Agent 2 received: {msg.payload}")
    
    # Agent 2 sends response
    response_id = agent2.send_response(
        receiver_id="agent_001",
        result={"analysis": "complete"},
        parent_message_id=msg.message_id
    )
    print(f"Response sent: {response_id}")
    
    # Agent 1 receives response
    response = agent1.receive_message()
    print(f"Agent 1 received response: {response.payload}")
