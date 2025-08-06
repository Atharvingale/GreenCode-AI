from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import gc
import psutil

# Memory monitoring
def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    if memory_info.rss > 400 * 1024 * 1024:  # 400MB threshold (reduced from 450)
        gc.collect()
        return True
    return False

# Lazy import heavy dependencies
def lazy_import(module_name, attr_name=None):
    """Lazy import to reduce memory at startup"""
    def _import():
        module = __import__(module_name, fromlist=[attr_name] if attr_name else [])
        return getattr(module, attr_name) if attr_name else module
    return _import

# Initialize FastAPI with minimal config
app = FastAPI(
    title="VeriSure AI",
    description="Policy Explainer AI - memory-optimized insurance assistant",
    version="1.0",
    docs_url=None,  # Disable docs to save memory
    redoc_url=None  # Disable redoc to save memory
)

# Startup health check
@app.on_event("startup")
async def startup_event():
    print("VeriSure AI backend starting...")
    check_memory_usage()

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
    session_id : str

@app.get("/")
def root():
    return {"message": "VeriSure AI is live!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/query")
def query_docs(request: QueryRequest):
    session_id = request.session_id
    try:
        # Lazy import dependencies
        retrieve_chunks = lazy_import('app.core.retriever', 'retrieve_chunks')()
        evaluate_decision = lazy_import('app.core.engine', 'evaluate_decision')()
        
        # Aggressive memory limits
        query = request.query[:500]  # Reduce from 1000 to 500 characters
        
        # Get relevant chunks with minimal memory
        relevant_chunks = retrieve_chunks(query, session_id, k=2)  # Reduce from 3 to 2 chunks
        
        # Process answer
        answer = evaluate_decision(query, session_id)
        
        # Compact response
        response = {
            "query": query[:100],  # Truncate in response
            "response": answer,
            "retrieved_clauses": [c[:200] for c in relevant_chunks[:2]]  # Severe truncation
        }
        
        # Aggressive cleanup
        del relevant_chunks, answer, query
        for _ in range(3):  # Multiple gc passes
            gc.collect()
        
        return response
        
    except Exception as e:
        return {"error": str(e)[:100]}  # Truncate error messages
    finally:
        gc.collect()



@app.post("/upload_docs")
async def upload_docs(uploaded_files: List[UploadFile] = File(...)):
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_dir = f"session_{session_id}"
    batch_size = 100  # Ultra-small batch size
    max_files = 3   # Limit to 3 files max
    max_file_size = 1024 * 1024  # 1MB max per file
    
    # Limit file count
    uploaded_files = uploaded_files[:max_files]
    
    try:
        # Lazy import dependencies
        load_content = lazy_import('app.core.retriever', 'load_content')()
        chunk_text = lazy_import('app.core.retriever', 'chunk_text')()
        build_index = lazy_import('app.core.retriever', 'build_index')()
        
        # Create session directory
        temp_dir = f"temp_uploads/{index_dir}"
        os.makedirs(temp_dir, exist_ok=True)
        
        responses = []
        current_batch = []
        total_chunks = 0
        
        for uploaded_file in uploaded_files:
            try:
                # Check file size
                if uploaded_file.size > max_file_size:
                    raise ValueError(f"File too large: {uploaded_file.size} > {max_file_size}")
                
                # Process file in ultra-small chunks
                chunk_size = 2048  # 2KB chunks
                file_path = f"{temp_dir}/{uploaded_file.filename}"
                
                # Stream file content
                content = await uploaded_file.read()
                if len(content) > max_file_size:
                    content = content[:max_file_size]
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Process text with severe limits
                raw_text = load_content(file_path)
                raw_text = raw_text[:10 * 1024]  # 10KB max text
                
                for text_batch in chunk_text(raw_text):
                    # Limit chunks per batch
                    chunks = text_batch[:50]  # Max 50 chunks per batch
                    current_batch.extend(chunks)
                    total_chunks += len(chunks)
                    
                    if len(current_batch) >= batch_size:
                        build_index(current_batch[:batch_size], session_id, force_rebuild=False)
                        current_batch = current_batch[batch_size:]
                        check_memory_usage()
                        
                        # Hard limit on total chunks
                        if total_chunks > 1000:
                            break
                
                if total_chunks > 1000:
                    break
                
                responses.append({
                    "filename": uploaded_file.filename,
                    "status": "processed",
                    "chunks": len(current_batch),
                    "session_id": session_id
                })
                
            except Exception as e:
                responses.append({
                    "filename": uploaded_file.filename,
                    "status": "failed",
                    "error": str(e)[:50]  # Truncate error
                })
            finally:
                # Clean up immediately
                if os.path.exists(file_path):
                    os.remove(file_path)
                gc.collect()
        
        # Process final batch
        if current_batch:
            build_index(current_batch[:batch_size], session_id, force_rebuild=False)
        
        # Ultra cleanup
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        for _ in range(3):
            gc.collect()
        
        return {
            "status": "success",
            "indexed_files": responses,
            "session_id": session_id,
            "total_chunks": total_chunks,
            "message": "Documents processed with ultra-memory optimization."
        }

    except Exception as e:
        return {"error": str(e)}

