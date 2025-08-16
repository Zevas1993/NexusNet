"""Writing expert for creative and technical writing"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse
import re

class WritingExpert(BaseExpert):
    """Expert in creative writing, editing, and content creation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="writing",
            specialties=["writing", "editing", "creativity", "storytelling", "content", "copywriting"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Determine if this is a writing-related query"""
        writing_keywords = [
            'write', 'writing', 'edit', 'editing', 'story', 'storytelling',
            'creative', 'creativity', 'content', 'copy', 'copywriting',
            'article', 'blog', 'essay', 'poem', 'poetry', 'novel',
            'script', 'screenplay', 'dialogue', 'character', 'plot',
            'narrative', 'prose', 'fiction', 'non-fiction', 'draft',
            'revision', 'grammar', 'style', 'tone', 'voice', 'audience'
        ]
        
        query_lower = query.lower()
        context_text = str(context).lower()
        combined_text = f"{query_lower} {context_text}"
        
        matches = sum(1 for keyword in writing_keywords if keyword in combined_text)
        confidence = min(matches / 4, 1.0)
        
        # Boost for writing-specific patterns
        if re.search(r'how to write|help me write|improve.*(writing|text)', query_lower):
            confidence += 0.3
        
        return min(confidence, 0.95)
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process writing query"""
        confidence = self.can_handle(query, context)
        
        if confidence < self.confidence_threshold:
            return self._format_response(
                "This doesn't appear to be a writing question I can help with.",
                confidence,
                "Query doesn't match writing expertise areas"
            )
        
        response = f"""Looking at your writing request:

{query}

Here's my writing guidance and approach:

**Writing Strategy:**
1. **Purpose & Audience**: Define your goals and target readers
2. **Structure & Organization**: Logical flow and clear progression
3. **Voice & Tone**: Appropriate style for your content type
4. **Clarity & Engagement**: Clear communication that holds attention
5. **Revision & Polish**: Iterative improvement and refinement

**Key Writing Principles:**
- Start with a strong hook or opening
- Use clear, concise language appropriate for your audience
- Show don't tell (especially for creative writing)
- Maintain consistent voice and tone throughout
- Edit ruthlessly - every word should serve a purpose

**Next Steps:**
- Would you like help with a specific type of writing (creative, technical, marketing, etc.)?
- Do you have a draft that needs feedback and improvement?
- Are you looking for brainstorming and ideation support?

I can provide detailed guidance on structure, style, technique, and revision strategies."""
        
        return self._format_response(
            response,
            confidence,
            f"High confidence based on writing keyword matches and content patterns"
        )
