"""Code expert for software development and programming"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse
import re

class CodeExpert(BaseExpert):
    """Expert in software development, programming, and technical implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="code",
            specialties=["programming", "coding", "software", "development", "debugging", "algorithms", "architecture"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Determine if this is a programming-related query"""
        programming_keywords = [
            'code', 'programming', 'software', 'development', 'algorithm',
            'function', 'class', 'method', 'variable', 'debug', 'bug',
            'python', 'javascript', 'java', 'cpp', 'rust', 'go', 'php',
            'html', 'css', 'sql', 'api', 'framework', 'library', 'package',
            'git', 'github', 'repository', 'commit', 'branch', 'merge',
            'database', 'server', 'client', 'frontend', 'backend', 'fullstack'
        ]
        
        query_lower = query.lower()
        context_text = str(context).lower()
        combined_text = f"{query_lower} {context_text}"
        
        matches = sum(1 for keyword in programming_keywords if keyword in combined_text)
        confidence = min(matches / 4, 1.0)
        
        # Boost confidence for code patterns
        if re.search(r'\bdef\b|\bclass\b|\bimport\b|\bfrom\b', query):
            confidence += 0.3
        if re.search(r'[{}();]', query):
            confidence += 0.2
        
        return min(confidence, 0.95)
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process programming query"""
        confidence = self.can_handle(query, context)
        
        if confidence < self.confidence_threshold:
            return self._format_response(
                "This doesn't appear to be a programming-related question I can help with.",
                confidence,
                "Query doesn't match programming expertise areas"
            )
        
        system_prompt = f"""
You are a senior software engineer and programming expert with expertise in:
- Multiple programming languages (Python, JavaScript, Java, C++, etc.)
- Software architecture and design patterns
- Algorithms and data structures
- Debugging and problem-solving
- Best practices and code quality
- Modern development tools and frameworks

Provide clear, practical programming advice including:
1. Working code examples when appropriate
2. Explanation of concepts and logic
3. Best practices and potential pitfalls
4. Alternative approaches when relevant
5. Performance and security considerations
"""
        
        response = f"""Looking at your programming question:

{query}

Here's my technical analysis and recommendations:

1. **Problem Analysis**: I can help break down the technical requirements
2. **Solution Approach**: Multiple implementation strategies to consider
3. **Code Quality**: Best practices for maintainable, efficient code
4. **Testing Strategy**: How to validate and debug the implementation
5. **Performance Considerations**: Optimization opportunities

Would you like me to provide specific code examples or dive deeper into any particular aspect?"""
        
        return self._format_response(
            response,
            confidence,
            f"High confidence based on programming keyword matches and technical patterns"
        )
