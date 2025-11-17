from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import time

class HealthStatus(Enum):
    """Agent health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

class ReliabilityMonitor:
    """
    Monitors agent health, performance, and reliability.
    Tracks uptime, error rates, response times, and alerts on issues.
    """
    
    def __init__(self,
                 health_check_timeout: int = 10,
                 error_rate_threshold: float = 0.1,
                 response_time_threshold_ms: int = 5000):
        """
        Initialize reliability monitor.
        
        Args:
            health_check_timeout: Timeout for health checks (seconds)
            error_rate_threshold: Alert threshold for error rate
            response_time_threshold_ms: Alert threshold for response time
        """
        self.health_check_timeout = health_check_timeout
        self.error_rate_threshold = error_rate_threshold
        self.response_time_threshold_ms = response_time_threshold_ms
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        self.health_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alerts: Dict[str, List[Dict[str, str]]] = {}
    
    def register_agent(self, agent_id: str):
        """Register an agent for monitoring."""
        if agent_id not in self.agent_health:
            self.agent_health[agent_id] = {
                "agent_id": agent_id,
                "status": HealthStatus.HEALTHY.value,
                "uptime_start": datetime.now(),
                "task_count": 0,
                "success_count": 0,
                "error_count": 0,
                "total_response_time_ms": 0,
                "last_health_check": datetime.now(),
                "last_activity": datetime.now(),
                "response_times": []
            }
    
    def record_task_completion(self, 
                              agent_id: str, 
                              success: bool, 
                              response_time_ms: int):
        """
        Record task completion.
        
        Args:
            agent_id: Agent ID
            success: Whether task succeeded
            response_time_ms: Response time in milliseconds
        """
        if agent_id not in self.agent_health:
            self.register_agent(agent_id)
        
        health = self.agent_health[agent_id]
        health["task_count"] += 1
        health["total_response_time_ms"] += response_time_ms
        health["response_times"].append(response_time_ms)
        health["last_activity"] = datetime.now()
        
        # Keep only last 100 response times
        if len(health["response_times"]) > 100:
            health["response_times"] = health["response_times"][-100:]
        
        if success:
            health["success_count"] += 1
        else:
            health["error_count"] += 1
        
        # Check for alerts
        self._check_alerts(agent_id)
    
    def health_check(self, agent_id: str) -> Dict[str, Any]:
        """
        Perform health check on agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Health check result
        """
        if agent_id not in self.agent_health:
            self.register_agent(agent_id)
        
        health = self.agent_health[agent_id]
        
        # Calculate metrics
        uptime_seconds = (datetime.now() - health["uptime_start"]).total_seconds()
        uptime_percent = (uptime_seconds / (uptime_seconds + health["error_count"] * 60)) * 100 if uptime_seconds > 0 else 100
        
        error_rate = (health["error_count"] / health["task_count"]) if health["task_count"] > 0 else 0
        
        avg_response_time = (health["total_response_time_ms"] / health["task_count"]) if health["task_count"] > 0 else 0
        
        success_rate = (health["success_count"] / health["task_count"]) if health["task_count"] > 0 else 0
        
        # Determine status
        if health["task_count"] == 0:
            status = HealthStatus.OFFLINE.value
        elif error_rate > self.error_rate_threshold or avg_response_time > self.response_time_threshold_ms:
            status = HealthStatus.CRITICAL.value
        elif error_rate > self.error_rate_threshold * 0.5:
            status = HealthStatus.DEGRADED.value
        else:
            status = HealthStatus.HEALTHY.value
        
        health["status"] = status
        health["last_health_check"] = datetime.now()
        
        # Check last activity timeout
        last_activity_seconds = (datetime.now() - health["last_activity"]).total_seconds()
        if last_activity_seconds > self.health_check_timeout * 60:
            status = HealthStatus.OFFLINE.value
        
        report = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "metrics": {
                "uptime_percent": round(uptime_percent, 2),
                "task_success_rate": round(success_rate, 3),
                "error_rate": round(error_rate, 3),
                "avg_response_time_ms": round(avg_response_time, 1),
                "total_tasks": health["task_count"],
                "error_count": health["error_count"]
            },
            "alerts": self.alerts.get(agent_id, [])
        }
        
        # Store in history
        if agent_id not in self.health_history:
            self.health_history[agent_id] = []
        
        self.health_history[agent_id].append(report)
        
        # Keep only last 100 reports
        if len(self.health_history[agent_id]) > 100:
            self.health_history[agent_id] = self.health_history[agent_id][-100:]
        
        return report
    
    def _check_alerts(self, agent_id: str):
        """Check for alert conditions."""
        if agent_id not in self.alerts:
            self.alerts[agent_id] = []
        
        health = self.agent_health[agent_id]
        
        # Check error rate
        if health["task_count"] > 0:
            error_rate = health["error_count"] / health["task_count"]
            if error_rate > self.error_rate_threshold:
                self.alerts[agent_id].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "HIGH_ERROR_RATE",
                    "value": round(error_rate, 3),
                    "threshold": self.error_rate_threshold
                })
        
        # Check response time
        if health["response_times"]:
            avg_response_time = sum(health["response_times"][-10:]) / len(health["response_times"][-10:])
            if avg_response_time > self.response_time_threshold_ms:
                self.alerts[agent_id].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "SLOW_RESPONSE",
                    "value": round(avg_response_time, 1),
                    "threshold": self.response_time_threshold_ms
                })
        
        # Keep only last 20 alerts
        if len(self.alerts[agent_id]) > 20:
            self.alerts[agent_id] = self.alerts[agent_id][-20:]
    
    def get_health_status(self, agent_id: str) -> str:
        """Get current health status."""
        report = self.health_check(agent_id)
        return report["status"]
    
    def get_all_agents_status(self) -> Dict[str, str]:
        """Get status of all monitored agents."""
        return {
            agent_id: self.get_health_status(agent_id)
            for agent_id in self.agent_health.keys()
        }
    
    def get_health_history(self, agent_id: str, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get recent health history for an agent."""
        history = self.health_history.get(agent_id, [])
        return history[-last_n:] if history else []


# Example usage
if __name__ == "__main__":
    monitor = ReliabilityMonitor()
    
    # Register agents
    monitor.register_agent("agent_001")
    monitor.register_agent("agent_002")
    
    # Record successful tasks
    for i in range(90):
        monitor.record_task_completion("agent_001", True, 1200 + (i % 500))
    
    # Record some failures
    for i in range(10):
        monitor.record_task_completion("agent_001", False, 5000 + (i % 1000))
    
    # Health check
    health = monitor.health_check("agent_001")
    print(f"Health report: {health}")
    
    # All agents status
    status = monitor.get_all_agents_status()
    print(f"All agents status: {status}")
