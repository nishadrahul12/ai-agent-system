from .typing import List, Tuple, Dict, Any, Callable, Optional
import random
import string
from .datetime import datetime
from .copy import deepcopy

class Individual:
    """Represents a prompt individual in genetic algorithm."""
    
    def __init__(self, prompt: str, genes: List[str] = None):
        """
        Initialize individual.
        
        Args:
            prompt: Prompt text
            genes: Gene segments (prompt components)
        """
        self.prompt = prompt
        self.genes = genes or self._extract_genes(prompt)
        self.fitness_score = 0.0
        self.generation = 0
    
    def _extract_genes(self, prompt: str) -> List[str]:
        """Extract genes (segments) from prompt."""
        # Split prompt into sentences
        sentences = prompt.split('.')
        return [s.strip() for s in sentences if s.strip()]
    
    def to_prompt(self) -> str:
        """Convert genes back to prompt."""
        return '. '.join(self.genes) + '.'
    
    def copy(self):
        """Create a copy of this individual."""
        new_ind = Individual(self.prompt, deepcopy(self.genes))
        new_ind.fitness_score = self.fitness_score
        new_ind.generation = self.generation
        return new_ind


class GeneticAlgorithm:
    """
    Genetic algorithm for prompt evolution.
    Evolves prompts through selection, crossover, and mutation.
    """
    
    def __init__(self,
                 population_size: int = 10,
                 mutation_rate: float = 0.2,
                 crossover_rate: float = 0.8,
                 elite_percentage: float = 0.2):
        """
        Initialize genetic algorithm.
        
        Args:
            population_size: Size of population
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elite_percentage: Percentage of elite to preserve
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_percentage = elite_percentage
        self.elite_count = max(1, int(population_size * elite_percentage))
        self.population: List[Individual] = []
        self.generation = 0
        self.evolution_history: List[Dict[str, Any]] = []
    
    def initialize_population(self, seed_prompt: str):
        """
        Initialize population from seed prompt.
        
        Args:
            seed_prompt: Initial prompt to evolve
        """
        self.population = []
        
        # Add seed individual
        seed_individual = Individual(seed_prompt)
        self.population.append(seed_individual)
        
        # Create variations
        for _ in range(self.population_size - 1):
            variation = self._create_variation(seed_prompt)
            self.population.append(variation)
    
    def _create_variation(self, prompt: str) -> Individual:
        """Create a variation of a prompt."""
        genes = prompt.split('. ')
        
        # Random modifications
        for i in range(len(genes)):
            if random.random() < 0.3:
                genes[i] = self._mutate_gene(genes[i])
        
        new_prompt = '. '.join(genes) + '.'
        return Individual(new_prompt)
    
    def evaluate_population(self, fitness_func: Callable) -> float:
        """
        Evaluate fitness of entire population.
        
        Args:
            fitness_func: Function that takes prompt and returns fitness score
            
        Returns:
            Average fitness of population
        """
        for individual in self.population:
            individual.fitness_score = fitness_func(individual.prompt)
            individual.generation = self.generation
        
        return self.get_average_fitness()
    
    def evolve(self, generations: int, fitness_func: Callable):
        """
        Run evolution for specified generations.
        
        Args:
            generations: Number of generations
            fitness_func: Fitness evaluation function
        """
        for gen in range(generations):
            self.generation = gen
            
            # Evaluate
            avg_fitness = self.evaluate_population(fitness_func)
            
            # Store history
            best_individual = max(self.population, key=lambda x: x.fitness_score)
            self.evolution_history.append({
                "generation": gen,
                "best_fitness": best_individual.fitness_score,
                "avg_fitness": avg_fitness,
                "best_prompt": best_individual.prompt
            })
            
            # Selection & Reproduction
            self.population = self._reproduction()
    
    def _reproduction(self) -> List[Individual]:
        """Create new population through selection, crossover, mutation."""
        # Sort by fitness
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Elitism: keep best individuals
        new_population = [ind.copy() for ind in self.population[:self.elite_count]]
        
        # Fill rest with offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < self.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self._mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        return new_population[:self.population_size]
    
    def _tournament_selection(self, tournament_size: int = 3) -> Individual:
        """Tournament selection."""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Crossover (breed) two parents."""
        genes1 = parent1.genes.copy()
        genes2 = parent2.genes.copy()
        
        # Single-point crossover
        crossover_point = random.randint(1, min(len(genes1), len(genes2)) - 1)
        
        # Create children
        child1_genes = genes1[:crossover_point] + genes2[crossover_point:]
        child2_genes = genes2[:crossover_point] + genes1[crossover_point:]
        
        child1 = Individual('. '.join(child1_genes) + '.', child1_genes)
        child2 = Individual('. '.join(child2_genes) + '.', child2_genes)
        
        return child1, child2
    
    def _mutate(self, individual: Individual) -> Individual:
        """Mutate an individual."""
        new_ind = individual.copy()
        
        if new_ind.genes and random.random() < 0.5:
            # Mutate a gene
            idx = random.randint(0, len(new_ind.genes) - 1)
            new_ind.genes[idx] = self._mutate_gene(new_ind.genes[idx])
        else:
            # Add or remove a gene
            if random.random() < 0.5 and new_ind.genes:
                new_ind.genes.pop(random.randint(0, len(new_ind.genes) - 1))
            else:
                new_ind.genes.append(self._generate_new_gene())
        
        new_ind.prompt = '. '.join(new_ind.genes) + '.'
        return new_ind
    
    def _mutate_gene(self, gene: str) -> str:
        """Mutate a single gene."""
        mutations = [
            f"Carefully {gene}",
            f"{gene} with precision",
            f"Thoroughly {gene}",
            f"{gene} and validate results",
            f"{gene} step by step"
        ]
        return random.choice(mutations)
    
    def _generate_new_gene(self) -> str:
        """Generate a new random gene."""
        gene_templates = [
            "Check your work",
            "Provide detailed reasoning",
            "Use structured format",
            "Double-check calculations",
            "Explain your logic",
            "Validate assumptions"
        ]
        return random.choice(gene_templates)
    
    def get_best_individual(self) -> Individual:
        """Get best individual in population."""
        return max(self.population, key=lambda x: x.fitness_score)
    
    def get_average_fitness(self) -> float:
        """Get average fitness of population."""
        if not self.population:
            return 0.0
        return sum(ind.fitness_score for ind in self.population) / len(self.population)


# Example usage
if __name__ == "__main__":
    ga = GeneticAlgorithm(population_size=10, mutation_rate=0.2, crossover_rate=0.8)
    
    # Initialize
    seed_prompt = "You are a helpful assistant. Answer questions clearly."
    ga.initialize_population(seed_prompt)
    
    # Fitness function
    def fitness_func(prompt):
        # Longer, more detailed prompts score higher (simplified example)
        return min(len(prompt.split()) / 50, 1.0)
    
    # Evolve
    ga.evolve(generations=10, fitness_func=fitness_func)
    
    # Results
    best = ga.get_best_individual()
    print(f"Best prompt: {best.prompt}")
    print(f"Best fitness: {best.fitness_score}")
    print(f"Evolution history: {ga.evolution_history[-3:]}")
