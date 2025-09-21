"""
Legal Document Templates and Specialized Prompts
Tailored analysis prompts for different legal document types
"""

from typing import Dict, List
from enum import Enum

class DocumentType(Enum):
    RENTAL_AGREEMENT = "rental_agreement"
    LOAN_CONTRACT = "loan_contract"
    TERMS_OF_SERVICE = "terms_of_service"
    EMPLOYMENT_CONTRACT = "employment_contract"
    INSURANCE_POLICY = "insurance_policy"
    SERVICE_AGREEMENT = "service_agreement"
    GENERAL_LEGAL_DOCUMENT = "general_legal_document"

# Document-specific translation prompts
DOCUMENT_TRANSLATION_PROMPTS = {
    DocumentType.RENTAL_AGREEMENT: """
You are a rental agreement translator. Focus on tenant rights and obligations.

Key areas to pay special attention to:
- Rent payment terms and late fees
- Security deposit conditions
- Maintenance responsibilities  
- Lease termination and renewal
- Restrictions and rules
- Landlord entry rights

Translate these rental agreement clauses into plain English that a tenant can easily understand:
{clauses}

Return JSON with translations that emphasize what tenants need to know.
""",

    DocumentType.LOAN_CONTRACT: """
You are a loan contract translator. Focus on borrower obligations and costs.

Key areas to emphasize:
- Interest rates and APR
- Payment schedule and amounts
- Fees and penalties
- Default consequences
- Prepayment terms
- Collateral requirements

Translate these loan contract clauses into simple terms a borrower can understand:
{clauses}

Return JSON focusing on total costs and borrower risks.
""",

    DocumentType.TERMS_OF_SERVICE: """
You are a terms of service translator. Focus on user rights and platform powers.

Key areas to highlight:
- Data collection and usage
- Account termination policies
- Content ownership
- Liability limitations
- Privacy implications
- Service changes

Translate these terms of service clauses into language everyday users can understand:
{clauses}

Return JSON emphasizing what users are agreeing to give up or accept.
""",

    DocumentType.EMPLOYMENT_CONTRACT: """
You are an employment contract translator. Focus on employee rights and employer powers.

Key areas to emphasize:
- Compensation and benefits
- Termination conditions
- Non-compete and confidentiality
- Work responsibilities
- Disciplinary procedures
- Intellectual property rights

Translate these employment contract clauses for an employee to understand:
{clauses}

Return JSON focusing on employee obligations and protections.
"""
}

# Document-specific risk analysis prompts
DOCUMENT_RISK_PROMPTS = {
    DocumentType.RENTAL_AGREEMENT: """
You are analyzing a rental agreement for tenant risks.

Common rental agreement traps to look for:
- Automatic lease renewal without proper notice
- Excessive or non-refundable fees
- Unfair security deposit terms
- Broad landlord entry rights
- Tenant liability for normal wear and tear
- Restrictions on reasonable use
- Unfair termination clauses
- Hidden maintenance costs

Analyze these rental agreement clauses and identify risks to the tenant:
{clauses}

Focus on clauses that could cost the tenant money or limit their rights unfairly.
""",

    DocumentType.LOAN_CONTRACT: """
You are analyzing a loan contract for borrower risks.

Common loan contract traps to look for:
- Variable interest rates that can increase
- Hidden fees and charges
- Prepayment penalties
- Harsh default consequences
- Personal guarantees or collateral requirements
- Automatic payment authorizations
- Balloon payments
- Credit insurance add-ons

Analyze these loan contract clauses and identify risks to the borrower:
{clauses}

Focus on clauses that could increase costs or create unexpected obligations.
""",

    DocumentType.TERMS_OF_SERVICE: """
You are analyzing terms of service for user risks.

Common ToS traps to look for:
- Broad data collection and sharing
- Unilateral changes to terms
- Account termination without cause
- Liability waivers and indemnification
- Forced arbitration clauses
- Content ownership transfers
- Automatic subscription renewals
- Privacy policy cross-references

Analyze these terms of service clauses and identify risks to users:
{clauses}

Focus on clauses that limit user rights or expand platform powers.
"""
}

# Document-specific Q&A prompts
DOCUMENT_QA_PROMPTS = {
    DocumentType.RENTAL_AGREEMENT: """
You are a rental agreement expert answering tenant questions.

When answering, consider typical tenant concerns:
- Monthly rent and additional costs
- Security deposit return conditions
- Maintenance and repair responsibilities
- Lease breaking and early termination
- Guest and pet policies
- Rent increases and lease renewals

User Question: {query}
Relevant Rental Agreement Clauses: {clauses}

Provide practical advice focusing on tenant rights and obligations.
""",

    DocumentType.LOAN_CONTRACT: """
You are a loan contract expert answering borrower questions.

When answering, consider typical borrower concerns:
- Total loan cost and monthly payments
- Interest rate changes and caps
- Early payment options and penalties
- Default consequences and remedies
- Required insurance or collateral
- Fees and additional charges

User Question: {query}
Relevant Loan Contract Clauses: {clauses}

Provide clear answers focusing on borrower costs and obligations.
""",

    DocumentType.EMPLOYMENT_CONTRACT: """
You are an employment contract expert answering employee questions.

When answering, consider typical employee concerns:
- Compensation, benefits, and raises
- Job responsibilities and expectations
- Termination conditions and severance
- Non-compete and confidentiality rules
- Intellectual property ownership
- Work schedule and location flexibility

User Question: {query}
Relevant Employment Contract Clauses: {clauses}

Provide practical guidance focusing on employee rights and obligations.
"""
}

# Common legal phrases and their translations
LEGAL_JARGON_DICTIONARY = {
    "indemnify": "pay for damages or legal costs on behalf of someone else",
    "hold harmless": "not blame or make someone pay for damages",
    "liquidated damages": "a pre-set amount you must pay if you break the contract",
    "force majeure": "unforeseeable circumstances that prevent fulfilling the contract",
    "non-disclosure agreement": "promise not to share confidential information",
    "severability": "if one part of the contract is invalid, the rest still applies",
    "governing law": "which state's or country's laws apply to this contract",
    "jurisdiction": "which courts can handle disputes about this contract",
    "binding arbitration": "required to resolve disputes through arbitration, not court",
    "class action waiver": "give up the right to join group lawsuits",
    "warranty disclaimer": "we don't guarantee this will work perfectly",
    "as-is": "you buy this with all its problems, we won't fix anything",
    "time is of the essence": "deadlines are extremely important and strict",
    "entire agreement": "this document contains all the terms, nothing else counts",
    "modification": "changes to this contract must be in writing",
    "assignment": "transferring your rights or obligations to someone else",
    "successor": "person or company that takes over rights and responsibilities",
    "cure period": "time allowed to fix a problem before facing consequences",
    "material breach": "breaking the contract in a significant way",
    "reasonable notice": "fair warning given in advance"
}

def get_document_specific_prompt(document_type: DocumentType, prompt_type: str, **kwargs) -> str:
    """Get a specialized prompt for a specific document type and analysis type."""
    
    if prompt_type == "translation":
        return DOCUMENT_TRANSLATION_PROMPTS.get(document_type, 
                                                DOCUMENT_TRANSLATION_PROMPTS[DocumentType.GENERAL_LEGAL_DOCUMENT]
                                                ).format(**kwargs)
    
    elif prompt_type == "risk":
        return DOCUMENT_RISK_PROMPTS.get(document_type,
                                        "Analyze these legal document clauses for potential risks to the individual: {clauses}"
                                        ).format(**kwargs)
    
    elif prompt_type == "qa":
        return DOCUMENT_QA_PROMPTS.get(document_type,
                                      "Answer this question about the legal document: {query}\nRelevant clauses: {clauses}"
                                      ).format(**kwargs)
    
    return ""

def translate_legal_phrase(phrase: str) -> str:
    """Translate a common legal phrase to plain English."""
    phrase_lower = phrase.lower().strip()
    
    for legal_term, plain_english in LEGAL_JARGON_DICTIONARY.items():
        if legal_term in phrase_lower:
            return phrase_lower.replace(legal_term, f"**{plain_english}**")
    
    return phrase

def get_document_specific_risks(document_type: DocumentType) -> List[str]:
    """Get a list of common risks for a specific document type."""
    
    risk_categories = {
        DocumentType.RENTAL_AGREEMENT: [
            "automatic_renewal", "hidden_fees", "deposit_risk", "unfair_termination",
            "liability_shift", "penalty_fees", "unilateral_changes"
        ],
        DocumentType.LOAN_CONTRACT: [
            "variable_interest", "hidden_fees", "penalty_fees", "liability_shift",
            "automatic_renewal", "unfair_termination"
        ],
        DocumentType.TERMS_OF_SERVICE: [
            "privacy_risk", "unilateral_changes", "dispute_resolution_limitation",
            "liability_shift", "automatic_renewal", "unfair_termination"
        ],
        DocumentType.EMPLOYMENT_CONTRACT: [
            "unfair_termination", "liability_shift", "penalty_fees",
            "dispute_resolution_limitation", "unilateral_changes"
        ],
        DocumentType.INSURANCE_POLICY: [
            "automatic_renewal", "hidden_fees", "liability_shift", "unfair_termination"
        ]
    }
    
    return risk_categories.get(document_type, [
        "automatic_renewal", "hidden_fees", "liability_shift", "unfair_termination"
    ])

# Example clauses for testing (anonymized)
SAMPLE_CLAUSES = {
    DocumentType.RENTAL_AGREEMENT: [
        "This lease shall automatically renew for successive one-year terms unless either party gives sixty (60) days written notice of intent not to renew.",
        "Tenant shall indemnify and hold harmless Landlord from any claims arising from Tenant's use of the premises.",
        "Late fees of $50 plus $5 per day shall be assessed for rent payments received more than three (3) days after the due date."
    ],
    DocumentType.LOAN_CONTRACT: [
        "The interest rate is variable and may be adjusted quarterly based on the Prime Rate plus 3.25%.",
        "Borrower agrees to pay a prepayment penalty equal to 2% of the outstanding balance if paid in full within the first two years.",
        "In the event of default, the entire unpaid balance shall become immediately due and payable."
    ]
}

def get_sample_clauses(document_type: DocumentType) -> List[str]:
    """Get sample clauses for testing document analysis."""
    return SAMPLE_CLAUSES.get(document_type, [
        "This is a sample legal clause that contains standard legal language and terms.",
        "The parties agree to binding arbitration for any disputes arising under this agreement."
    ])