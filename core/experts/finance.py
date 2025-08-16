"""Finance expert for financial analysis and advice"""
from typing import Dict, Any
from .base import BaseExpert, ExpertResponse
import re

class FinanceExpert(BaseExpert):
    """Expert in finance, investment, and economic analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="finance",
            specialties=["finance", "investment", "economics", "trading", "banking", "portfolio", "valuation"],
            config=config
        )
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> float:
        """Determine if this is a finance-related query"""
        finance_keywords = [
            'investment', 'portfolio', 'stock', 'bond', 'trading', 'market',
            'finance', 'financial', 'money', 'economics', 'economic', 'bank',
            'banking', 'credit', 'loan', 'mortgage', 'insurance', 'tax',
            'valuation', 'dcf', 'roi', 'irr', 'npv', 'revenue', 'profit',
            'cash flow', 'balance sheet', 'income statement', 'financial statement'
        ]
        
        query_lower = query.lower()
        context_text = str(context).lower()
        combined_text = f"{query_lower} {context_text}"
        
        matches = sum(1 for keyword in finance_keywords if keyword in combined_text)
        confidence = min(matches / 5, 1.0)  # Scale to 0-1
        
        # Boost confidence for specific financial patterns
        if re.search(r'\$[0-9,]+', query) or re.search(r'[0-9]+%', query):
            confidence += 0.2
        
        return min(confidence, 0.95)
    
    def process(self, query: str, context: Dict[str, Any]) -> ExpertResponse:
        """Process financial query"""
        confidence = self.can_handle(query, context)
        
        if confidence < self.confidence_threshold:
            return self._format_response(
                "I don't have sufficient confidence to provide financial advice on this topic.",
                confidence,
                "Query doesn't match my financial expertise areas"
            )
        
        # Financial analysis prompt
        system_prompt = f"""
You are a financial expert with deep knowledge of:
- Investment analysis and portfolio management
- Financial markets and trading strategies  
- Corporate finance and valuation
- Economic analysis and forecasting
- Risk management and financial planning

Provide accurate, professional financial analysis. Always include:
1. Key financial concepts and metrics
2. Risk considerations and disclaimers
3. Relevant market context
4. Actionable insights when appropriate

IMPORTANT: Always include appropriate disclaimers about financial advice.
"""
        
        # This would integrate with the actual LLM provider
        response = f"""Based on my financial analysis:

{query}

I would recommend considering the following financial factors:
1. Risk assessment and risk tolerance
2. Diversification strategies
3. Time horizon and liquidity needs
4. Market conditions and economic indicators
5. Tax implications and regulatory considerations

DISCLAIMER: This is educational information only and not personalized financial advice. Consult with a qualified financial advisor for specific recommendations."""
        
        return self._format_response(
            response,
            confidence,
            f"High confidence based on financial keyword matches and domain expertise"
        )
