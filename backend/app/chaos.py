"""
Chaos engineering experiments for testing system resilience.
"""
import structlog
from typing import Optional
from enum import Enum
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class ChaosExperiment(str, Enum):
    """Types of chaos experiments."""
    LATENCY_INJECTION = "latency_injection"
    ERROR_INJECTION = "error_injection"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_PRESSURE = "cpu_pressure"
    NETWORK_FAILURE = "network_failure"


class ChaosEngine:
    """Engine for running chaos experiments."""
    
    def __init__(self):
        self.active_experiments = set()
        logger.info("Chaos engine initialized")
    
    def inject_latency(self, duration_ms: int = 1000):
        """Inject latency into requests."""
        if not settings.CHAOS_ENABLED:
            return
        
        experiment_id = f"latency_{duration_ms}ms"
        self.active_experiments.add(experiment_id)
        logger.info(
            "chaos.experiment.start",
            experiment=ChaosExperiment.LATENCY_INJECTION,
            duration_ms=duration_ms,
            experiment_id=experiment_id,
        )
        
        # In a real implementation, we'd use middleware or proxy to inject latency
        # For now, we'll just log it
        
        return experiment_id
    
    def inject_error(self, error_rate: float = 0.1, status_code: int = 500):
        """Inject errors into responses."""
        if not settings.CHAOS_ENABLED:
            return
        
        experiment_id = f"error_{status_code}_{int(error_rate*100)}pct"
        self.active_experiments.add(experiment_id)
        logger.info(
            "chaos.experiment.start",
            experiment=ChaosExperiment.ERROR_INJECTION,
            error_rate=error_rate,
            status_code=status_code,
            experiment_id=experiment_id,
        )
        
        return experiment_id
    
    def stop_experiment(self, experiment_id: str):
        """Stop a running experiment."""
        if experiment_id in self.active_experiments:
            self.active_experiments.remove(experiment_id)
            logger.info(
                "chaos.experiment.stop",
                experiment_id=experiment_id,
            )
            return True
        return False
    
    def list_active_experiments(self) -> list:
        """List all active experiments."""
        return list(self.active_experiments)
    
    def clear_all_experiments(self):
        """Stop all active experiments."""
        count = len(self.active_experiments)
        self.active_experiments.clear()
        logger.info(
            "chaos.experiment.clear_all",
            count=count,
        )


# Global chaos engine
chaos_engine = ChaosEngine()


def setup_chaos_middleware(app):
    """Setup chaos engineering middleware."""
    if not settings.CHAOS_ENABLED:
        logger.info("Chaos engineering disabled")
        return
    
    logger.info("Chaos engineering middleware enabled")
    # In a real implementation, we'd add middleware here to actually inject faults
    # For now, we just log that it's enabled