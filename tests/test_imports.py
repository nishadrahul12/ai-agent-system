"""
Test that all modules can be imported successfully.
This catches syntax errors and import issues.
"""

def test_orchestrator_imports():
    """Test orchestrator module imports."""
    try:
        from orchestrator import agent
        from orchestrator import agent_registry
        from orchestrator import router
        from orchestrator import task_queue
        from orchestrator import orchestrator
        from orchestrator import config
        assert True
    except ImportError as e:
        assert False, f"Orchestrator import failed: {e}"


def test_memory_imports():
    """Test memory module imports."""
    try:
        from memory import long_term_memory
        from memory import memory_retriever
        from memory import vector_store
        from memory import memory_summarizer
        from memory import memory_manager
        assert True
    except ImportError as e:
        assert False, f"Memory import failed: {e}"


def test_multiagent_imports():
    """Test multiagent module imports."""
    try:
        from multiagent import message
        from multiagent import message_broker
        from multiagent import agent_communication
        from multiagent import drift_detector
        from multiagent import reliability_monitor
        from multiagent import workflow_coordinator
        assert True
    except ImportError as e:
        assert False, f"Multiagent import failed: {e}"


def test_trust_safety_imports():
    """Test trust_safety module imports."""
    try:
        from trust_safety import privacy_checker
        from trust_safety import security_scanner
        from trust_safety import risk_engine
        from trust_safety import supervisor_repair
        from trust_safety import safety_guardrails
        assert True
    except ImportError as e:
        assert False, f"Trust & Safety import failed: {e}"


def test_evolution_imports():
    """Test evolution module imports."""
    try:
        from evolution import prompt_evaluator
        from evolution import genetic_algorithm
        from evolution import prompt_evolver
        from evolution import evolution_metrics
        assert True
    except ImportError as e:
        assert False, f"Evolution import failed: {e}"
