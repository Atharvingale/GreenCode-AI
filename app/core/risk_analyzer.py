import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskPattern:
    pattern: str
    risk_type: str
    risk_level: RiskLevel
    warning: str
    suggestion: str
    document_types: List[str]

class LegalRiskAnalyzer:
    """Advanced risk analyzer for legal documents with predefined risk patterns."""
    
    def __init__(self):
        self.risk_patterns = self._initialize_risk_patterns()
    
    def _initialize_risk_patterns(self) -> List[RiskPattern]:
        """Define common risky patterns in legal documents."""
        return [
            # Automatic Renewal Patterns
            RiskPattern(
                pattern=r"(automatic[ly]*\s*(renew|extend|continue)|renew[s]*\s*automatic[ly]*|unless\s*you\s*cancel)",
                risk_type="automatic_renewal",
                risk_level=RiskLevel.HIGH,
                warning="This contract will renew itself automatically unless you take action to cancel it.",
                suggestion="Mark your calendar to cancel before the renewal date if you don't want to continue.",
                document_types=["rental_agreement", "subscription", "insurance_policy", "terms_of_service"]
            ),
            
            # Hidden Fee Patterns
            RiskPattern(
                pattern=r"(additional\s*fees|service\s*charges|administrative\s*fees|processing\s*fees|convenience\s*fees)",
                risk_type="hidden_fees",
                risk_level=RiskLevel.MEDIUM,
                warning="There may be extra fees beyond the main price that could increase your total cost.",
                suggestion="Ask for a complete breakdown of all possible fees before signing.",
                document_types=["loan_contract", "rental_agreement", "service_agreement"]
            ),
            
            # Liability Shift Patterns
            RiskPattern(
                pattern=r"(you\s*(agree\s*to\s*)?(indemnify|hold\s*harmless|defend)|liability\s*is\s*limited\s*to|not\s*liable\s*for)",
                risk_type="liability_shift",
                risk_level=RiskLevel.HIGH,
                warning="You may be responsible for paying for damages or legal costs, even if they're not your fault.",
                suggestion="Consider if you need additional insurance or legal protection.",
                document_types=["rental_agreement", "service_agreement", "terms_of_service"]
            ),
            
            # Unfair Termination Patterns
            RiskPattern(
                pattern=r"(terminate\s*at\s*any\s*time|without\s*cause|without\s*notice|immediate\s*termination)",
                risk_type="unfair_termination",
                risk_level=RiskLevel.HIGH,
                warning="The other party can end this agreement suddenly without giving you much warning or reason.",
                suggestion="Negotiate for reasonable notice period or termination protections.",
                document_types=["employment_contract", "rental_agreement", "service_agreement"]
            ),
            
            # Penalty Clauses
            RiskPattern(
                pattern=r"(penalty|fine|late\s*fee|breach\s*fee|early\s*termination\s*fee)",
                risk_type="penalty_fees",
                risk_level=RiskLevel.MEDIUM,
                warning="You could face financial penalties for various actions or situations.",
                suggestion="Understand exactly when penalties apply and how much they cost.",
                document_types=["loan_contract", "rental_agreement", "employment_contract"]
            ),
            
            # Arbitration Clauses
            RiskPattern(
                pattern=r"(arbitration|binding\s*arbitration|waive\s*right\s*to\s*jury|class\s*action\s*waiver)",
                risk_type="dispute_resolution_limitation",
                risk_level=RiskLevel.HIGH,
                warning="You're giving up your right to sue in court or join group lawsuits.",
                suggestion="Understand that you'll have to resolve disputes through arbitration, which may limit your options.",
                document_types=["terms_of_service", "employment_contract", "service_agreement"]
            ),
            
            # Data and Privacy Risks
            RiskPattern(
                pattern=r"(collect\s*personal\s*information|share\s*with\s*third\s*parties|sell\s*your\s*data|marketing\s*purposes)",
                risk_type="privacy_risk",
                risk_level=RiskLevel.MEDIUM,
                warning="Your personal information may be collected, shared, or used in ways you might not expect.",
                suggestion="Review privacy settings and opt-out options if available.",
                document_types=["terms_of_service", "privacy_policy", "service_agreement"]
            ),
            
            # Interest Rate and APR Risks
            RiskPattern(
                pattern=r"(variable\s*rate|adjustable\s*rate|rate\s*may\s*increase|subject\s*to\s*change)",
                risk_type="variable_interest",
                risk_level=RiskLevel.HIGH,
                warning="Interest rates can go up, making your payments more expensive over time.",
                suggestion="Ask about rate caps and consider if you can afford higher payments.",
                document_types=["loan_contract", "credit_agreement", "mortgage"]
            ),
            
            # Security Deposit Issues
            RiskPattern(
                pattern=r"(non-refundable|deposit\s*may\s*not\s*be\s*returned|normal\s*wear\s*and\s*tear)",
                risk_type="deposit_risk",
                risk_level=RiskLevel.MEDIUM,
                warning="You might not get your full deposit back, even if you take good care of the property.",
                suggestion="Document the condition of the property when you move in and out.",
                document_types=["rental_agreement", "lease_agreement"]
            ),
            
            # Modification Clauses
            RiskPattern(
                pattern=r"(reserve\s*the\s*right\s*to\s*modify|terms\s*may\s*change|unilateral|at\s*our\s*discretion)",
                risk_type="unilateral_changes",
                risk_level=RiskLevel.HIGH,
                warning="The other party can change the terms of this agreement without your consent.",
                suggestion="Look for limitations on changes and your right to cancel if terms change significantly.",
                document_types=["terms_of_service", "service_agreement", "subscription"]
            )
        ]
    
    def analyze_text_risks(self, text: str, document_type: str = "general_legal_document") -> List[Dict[str, Any]]:
        """Analyze text for risk patterns and return detailed risk assessment."""
        risks = []
        text_lower = text.lower()
        
        for pattern in self.risk_patterns:
            # Check if this pattern applies to the document type
            if document_type not in pattern.document_types and "general_legal_document" not in pattern.document_types:
                continue
            
            matches = re.finditer(pattern.pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Find the sentence containing the match
                sentence = self._extract_sentence(text, match.start(), match.end())
                
                risk_item = {
                    "clause": sentence,
                    "risk_level": pattern.risk_level.value,
                    "risk_type": pattern.risk_type,
                    "warning": pattern.warning,
                    "suggestion": pattern.suggestion,
                    "matched_text": match.group(),
                    "document_type": document_type
                }
                risks.append(risk_item)
        
        # Remove duplicates and sort by risk level
        unique_risks = self._deduplicate_risks(risks)
        return sorted(unique_risks, key=lambda x: self._risk_sort_key(x["risk_level"]))
    
    def _extract_sentence(self, text: str, start: int, end: int) -> str:
        """Extract the sentence containing the matched pattern."""
        # Find sentence boundaries
        sentence_start = max(0, text.rfind('.', 0, start) + 1)
        sentence_end = text.find('.', end)
        if sentence_end == -1:
            sentence_end = len(text)
        
        sentence = text[sentence_start:sentence_end].strip()
        return sentence if sentence else text[max(0, start-50):end+50]
    
    def _deduplicate_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate risks based on risk type and similar clauses."""
        seen_combinations = set()
        unique_risks = []
        
        for risk in risks:
            combination = (risk["risk_type"], risk["clause"][:100])  # First 100 chars
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                unique_risks.append(risk)
        
        return unique_risks
    
    def _risk_sort_key(self, risk_level: str) -> int:
        """Return sort key for risk levels."""
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return order.get(risk_level, 4)
    
    def get_risk_summary(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of all identified risks."""
        if not risks:
            return {
                "total_risks": 0,
                "risk_distribution": {},
                "highest_risk": "none",
                "recommendations": ["This document appears to have standard terms with no major red flags."]
            }
        
        risk_counts = {}
        risk_types = set()
        
        for risk in risks:
            level = risk["risk_level"]
            risk_counts[level] = risk_counts.get(level, 0) + 1
            risk_types.add(risk["risk_type"])
        
        highest_risk = min(risks, key=lambda x: self._risk_sort_key(x["risk_level"]))["risk_level"]
        
        recommendations = self._generate_recommendations(risks, risk_types)
        
        return {
            "total_risks": len(risks),
            "risk_distribution": risk_counts,
            "highest_risk": highest_risk,
            "risk_types_found": list(risk_types),
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self, risks: List[Dict[str, Any]], risk_types: set) -> List[str]:
        """Generate actionable recommendations based on identified risks."""
        recommendations = []
        
        if "automatic_renewal" in risk_types:
            recommendations.append("Set calendar reminders for cancellation dates to avoid unwanted renewals.")
        
        if "liability_shift" in risk_types:
            recommendations.append("Consider purchasing additional insurance coverage to protect yourself.")
        
        if "arbitration" in risk_types or "dispute_resolution_limitation" in risk_types:
            recommendations.append("Understand that you're giving up certain legal rights. Consult a lawyer if concerned.")
        
        if "variable_interest" in risk_types:
            recommendations.append("Budget for potential rate increases and understand the maximum possible rate.")
        
        if "hidden_fees" in risk_types or "penalty_fees" in risk_types:
            recommendations.append("Get a complete fee schedule in writing and budget for potential additional costs.")
        
        if len(risks) > 5:
            recommendations.append("This document has many potentially problematic clauses. Consider legal review before signing.")
        
        if not recommendations:
            recommendations.append("Review the highlighted clauses carefully and ask questions about anything unclear.")
        
        return recommendations

# Utility functions for the main engine
def analyze_document_risks_advanced(clauses: List[str], document_type: str) -> Dict[str, Any]:
    """Advanced risk analysis using pattern matching and AI."""
    analyzer = LegalRiskAnalyzer()
    all_risks = []
    
    # Analyze each clause
    for clause in clauses:
        risks = analyzer.analyze_text_risks(clause, document_type)
        all_risks.extend(risks)
    
    # Get summary
    risk_summary = analyzer.get_risk_summary(all_risks)
    
    return {
        "risk_analysis": all_risks,
        "summary": risk_summary,
        "document_type": document_type,
        "analysis_method": "pattern_matching + ai"
    }