"""Product management expert"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse

class ProductExpert(BaseExpert):
    """Expert in product management and development"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="product",
            specialties=["product", "management", "strategy", "roadmap", "requirements", "user experience"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Determine if this is a product management query"""
        product_keywords = [
            'product', 'product management', 'roadmap', 'strategy', 'requirements',
            'user story', 'feature', 'epic', 'sprint', 'agile', 'scrum',
            'stakeholder', 'customer', 'user experience', 'ux', 'market',
            'competitive analysis', 'mvp', 'go-to-market', 'launch', 'metrics',
            'kpi', 'okr', 'prioritization', 'backlog', 'user research'
        ]
        
        query_lower = query.lower()
        context_text = str(context).lower()
        combined_text = f"{query_lower} {context_text}"
        
        matches = sum(1 for keyword in product_keywords if keyword in combined_text)
        confidence = min(matches / 4, 1.0)
        
        return min(confidence, 0.95)
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process product management query"""
        confidence = self.can_handle(query, context)
        
        if confidence < self.confidence_threshold:
            return self._format_response(
                "This doesn't appear to be a product management question I can help with.",
                confidence,
                "Query doesn't match product management expertise areas"
            )
        
        response = f"""Based on your product management question:

{query}

Here's my product strategy analysis:

**Product Framework:**
1. **User Research**: Understanding customer needs and pain points
2. **Market Analysis**: Competitive landscape and positioning
3. **Feature Prioritization**: Impact vs effort matrix
4. **Roadmap Planning**: Strategic milestones and timeline
5. **Success Metrics**: KPIs and measurement strategy

**Key Considerations:**
- User-centric design and development
- Cross-functional team alignment
- Technical feasibility and resource constraints
- Go-to-market strategy and launch planning
- Iterative improvement based on feedback

Would you like me to elaborate on any specific product management methodology or framework?"""
        
        return self._format_response(
            response,
            confidence,
            f"High confidence based on product management keyword matches"
        )
