from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics

class DriftAlertLevel(Enum):
    """Drift alert severity levels."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"

class DriftDetector:
    """
    Detects when agents deviate from expected behavior (drift).
    Monitors quality metrics and alerts when thresholds are exceeded.
    """
    
    def __init__(self, 
                 baseline_window_size: int = 100,
                 deviation_threshold: float = 0.2):
        """
        Initialize drift detector.
        
        Args:
            baseline_window_size: Number of samples for baseline
            deviation_threshold: Threshold for drift detection (0-1)
        """
        self.baseline_window_size = baseline_window_size
        self.deviation_threshold = deviation_threshold
        self.agent_metrics: Dict[str, List[Dict[str, float]]] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.drift_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_metric(self, 
                     agent_id: str, 
                     metric_name: str, 
                     value: float,
                     timestamp: Optional[datetime] = None):
        """
        Record a metric for an agent.
        
        Args:
            agent_id: Agent ID
            metric_name: Name of metric
            value: Metric value
            timestamp: Optional timestamp
        """
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = []
        
        metric = {
            "metric": metric_name,
            "value": value,
            "timestamp": timestamp or datetime.now()
        }
        
        self.agent_metrics[agent_id].append(metric)
        
        # Keep only recent metrics
        if len(self.agent_metrics[agent_id]) > self.baseline_window_size * 2:
            self.agent_metrics[agent_id] = self.agent_metrics[agent_id][-self.baseline_window_size:]
    
    def compute_baseline(self, agent_id: str, metric_name: str) -> Optional[float]:
        """
        Compute baseline (average) for a metric.
        
        Args:
            agent_id: Agent ID
            metric_name: Metric name
            
        Returns:
            Average value or None
        """
        if agent_id not in self.agent_metrics:
            return None
        
        values = [
            m["value"] for m in self.agent_metrics[agent_id]
            if m["metric"] == metric_name
        ]
        
        if len(values) < self.baseline_window_size:
            return None
        
        # Use first baseline_window_size samples
        baseline = statistics.mean(values[:self.baseline_window_size])
        
        if agent_id not in self.baselines:
            self.baselines[agent_id] = {}
        
        self.baselines[agent_id][metric_name] = baseline
        
        return baseline
    
    def detect_drift(self, 
                    agent_id: str, 
                    metric_name: str, 
                    current_value: float) -> Tuple[bool, float]:
        """
        Detect if metric has drifted.
        
        Args:
            agent_id: Agent ID
            metric_name: Metric name
            current_value: Current value
            
        Returns:
            Tuple of (has_drifted, drift_score)
        """
        baseline = self.baselines.get(agent_id, {}).get(metric_name)
        
        if baseline is None:
            return False, 0.0
        
        # Calculate drift as percentage deviation
        if baseline == 0:
            drift_score = 1.0 if current_value != 0 else 0.0
        else:
            drift_score = abs(current_value - baseline) / abs(baseline)
        
        has_drifted = drift_score > self.deviation_threshold
        
        return has_drifted, drift_score
    
    def analyze_agent_drift(self, agent_id: str) -> Dict[str, Any]:
        """
        Comprehensive drift analysis for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Drift analysis report
        """
        if agent_id not in self.agent_metrics:
            return {"error": "No metrics found"}
        
        # Compute baselines if not exists
        metrics_set = set()
        for m in self.agent_metrics[agent_id]:
            metrics_set.add(m["metric"])
        
        for metric_name in metrics_set:
            if metric_name not in self.baselines.get(agent_id, {}):
                self.compute_baseline(agent_id, metric_name)
        
        # Analyze drift for each metric
        drift_metrics = {}
        overall_drift_score = 0.0
        drifted_count = 0
        
        # Get recent values
        recent_metrics = self.agent_metrics[agent_id][-50:] if self.agent_metrics[agent_id] else []
        
        for metric_name in metrics_set:
            recent_values = [m["value"] for m in recent_metrics if m["metric"] == metric_name]
            
            if recent_values:
                current_value = statistics.mean(recent_values)
                has_drifted, drift_score = self.detect_drift(agent_id, metric_name, current_value)
                
                drift_metrics[metric_name] = {
                    "baseline": self.baselines.get(agent_id, {}).get(metric_name, 0),
                    "current": current_value,
                    "drift_score": drift_score,
                    "drifted": has_drifted
                }
                
                if has_drifted:
                    drifted_count += 1
                
                overall_drift_score += drift_score
        
        if metrics_set:
            overall_drift_score /= len(metrics_set)
        
        # Determine alert level
        if overall_drift_score > 0.5:
            alert_level = DriftAlertLevel.CRITICAL
        elif overall_drift_score > self.deviation_threshold:
            alert_level = DriftAlertLevel.WARNING
        else:
            alert_level = DriftAlertLevel.NORMAL
        
        report = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": drift_metrics,
            "overall_drift_score": round(overall_drift_score, 3),
            "drifted": overall_drift_score > self.deviation_threshold,
            "drifted_metrics_count": drifted_count,
            "total_metrics": len(metrics_set),
            "alert_level": alert_level.value
        }
        
        # Store in history
        if agent_id not in self.drift_history:
            self.drift_history[agent_id] = []
        
        self.drift_history[agent_id].append(report)
        
        return report
    
    def get_drift_history(self, agent_id: str, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get recent drift reports for an agent."""
        history = self.drift_history.get(agent_id, [])
        return history[-last_n:] if history else []


# Example usage
if __name__ == "__main__":
    detector = DriftDetector()
    
    # Record baseline metrics
    for i in range(100):
        detector.record_metric("agent_001", "output_quality", 0.92 + (i % 5) * 0.01)
        detector.record_metric("agent_001", "response_time", 1200 + (i % 100))
    
    # Compute baselines
    detector.compute_baseline("agent_001", "output_quality")
    detector.compute_baseline("agent_001", "response_time")
    
    # Record drifted metrics
    for i in range(10):
        detector.record_metric("agent_001", "output_quality", 0.75 + (i % 3) * 0.02)
        detector.record_metric("agent_001", "response_time", 2500 + (i % 50))
    
    # Analyze drift
    analysis = detector.analyze_agent_drift("agent_001")
    print(f"Drift analysis: {analysis}")
