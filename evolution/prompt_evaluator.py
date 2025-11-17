from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import random

class PromptEvaluator:
    """
    Evaluates prompt performance using test cases.
    Scores prompts based on quality, speed, and consistency.
    """
    
    def __init__(self):
        """Initialize prompt evaluator."""
        self.test_cases: List[Dict[str, Any]] = []
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def add_test_case(self, 
                      test_id: str,
                      input_text: str,
                      expected_output: str,
                      test_type: str = "functional"):
        """
        Add a test case for evaluation.
        
        Args:
            test_id: Test identifier
            input_text: Input to test
            expected_output: Expected output
            test_type: Type of test
        """
        test_case = {
            "test_id": test_id,
            "input": input_text,
            "expected": expected_output,
            "type": test_type
        }
        self.test_cases.append(test_case)
    
    def evaluate_prompt(self, 
                       prompt: str,
                       agent_response_func=None) -> Dict[str, Any]:
        """
        Evaluate a prompt using test cases.
        
        Args:
            prompt: Prompt to evaluate
            agent_response_func: Function that generates response given prompt & input
            
        Returns:
            Evaluation report with fitness score
        """
        results = []
        quality_scores = []
        speed_scores = []
        consistency_scores = []
        
        # Test against all test cases
        for test_case in self.test_cases:
            # Simulate agent response (in real system, call actual agent)
            if agent_response_func:
                import time
                start_time = time.time()
                response = agent_response_func(prompt, test_case["input"])
                response_time = (time.time() - start_time) * 1000  # ms
            else:
                # Placeholder simulation
                response = self._simulate_response(prompt, test_case["input"])
                response_time = random.uniform(800, 3000)
            
            # Quality score (how well does it match expected output?)
            quality_score = self._calculate_quality_score(
                response, 
                test_case["expected"]
            )
            quality_scores.append(quality_score)
            
            # Speed score (response time performance)
            speed_score = self._calculate_speed_score(response_time)
            speed_scores.append(speed_score)
            
            # Consistency score (determinism)
            consistency_score = self._calculate_consistency_score(prompt, response)
            consistency_scores.append(consistency_score)
            
            results.append({
                "test_id": test_case["test_id"],
                "quality": quality_score,
                "speed_ms": response_time,
                "consistency": consistency_score
            })
        
        # Calculate average scores
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        avg_speed = sum(speed_scores) / len(speed_scores) if speed_scores else 0
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
        
        # Combined fitness
        fitness_score = (avg_quality * 0.5) + (avg_speed * 0.2) + (avg_consistency * 0.3)
        
        evaluation = {
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "average_scores": {
                "quality": round(avg_quality, 3),
                "speed": round(avg_speed, 3),
                "consistency": round(avg_consistency, 3)
            },
            "fitness_score": round(fitness_score, 3),
            "tests_passed": sum(1 for r in results if r["quality"] > 0.7),
            "total_tests": len(results)
        }
        
        self.evaluation_history.append(evaluation)
        
        return evaluation
    
    def _calculate_quality_score(self, response: str, expected: str) -> float:
        """Calculate quality score based on response correctness."""
        if not response or not expected:
            return 0.0
        
        # Simple similarity scoring
        response_lower = response.lower()
        expected_lower = expected.lower()
        
        # Check if key terms are present
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        
        if not expected_words:
            return 0.0
        
        matches = len(expected_words & response_words)
        similarity = matches / len(expected_words)
        
        return min(similarity, 1.0)
    
    def _calculate_speed_score(self, response_time_ms: float) -> float:
        """Calculate speed score based on response time."""
        # Baseline: 1000ms is optimal (score = 1.0)
        # 3000ms is acceptable (score = 0.5)
        # 5000ms+ is too slow (score = 0)
        
        if response_time_ms <= 1000:
            return 1.0
        elif response_time_ms <= 3000:
            return 1.0 - ((response_time_ms - 1000) / 2000) * 0.5
        elif response_time_ms <= 5000:
            return 0.5 - ((response_time_ms - 3000) / 2000) * 0.5
        else:
            return 0.0
    
    def _calculate_consistency_score(self, prompt: str, response: str) -> float:
        """Calculate consistency score."""
        # In real system, would test prompt multiple times with same input
        # For now, return high score (would be deterministic in production)
        return random.uniform(0.8, 1.0)
    
    def _simulate_response(self, prompt: str, input_text: str) -> str:
        """Simulate agent response for testing."""
        # Placeholder: in real system, call actual agent
        return f"Response based on: {input_text[:20]}"
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        if not self.evaluation_history:
            return {"message": "No evaluations yet"}
        
        fitness_scores = [e["fitness_score"] for e in self.evaluation_history]
        
        return {
            "total_evaluations": len(self.evaluation_history),
            "best_fitness": max(fitness_scores),
            "avg_fitness": sum(fitness_scores) / len(fitness_scores),
            "worst_fitness": min(fitness_scores),
            "improvement_over_time": self._calculate_improvement_trend()
        }
    
    def _calculate_improvement_trend(self) -> float:
        """Calculate fitness improvement trend."""
        if len(self.evaluation_history) < 2:
            return 0.0
        
        first_half_avg = sum(
            e["fitness_score"] for e in self.evaluation_history[:len(self.evaluation_history)//2]
        ) / (len(self.evaluation_history) // 2)
        
        second_half_avg = sum(
            e["fitness_score"] for e in self.evaluation_history[len(self.evaluation_history)//2:]
        ) / (len(self.evaluation_history) - len(self.evaluation_history)//2)
        
        return second_half_avg - first_half_avg


# Example usage
if __name__ == "__main__":
    evaluator = PromptEvaluator()
    
    # Add test cases
    evaluator.add_test_case(
        "test_001",
        "What is 2+2?",
        "The answer is 4"
    )
    evaluator.add_test_case(
        "test_002",
        "Explain recursion",
        "Recursion is a function calling itself"
    )
    
    # Evaluate prompt
    prompt = "You are a helpful math tutor. Explain clearly and concisely."
    evaluation = evaluator.evaluate_prompt(prompt)
    print(f"Evaluation: {evaluation}")
    
    # Statistics
    stats = evaluator.get_evaluation_statistics()
    print(f"Statistics: {stats}")
