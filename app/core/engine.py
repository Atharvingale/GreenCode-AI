from openai import OpenAI
import yaml
import json
from app.core.retriever import retrieve_chunks
from typing import Dict, List, Any

# Load API key from config file
with open("config/config.yaml") as f:
    cfg = yaml.safe_load(f)

# Configure OpenAI/OpenRouter client
api_key = cfg.get("openai_api_key", cfg.get("gemini_api_key"))

# Check if using OpenRouter
if api_key and "sk-or-v1" in api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    MODEL_NAME = "openai/gpt-4o-mini"
    print("Using OpenRouter with GPT-4o-mini")
else:
    client = OpenAI(api_key=api_key)
    MODEL_NAME = "gpt-3.5-turbo"
    print("Using OpenAI with GPT-3.5-turbo")

def generate_content(prompt: str) -> str:
    """Generate content using OpenAI or OpenRouter."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful legal document analysis assistant. Always respond with valid JSON as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Error: {str(e)}")
        return '{"error": "API connection failed"}'

# Legal Document Analysis Prompts
TRANSLATION_PROMPT = """
You are a legal document translator. Your job is to convert complex legal jargon into simple, fifth-grade reading level language.

For each clause provided, translate it into plain English that anyone can understand.

Clauses to translate:
{clauses}

Return a JSON response with:
{{
  "translations": [
    {{
      "original": "original clause text",
      "simplified": "plain English translation",
      "key_points": ["main takeaway 1", "main takeaway 2"]
    }}
  ]
}}

⚠️ Make the language accessible to everyday people. Avoid legal terms.
✅ Return only valid JSON.
"""

RISK_ANALYSIS_PROMPT = """
You are a legal risk analyzer. Your job is to identify clauses that may be unfavorable to the less powerful party (tenant, borrower, consumer, employee).

Analyze these clauses and flag potential risks:
{clauses}

Document Type: {document_type}

Return a JSON response with:
{{
  "risk_analysis": [
    {{
      "clause": "clause text",
      "risk_level": "high|medium|low",
      "risk_type": "automatic_renewal|hidden_fees|unfair_termination|liability_shift|etc",
      "warning": "plain English explanation of the risk",
      "suggestion": "what the user should do about this"
    }}
  ]
}}

⚠️ Focus on clauses that could harm the individual's interests.
✅ Return only valid JSON.
"""

QA_PROMPT = """
You are a legal document Q&A assistant. Answer the user's question based ONLY on the provided document clauses.

User Question: {query}

Relevant Clauses:
{clauses}

Provide a clear, direct answer in plain English. If the information isn't in the provided clauses, say so.

Return a JSON response with:
{{
  "answer": "direct answer to the question",
  "relevant_clauses": ["clause 1", "clause 2"],
  "confidence": "high|medium|low",
  "additional_notes": "any important context or warnings"
}}

⚠️ Only use information from the provided clauses.
✅ Return only valid JSON.
"""

def detect_document_type(text_chunks: List[str]) -> str:
    """Detect the type of legal document based on content."""
    combined_text = " ".join(text_chunks).lower()
    
    if any(term in combined_text for term in ["lease", "rent", "tenant", "landlord", "premises"]):
        return "rental_agreement"
    elif any(term in combined_text for term in ["loan", "borrower", "lender", "interest rate", "repayment"]):
        return "loan_contract"
    elif any(term in combined_text for term in ["terms of service", "user agreement", "privacy policy", "cookies"]):
        return "terms_of_service"
    elif any(term in combined_text for term in ["employment", "employee", "employer", "salary", "termination"]):
        return "employment_contract"
    elif any(term in combined_text for term in ["insurance", "policy", "coverage", "premium", "deductible"]):
        return "insurance_policy"
    else:
        return "general_legal_document"

def translate_legal_jargon(clauses: List[str]) -> Dict[str, Any]:
    """Translate legal clauses into plain English."""
    clauses_text = "\n\n".join(clauses)
    prompt = TRANSLATION_PROMPT.format(clauses=clauses_text)
    
    try:
        response_text = generate_content(prompt)
        
        # Clean up response text - remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response_text[:500],
            "translations": [{
                "original": "Analysis Error",
                "simplified": "The AI couldn't provide a proper translation. Please try again.",
                "key_points": ["Technical error occurred"]
            }]
        }
    except Exception as e:
        return {"error": f"Translation failed: {str(e)}"}

def analyze_document_risks(clauses: List[str], document_type: str) -> Dict[str, Any]:
    """Identify risky or unfavorable clauses."""
    clauses_text = "\n\n".join(clauses)
    prompt = RISK_ANALYSIS_PROMPT.format(clauses=clauses_text, document_type=document_type)
    
    try:
        response_text = generate_content(prompt)
        
        # Clean up response text - remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response_text[:500],
            "risk_analysis": [{
                "clause": "Analysis Error",
                "risk_level": "medium",
                "risk_type": "technical_error",
                "warning": "The AI couldn't analyze risks properly. Please try uploading the document again.",
                "suggestion": "Check your document format and try again, or contact support."
            }]
        }
    except Exception as e:
        return {"error": f"Risk analysis failed: {str(e)}"}

def answer_legal_question(query: str, session_id: str) -> Dict[str, Any]:
    """Answer specific questions about the legal document."""
    retrieved_chunks = retrieve_chunks(query, session_id)
    clauses = "\n\n".join(retrieved_chunks)
    prompt = QA_PROMPT.format(query=query, clauses=clauses)
    
    try:
        response_text = generate_content(prompt)
        
        # Clean up response text - remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response_text[:500],
            "answer": "I couldn't process your question properly. Please try rephrasing it or upload the document again.",
            "confidence": "low",
            "additional_notes": "Technical error occurred during analysis."
        }
    except Exception as e:
        return {"error": f"Q&A failed: {str(e)}"}

def comprehensive_legal_analysis(query: str, session_id: str, analysis_type: str = "qa") -> Dict[str, Any]:
    """Main function that orchestrates all three layers of analysis."""
    retrieved_chunks = retrieve_chunks(query, session_id)
    
    if not retrieved_chunks:
        return {"error": "No relevant clauses found for your query."}
    
    try:
        if analysis_type == "translate":
            # Translation Layer
            translation_result = translate_legal_jargon(retrieved_chunks)
            return {
                "analysis_type": "translation",
                "query": query,
                "result": translation_result,
                "retrieved_clauses": retrieved_chunks
            }
        
        elif analysis_type == "risk":
            # Risk Analysis Layer
            document_type = detect_document_type(retrieved_chunks)
            risk_result = analyze_document_risks(retrieved_chunks, document_type)
            return {
                "analysis_type": "risk_analysis",
                "query": query,
                "document_type": document_type,
                "result": risk_result,
                "retrieved_clauses": retrieved_chunks
            }
        
        elif analysis_type == "comprehensive":
            # All three layers
            document_type = detect_document_type(retrieved_chunks)
            translation_result = translate_legal_jargon(retrieved_chunks)
            risk_result = analyze_document_risks(retrieved_chunks, document_type)
            qa_result = answer_legal_question(query, session_id)
            
            return {
                "analysis_type": "comprehensive",
                "query": query,
                "document_type": document_type,
                "translation": translation_result,
                "risk_analysis": risk_result,
                "qa_response": qa_result,
                "retrieved_clauses": retrieved_chunks
            }
        
        else:
            # Default: Q&A Layer
            qa_result = answer_legal_question(query, session_id)
            return {
                "analysis_type": "qa",
                "query": query,
                "result": qa_result,
                "retrieved_clauses": retrieved_chunks
            }
            
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

QUESTION_GENERATION_PROMPT = """
You are a legal document analyst. Based on the document content provided, generate 8 insightful questions that someone should ask about this specific document.

Document Content:
{document_content}

Document Type: {document_type}

Generate questions that are:
1. Specific to this actual document
2. Important for the person signing/agreeing to understand
3. Focus on potential risks, obligations, and rights
4. Written in simple, everyday language

Return a JSON response with:
{{
  "questions": [
    "Question about specific aspect 1?",
    "Question about specific aspect 2?",
    "Question about specific aspect 3?",
    "Question about specific aspect 4?",
    "Question about specific aspect 5?",
    "Question about specific aspect 6?",
    "Question about specific aspect 7?",
    "Question about specific aspect 8?"
  ],
  "document_summary": "Brief 2-sentence summary of what this document is about"
}}

⚠️ Make questions specific to THIS document, not generic template questions.
✅ Return only valid JSON.
"""

def generate_smart_questions(session_id: str, max_questions: int = 8) -> Dict[str, Any]:
    """Generate AI-powered questions based on the actual document content."""
    try:
        # Get document chunks for analysis
        all_chunks = retrieve_chunks("", session_id, k=20)  # Get more chunks for comprehensive analysis
        
        if not all_chunks:
            return {
                "error": "No document content found",
                "questions": ["Please upload a document first to get personalized questions."]
            }
        
        # Combine chunks into document content (limit for API)
        document_content = "\n\n".join(all_chunks)[:4000]  # Limit to avoid token limits
        
        # Detect document type
        document_type = detect_document_type(all_chunks)
        
        # Generate AI questions
        prompt = QUESTION_GENERATION_PROMPT.format(
            document_content=document_content,
            document_type=document_type
        )
        
        response_text = generate_content(prompt)
        
        # Clean up response text
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        # Limit to requested number of questions
        if "questions" in result:
            result["questions"] = result["questions"][:max_questions]
            result["document_type"] = document_type
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse AI response",
            "questions": [
                "What are my main obligations under this agreement?",
                "What are the most important terms I should understand?",
                "What happens if I want to terminate this agreement?",
                "Are there any fees or penalties I should know about?"
            ],
            "document_type": "unknown"
        }
    except Exception as e:
        return {
            "error": f"Question generation failed: {str(e)}",
            "questions": ["Please try uploading your document again."],
            "document_type": "unknown"
        }

# Legacy function for backward compatibility
def evaluate_decision(query: str, session_id: str) -> Dict[str, Any]:
    """Legacy function - now redirects to comprehensive legal analysis."""
    return comprehensive_legal_analysis(query, session_id, "qa")
