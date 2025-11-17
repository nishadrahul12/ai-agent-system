from .typing import Dict, List, Any
from .datetime import datetime
import statistics

class EvolutionMetrics:
    """
    Tracks and analyzes evolution metrics and performance.
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics_history: List[Dict[str, Any]] = []
    
    def record_generation(self,
                         generation: int,
                         population_fitness_scores: List[float],
                         best_fitness: float,
                         mutation_count: int = 0):
        """
        Record metrics for a generation.
        
        Args:
            generation: Generation number
            population_fitness_scores: List of all fitness scores
            best_fitness: Best fitness in this generation
            mutation_count: Number of mutations applied
        """
        if not population_fitness_scores:
            return
        
        avg_fitness = statistics.mean(population_fitness_scores)
        std_fitness = statistics.stdev(population_fitness_scores) if len(population_fitness_scores) > 1 else 0
        
        record = {
            "generation": generation,
            "timestamp": datetime.now().isoformat(),
            "population_size": len(population_fitness_scores),
            "best_fitness": best_fitness,
            "avg_fitness": avg_fitness,
            "std_fitness": std_fitness,
            "min_fitness": min(population_fitness_scores),
            "max_fitness": max(population_fitness_scores),
            "mutation_count": mutation_count
        }
        
        self.metrics_history.append(record)
    
    def get_convergence_rate(self) -> float:
        """
        Calculate convergence rate (how fast fitness improves).
        
        Returns:
            Convergence rate (higher = faster improvement)
        """
        if len(self.metrics_history) < 2:
            return 0.0
        
        # Look at first and second half
        mid = len(self.metrics_history) // 2
        first_half = [m["avg_fitness"] for m in self.metrics_history[:mid]]
        second_half = [m["avg_fitness"] for m in self.metrics_history[mid:]]
        
        if not first_half or not second_half:
            return 0.0
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if first_avg == 0:
            return 0.0
        
        return (second_avg - first_avg) / first_avg
    
    def get_diversity_trend(self) -> List[float]:
        """
        Get population diversity over time.
        Lower std dev = less diverse = converged.
        
        Returns:
            List of standard deviations by generation
        """
        return [m["std_fitness"] for m in self.metrics_history]
    
    def get_fitness_trend(self) -> Dict[str, List[float]]:
        """Get fitness trends over generations."""
        return {
            "best": [m["best_fitness"] for m in self.metrics_history],
            "avg": [m["avg_fitness"] for m in self.metrics_history],
            "min": [m["min_fitness"] for m in self.metrics_history],
            "max": [m["max_fitness"] for m in self.metrics_history]
        }
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.metrics_history:
            return {"message": "No metrics recorded"}
        
        best_fitnesses = [m["best_fitness"] for m in self.metrics_history]
        avg_fitnesses = [m["avg_fitness"] for m in self.metrics_history]
        
        return {
            "total_generations": len(self.metrics_history),
            "initial_best_fitness": best_fitnesses[0],
            "final_best_fitness": best_fitnesses[-1],
            "improvement": best_fitnesses[-1] - best_fitnesses[0],
            "improvement_percent": ((best_fitnesses[-1] - best_fitnesses[0]) / best_fitnesses[0] * 100) if best_fitnesses[0] > 0 else 0,
            "convergence_rate": round(self.get_convergence_rate(), 3),
            "avg_final_diversity": round(self.metrics_history[-1]["std_fitness"], 3)
        }


# Example usage
if __name__ == "__main__":
    metrics = EvolutionMetrics()
    
    # Record some generations
    import random
    for gen in range(50):
        fitness_scores = [random.uniform(0.5, 0.99) for _ in range(10)]
        best = max(fitness_scores)
        metrics.record_generation(gen, fitness_scores, best, mutation_count=random.randint(1, 3))
    
    # Get results
    summary = metrics.get_summary_statistics()
    print(f"Summary: {summary}")
    
    convergence = metrics.get_convergence_rate()
    print(f"Convergence rate: {convergence}")
