"""Data science expert for analytics, ML, and data processing"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse
import re

class DataScienceExpert(BaseExpert):
    """Expert in data science, machine learning, and analytics"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="datascience",
            specialties=["data", "analytics", "machine learning", "ml", "statistics", "visualization", "modeling"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Determine if this is a data science-related query"""
        ds_keywords = [
            'data', 'dataset', 'analytics', 'analysis', 'machine learning', 'ml',
            'statistics', 'statistical', 'model', 'modeling', 'prediction',
            'classification', 'regression', 'clustering', 'neural network',
            'deep learning', 'ai', 'artificial intelligence', 'pandas',
            'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'visualization',
            'plot', 'chart', 'graph', 'matplotlib', 'seaborn', 'plotly',
            'correlation', 'feature', 'algorithm', 'training', 'testing',
            'validation', 'cross-validation', 'overfitting', 'underfitting'
        ]
        
        query_lower = query.lower()
        context_text = str(context).lower()
        combined_text = f"{query_lower} {context_text}"
        
        matches = sum(1 for keyword in ds_keywords if keyword in combined_text)
        confidence = min(matches / 4, 1.0)
        
        # Boost for data science patterns
        if re.search(r'\bdf\.|\bnp\.|\bpd\.|sklearn', query):
            confidence += 0.3
        if re.search(r'accuracy|precision|recall|f1.score', query_lower):
            confidence += 0.2
        
        return min(confidence, 0.95)
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process data science query"""
        confidence = self.can_handle(query, context)
        
        if confidence < self.confidence_threshold:
            return self._format_response(
                "This doesn't appear to be a data science question I can help with.",
                confidence,
                "Query doesn't match data science expertise areas"
            )
        
        response = f"""Based on your data science question:

{query}

Here's my analysis and recommendations:

**Data Science Approach:**
1. **Data Exploration**: Understanding the data structure, quality, and patterns
2. **Feature Engineering**: Selecting and transforming relevant variables
3. **Model Selection**: Choosing appropriate algorithms for the problem type
4. **Evaluation Strategy**: Metrics and validation techniques
5. **Implementation**: Python/R code examples and best practices

**Key Considerations:**
- Data quality and preprocessing requirements
- Model interpretability vs. performance trade-offs
- Potential biases and ethical implications
- Scalability and production deployment

Would you like me to provide specific code examples or dive deeper into any analytical technique?"""
        
        return self._format_response(
            response,
            confidence,
            f"High confidence based on data science keyword matches and analytical patterns"
        )
