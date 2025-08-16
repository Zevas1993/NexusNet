from typing import Dict, Any, List
from core.experts.base import ExpertBase
from core.config import hivemind_config, experts_config
from core.models.local_transformers import TransformersClient
from core.models.local_llama_cpp import LlamaCppClient
from core.models.http_vllm import VLLMClient
from core.rag.teacher import TeacherGate
import asyncio

class HiveMindOrchestrator:
    def __init__(self):
        self.config = hivemind_config()
        self.experts: Dict[str, ExpertBase] = {}
        self.local_models = {}
        self.teacher_gate = TeacherGate()
        self._load_experts()
        self._initialize_models()
    
    def _load_experts(self):
        """Load all expert modules"""
        from core.experts import (
            code, cybersecurity, datascience, design, devops, education,
            finance, generalist, legal, marketing, math, medical,
            operations, product, research, search, translation, vision, writing
        )
        
        expert_classes = {
            'code': code.CodeExpert,
            'cybersecurity': cybersecurity.CybersecurityExpert,
            'datascience': datascience.DataScienceExpert,
            'design': design.DesignExpert,
            'devops': devops.DevOpsExpert,
            'education': education.EducationExpert,
            'finance': finance.FinanceExpert,
            'generalist': generalist.GeneralistExpert,
            'legal': legal.LegalExpert,
            'marketing': marketing.MarketingExpert,
            'math': math.MathExpert,
            'medical': medical.MedicalExpert,
            'operations': operations.OperationsExpert,
            'product': product.ProductExpert,
            'research': research.ResearchExpert,
            'search': search.SearchExpert,
            'translation': translation.TranslationExpert,
            'vision': vision.VisionExpert,
            'writing': writing.WritingExpert,
        }
        
        for name, expert_class in expert_classes.items():
            self.experts[name] = expert_class()
    
    def _initialize_models(self):
        """Initialize local model backends"""
        # Initialize models based on config
        pass
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query through HiveMind"""
        context = context or {}
        
        # Route to appropriate experts
        expert_results = await self._route_to_experts(query, context)
        
        # Get teacher guidance if available
        teacher_result = None
        if self.teacher_gate.is_available():
            teacher_result = await self.teacher_gate.get_teacher_response(query, context)
        
        # Synthesize final response
        final_response = await self._synthesize_response(expert_results, teacher_result, query)
        
        return {
            'query': query,
            'expert_results': expert_results,
            'teacher_result': teacher_result,
            'final_response': final_response,
            'consensus': self._calculate_consensus(expert_results)
        }
    
    async def _route_to_experts(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Route query to relevant experts"""
        results = []
        
        # Calculate confidence scores for all experts
        expert_scores = [(name, expert.can_handle(query)) for name, expert in self.experts.items()]
        expert_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top experts above threshold
        threshold = 0.3
        selected_experts = [(name, score) for name, score in expert_scores if score >= threshold]
        
        # Process with selected experts concurrently
        tasks = []
        for name, score in selected_experts[:5]:  # Limit to top 5
            task = self.experts[name].process(query, context)
            tasks.append((name, score, task))
        
        for name, score, task in tasks:
            try:
                result = await task
                result['selection_score'] = score
                results.append(result)
            except Exception as e:
                results.append({
                    'expert': name,
                    'error': str(e),
                    'selection_score': score
                })
        
        return results
    
    async def _synthesize_response(self, expert_results: List[Dict[str, Any]], teacher_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Synthesize final response from expert and teacher inputs"""
        # Simple synthesis - can be enhanced with more sophisticated logic
        primary_response = ""
        confidence = 0.0
        
        if expert_results:
            # Use highest confidence expert response as primary
            best_expert = max(expert_results, key=lambda x: x.get('confidence', 0))
            primary_response = best_expert.get('response', '')
            confidence = best_expert.get('confidence', 0)
        
        # Enhance with teacher guidance if available
        if teacher_result and not teacher_result.get('error'):
            teacher_text = teacher_result.get('text', '')
            if teacher_text:
                primary_response = f"{primary_response}\n\nGuidance: {teacher_text[:200]}..."
                confidence = min(confidence + 0.2, 1.0)
        
        return {
            'text': primary_response,
            'confidence': confidence,
            'experts_consulted': len(expert_results),
            'teacher_available': teacher_result is not None and not teacher_result.get('error')
        }
    
    def _calculate_consensus(self, expert_results: List[Dict[str, Any]]) -> float:
        """Calculate consensus score among experts"""
        if len(expert_results) < 2:
            return 1.0
        
        confidences = [r.get('confidence', 0) for r in expert_results]
        avg_confidence = sum(confidences) / len(confidences)
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
        
        # Lower variance = higher consensus
        consensus = max(0, 1 - variance)
        return consensus