from .typing import Dict, List, Any, Optional, Callable
from .datetime import datetime
from .prompt_evaluator import PromptEvaluator
from .genetic_algorithm import GeneticAlgorithm
import json

class PromptEvolver:
    """
    Main orchestrator for prompt evolution.
    Evolves prompts to improve performance over time.
    """
    
    def __init__(self,
                 seed_prompt: str,
                 population_size: int = 10,
                 generations: int = 50,
                 mutation_rate: float = 0.2):
        """
        Initialize prompt evolver.
        
        Args:
            seed_prompt: Initial prompt to evolve
            population_size: Population size for GA
            generations: Number of generations
            mutation_rate: Mutation rate
        """
        self.seed_prompt = seed_prompt
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        self.evaluator = PromptEvaluator()
        self.ga = GeneticAlgorithm(
            population_size=population_size,
            mutation_rate=mutation_rate
        )
        
        self.evolution_log: List[Dict[str, Any]] = []
        self.best_prompts: List[Dict[str, Any]] = []
    
    def add_test_case(self, test_id: str, input_text: str, expected_output: str):
        """Add test case for evaluation."""
        self.evaluator.add_test_case(test_id, input_text, expected_output)
    
    def run_evolution(self) -> Dict[str, Any]:
        """
        Run prompt evolution.
        
        Returns:
            Evolution results
        """
        # Initialize GA population
        self.ga.initialize_population(self.seed_prompt)
        
        # Create fitness function using evaluator
        def fitness_func(prompt: str) -> float:
            evaluation = self.evaluator.evaluate_prompt(prompt)
            return evaluation["fitness_score"]
        
        # Run evolution
        self.ga.evolve(self.generations, fitness_func)
        
        # Get results
        best_individual = self.ga.get_best_individual()
        
        result = {
            "evolution_timestamp": datetime.now().isoformat(),
            "seed_prompt": self.seed_prompt,
            "generations_run": self.generations,
            "best_prompt": best_individual.prompt,
            "best_fitness": best_individual.fitness_score,
            "avg_fitness_final": self.ga.get_average_fitness(),
            "evolution_history": self.ga.evolution_history
        }
        
        self.evolution_log.append(result)
        self.best_prompts.append({
            "generation": self.generations,
            "prompt": best_individual.prompt,
            "fitness": best_individual.fitness_score,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_improvement(self) -> Dict[str, Any]:
        """Get improvement statistics."""
        if len(self.best_prompts) < 2:
            return {"message": "Need at least 2 evolution runs to compare"}
        
        first_fitness = self.best_prompts[0]["fitness"]
        latest_fitness = self.best_prompts[-1]["fitness"]
        
        improvement = (latest_fitness - first_fitness) / first_fitness * 100 if first_fitness > 0 else 0
        
        return {
            "initial_best_fitness": first_fitness,
            "current_best_fitness": latest_fitness,
            "improvement_percent": round(improvement, 2),
            "total_evolution_runs": len(self.best_prompts)
        }
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive evolution report."""
        if not self.evolution_log:
            return {"message": "No evolution runs yet"}
        
        latest = self.evolution_log[-1]
        
        return {
            "total_evaluations": len(self.evaluator.evaluation_history),
            "evolution_runs": len(self.evolution_log),
            "current_best_prompt": latest["best_prompt"],
            "current_best_fitness": latest["best_fitness"],
            "improvement": self.get_improvement(),
            "evolution_timeline": self.evolution_log
        }


# Example usage
if __name__ == "__main__":
    evolver = PromptEvolver(
        seed_prompt="You are a helpful assistant. Answer questions.",
        population_size=10,
        generations=20
    )
    
    # Add test cases
    evolver.add_test_case(
        "test_001",
        "What is machine learning?",
        "Machine learning is a subset of AI where systems learn from data"
    )
    evolver.add_test_case(
        "test_002",
        "Explain neural networks",
        "Neural networks are inspired by biological brains and process information"
    )
    
    # Run evolution
    result = evolver.run_evolution()
    print(f"Evolution result:\n{json.dumps(result, indent=2)}")
    
    # Get report
    report = evolver.get_evolution_report()
    print(f"\nEvolution report:\n{json.dumps(report, indent=2)}")
