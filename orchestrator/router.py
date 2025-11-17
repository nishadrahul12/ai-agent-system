from typing import Optional, Tuple, Dict, Any
from .agent import Agent
from .agent_registry import AgentRegistry

class Router:
    """
    Routes tasks to appropriate agents based on capability matching.
    """
    
    def __init__(self, registry: AgentRegistry):
        """
        Initialize router.
        
        Args:
            registry: Agent registry to use for routing
        """
        self.registry = registry
        self.routing_history = []
    
    def route_task(self, task_description: str) -> Tuple[Optional[Agent], float]:
        """
        Route a task to the best-matching agent.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Tuple of (selected_agent, confidence_score)
        """
        # Find best agent
        agent, score = self.registry.find_best_agent(task_description)
        
        # Record routing decision
        self.routing_history.append({
            "task": task_description,
            "assigned_agent": agent.name if agent else None,
            "confidence": score
        })
        
        return agent, score
    
    def route_by_type(self, agent_type: str) -> Optional[Agent]:
        """
        Route to a specific agent type (first available).
        
        Args:
            agent_type: Type of agent to use
            
        Returns:
            Agent or None if type not found
        """
        agents = self.registry.get_agents_by_type(agent_type)
        
        if agents:
            # Return first agent of this type
            return agents[0]
        
        return None
    
    def route_to_least_busy(self, agent_type: str = None) -> Optional[Agent]:
        """
        Route to the least busy agent.
        
        Args:
            agent_type: Optional filter by agent type
            
        Returns:
            Least busy agent
        """
        if agent_type:
            candidates = self.registry.get_agents_by_type(agent_type)
        else:
            candidates = self.registry.get_all_agents()
        
        if not candidates:
            return None
        
        # Find agent with lowest task count
        return min(candidates, key=lambda a: a.task_count)
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_routes = len(self.routing_history)
        successful_routes = sum(1 for r in self.routing_history if r["assigned_agent"])
        
        return {
            "total_routes": total_routes,
            "successful_routes": successful_routes,
            "success_rate": successful_routes / total_routes if total_routes > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    from agent import SupervisorAgent, WorkerAgent
    
    # Create registry and router
    registry = AgentRegistry()
    router = Router(registry)
    
    # Register agents
    supervisor = SupervisorAgent()
    worker_generic = WorkerAgent(worker_type="generic")
    worker_telecom = WorkerAgent(worker_type="telecom")
    
    registry.register_agent(supervisor)
    registry.register_agent(worker_generic)
    registry.register_agent(worker_telecom)
    
    # Route tasks
    agent1, score1 = router.route_task("Analyze telecom KPIs")
    print(f"Task 1 routed to: {agent1.name} (score: {score1})")
    
    agent2, score2 = router.route_task("Execute generic task")
    print(f"Task 2 routed to: {agent2.name} (score: {score2})")
    
    # Get statistics
    print(f"Routing stats: {router.get_routing_statistics()}")
