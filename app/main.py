from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.retriever import retrieve_chunks, build_index
from app.core.engine import evaluate_decision
from app.ingestion.load import load_content
from app.ingestion.chunk import chunk_text
from typing import List
from datetime import datetime
import os
import gc
import psutil

# Memory monitoring
def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    if memory_info.rss > 450 * 1024 * 1024:  # 450MB threshold
        gc.collect()
        return True
    return False

app = FastAPI(
    title="VeriSure AI",
    description="Policy Explainer AI is an intelligent, session-based insurance assistant that combines semantic document retrieval using FAISS with reasoning powered by Gemini 1.5 Flash. Users can upload multiple policy documents, ask natural language questions, and receive structured, justified decisions in real time. Each session is self-contained, allowing dynamic indexing, accurate clause referencing, and clean separation of uploaded contexts.",
    version="1.0"
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
    session_id : str

@app.get("/")
def root():
    return {"message": "VeriSure AI is live!"}

@app.post("/query")
def query_docs(request: QueryRequest):
    session_id = request.session_id
    try:
        # Limit query length
        query = request.query[:1000]  # Limit to 1000 characters
        
        # Get relevant chunks with memory-efficient retrieval
        relevant_chunks = retrieve_chunks(query, session_id, k=3)  # Reduced from 5 to 3 chunks
        
        # Process answer with memory cleanup
        answer = evaluate_decision(query, session_id)
        
        # Clear any large variables
        response = {
            "query": query,
            "response": answer,
            "retrieved_clauses": relevant_chunks[:3]  # Limit number of returned clauses
        }
        
        # Clear variables to free memory
        del relevant_chunks
        del answer
        gc.collect()
        
        return response
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Ensure memory cleanup
        gc.collect()



@app.post("/upload_docs")
async def upload_docs(uploaded_files: List[UploadFile] = File(...)):
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_dir = f"session_{session_id}"
    batch_size = 500  # Reduced batch size for better memory management
    
    try:
        # Create session directory
        temp_dir = f"temp_uploads/{index_dir}"
        os.makedirs(temp_dir, exist_ok=True)
        
        responses = []
        current_batch = []
        
        for uploaded_file in uploaded_files:
            try:
                # Process file in smaller chunks
                chunk_size = 4096  # 4KB chunks for file reading
                file_path = f"{temp_dir}/{uploaded_file.filename}"
                
                # Stream file content
                with open(file_path, "wb") as f:
                    while chunk := await uploaded_file.read(chunk_size):
                        f.write(chunk)
                        await uploaded_file.seek(uploaded_file.tell())  # Update position
                
                # Process text in smaller segments
                raw_text = load_content(file_path)
                for text_batch in chunk_text(raw_text):
                    current_batch.extend(text_batch)
                    
                    if len(current_batch) >= batch_size:
                        build_index(current_batch[:batch_size], session_id, force_rebuild=False)
                        current_batch = current_batch[batch_size:]
                        check_memory_usage()
                
                responses.append({
                    "filename": uploaded_file.filename,
                    "status": "processed",
                    "session_id": session_id
                })
                
            except Exception as e:
                responses.append({
                    "filename": uploaded_file.filename,
                    "status": "failed",
                    "error": str(e)
                })
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                gc.collect()
        
        # Process any remaining chunks
        if current_batch:
            build_index(current_batch, session_id, force_rebuild=False)
        
        # Clean up
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        gc.collect()
        return {
            "status": "success",
            "indexed_files": responses,
            "session_id": session_id,
            "message": "All documents processed and indexed successfully."
        }

    except Exception as e:
        return {"error": str(e)}

