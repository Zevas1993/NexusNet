"""Base expert class for NexusNet HiveMind"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import time

class ExpertResponse(BaseModel):
    """Response from an expert"""
    expert_name: str
    response: str
    confidence: float
    reasoning: Optional[str] = None
    sources: List[str] = []
    processing_time: float
    
class BaseExpert(ABC):
    """Base class for all experts in the HiveMind"""
    
    def __init__(self, name: str, specialties: List[str], config: Dict[str, Any]):
        self.name = name
        self.specialties = specialties
        self.config = config
        self.enabled = config.get('enabled', True)
        self.temperature = config.get('temperature', 0.7)
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        
    @abstractmethod
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Return confidence score (0-1) for handling this query"""
        pass
    
    @abstractmethod
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process the query and return response"""
        pass
    
    def _calculate_confidence(self, query: str, context: Dict[str, Any]) -> float:
        """Calculate confidence based on query relevance to specialties"""
        query_lower = query.lower()
        context_text = str(context).lower()
        
        specialty_matches = 0
        for specialty in self.specialties:
            if specialty.lower() in query_lower or specialty.lower() in context_text:
                specialty_matches += 1
        
        base_confidence = min(specialty_matches / len(self.specialties), 1.0)
        return base_confidence * 0.9  # Never claim 100% confidence
    
    def _format_response(self, response: str, confidence: float, reasoning: str = None) -> ExpertResponse:
        """Format response with metadata"""
        return ExpertResponse(
            expert_name=self.name,
            response=response,
            confidence=confidence,
            reasoning=reasoning,
            processing_time=time.time()
        )
