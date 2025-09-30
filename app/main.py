from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.retriever import retrieve_chunks, build_index
from app.core.engine import evaluate_decision, comprehensive_legal_analysis, generate_smart_questions
from app.core.risk_analyzer import analyze_document_risks_advanced
from app.ingestion.load import load_content
from app.ingestion.chunk import chunk_text
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(
    title="SafeSign - Digital Document Security Platform",
    description="SafeSign is an intelligent digital document analysis platform that provides secure document signing and analysis capabilities. It offers comprehensive document review, risk assessment, and AI-powered insights to ensure safe and informed document signing. Powered by advanced AI and semantic search.",
    version="2.0"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    session_id: str
    analysis_type: Optional[str] = "qa"  # qa, translate, risk, comprehensive

class DocumentAnalysisRequest(BaseModel):
    session_id: str
    document_type: Optional[str] = "general_legal_document"

@app.get("/")
def root():
    return {
        "message": "SafeSign - Digital Document Security Platform is live!",
        "features": {
            "translation": "Convert legal jargon to plain English",
            "risk_analysis": "Identify unfavorable clauses and hidden traps",
            "qa_system": "Ask questions about your legal documents",
            "comprehensive": "Get all three layers of analysis at once"
        },
        "supported_documents": [
            "Rental Agreements", "Loan Contracts", "Terms of Service",
            "Employment Contracts", "Insurance Policies", "Service Agreements"
        ]
    }

@app.post("/query")
def query_docs(request: QueryRequest):
    """Answer questions about legal documents with optional analysis type."""
    try:
        if request.analysis_type == "comprehensive":
            result = comprehensive_legal_analysis(request.query, request.session_id, "comprehensive")
        else:
            result = comprehensive_legal_analysis(request.query, request.session_id, request.analysis_type)
        
        print(f"Query received: {request.query}")
        print(f"Analysis type: {request.analysis_type}")
        print(f"Result: {result}")
        
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_risks")
def analyze_document_risks(request: DocumentAnalysisRequest):
    """Perform comprehensive risk analysis on uploaded documents."""
    try:
        # Retrieve all chunks from the session for risk analysis
        all_chunks = retrieve_chunks("", request.session_id, k=50)  # Get more chunks for comprehensive analysis
        
        if not all_chunks:
            return {"error": "No document content found for analysis. Please upload a document first."}
        
        # Perform advanced risk analysis
        risk_analysis = analyze_document_risks_advanced(all_chunks, request.document_type)
        
        return {
            "session_id": request.session_id,
            "document_type": request.document_type,
            "analysis": risk_analysis,
            "chunks_analyzed": len(all_chunks)
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate_questions")
def generate_questions_endpoint(request: DocumentAnalysisRequest):
    """Generate AI-powered questions based on the actual document content."""
    try:
        result = generate_smart_questions(request.session_id, max_questions=8)
        
        return {
            "session_id": request.session_id,
            "questions": result.get("questions", []),
            "document_type": result.get("document_type", "unknown"),
            "document_summary": result.get("document_summary", ""),
            "error": result.get("error")
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload_docs")
async def upload_docs(uploaded_files: List[UploadFile] = File(...)):
    responses = []
    alltext_chunks = []
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_dir = f"session_{session_id}"

    try:
        for uploaded_file in uploaded_files:
            contents = await uploaded_file.read()
            file_path = f"temp_uploads/{index_dir}/{uploaded_file.filename}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(contents)

            raw_text = load_content(file_path)
            text_chunks = chunk_text(raw_text)
            alltext_chunks.extend(text_chunks)

            responses.append({
                "filename": uploaded_file.filename,
                "status": "Legal document processed and indexed for analysis",
                "session_id": session_id
            })

        build_index(alltext_chunks, session_id, force_rebuild=True)

        return {
            "status": "success",
            "indexed_files": responses,
            "session_id": session_id,
            "message": "Legal documents successfully processed and ready for analysis. You can now ask questions, get translations, or perform risk analysis."
        }

    except Exception as e:
        return {"error": str(e)}

