from typing import Dict, List, Optional, Tuple
from agent import Agent, SupervisorAgent, WorkerAgent, EvaluatorAgent

class AgentRegistry:
    """
    Registry to track, manage, and access all agents in the system.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, Agent] = {}
        self.agents_by_type: Dict[str, List[str]] = {}
    
    def register_agent(self, agent: Agent) -> str:
        """
        Register a new agent.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            agent_id
        """
        agent_id = agent.agent_id
        self.agents[agent_id] = agent
        
        # Index by type
        agent_type = agent.agent_type
        if agent_type not in self.agents_by_type:
            self.agents_by_type[agent_type] = []
        
        self.agents_by_type[agent_type].append(agent_id)
        
        return agent_id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent_type = agent.agent_type
        
        # Remove from main dict
        del self.agents[agent_id]
        
        # Remove from type index
        if agent_type in self.agents_by_type:
            self.agents_by_type[agent_type].remove(agent_id)
            if not self.agents_by_type[agent_type]:
                del self.agents_by_type[agent_type]
        
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None
        """
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[Agent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Type of agent (supervisor, worker_generic, etc.)
            
        Returns:
            List of agents
        """
        agent_ids = self.agents_by_type.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids]
    
    def find_best_agent(self, task_description: str) -> Tuple[Optional[Agent], float]:
        """
        Find the best agent to handle a task.
        Uses capability matching and confidence scoring.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Tuple of (best_agent, confidence_score)
        """
        best_agent = None
        best_score = 0.0
        
        for agent in self.agents.values():
            score = agent.can_handle_task(task_description)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent, best_score
    
    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    def get_agent_count(self) -> int:
        """Get total number of registered agents."""
        return len(self.agents)
    
    def get_registry_status(self) -> Dict[str, any]:
        """Get overall registry status."""
        return {
            "total_agents": len(self.agents),
            "by_type": {
                agent_type: len(agent_ids)
                for agent_type, agent_ids in self.agents_by_type.items()
            },
            "agents": [agent.to_dict() for agent in self.agents.values()]
        }


# Example usage
if __name__ == "__main__":
    # Create registry
    registry = AgentRegistry()
    
    # Create and register agents
    supervisor = SupervisorAgent(name="Main Supervisor")
    worker1 = WorkerAgent(worker_type="generic", name="Worker 1")
    worker2 = WorkerAgent(worker_type="telecom", name="Telecom Worker")
    evaluator = EvaluatorAgent()
    
    registry.register_agent(supervisor)
    registry.register_agent(worker1)
    registry.register_agent(worker2)
    registry.register_agent(evaluator)
    
    # Get status
    print(f"Total agents: {registry.get_agent_count()}")
    print(f"Registry: {registry.get_registry_status()}")
    
    # Find best agent for task
    task = "Analyze telecom KPIs"
    best_agent, score = registry.find_best_agent(task)
    print(f"Best agent for '{task}': {best_agent.name} (score: {score})")
