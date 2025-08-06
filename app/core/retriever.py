import os
import numpy as np
import faiss
import pickle
import yaml
import gc
import psutil
from app.core.embedder import embed_texts
from datetime import datetime

# Memory monitoring
def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    if memory_info.rss > 450 * 1024 * 1024:  # 450MB threshold
        gc.collect()
        return True
    return False


# Load from config file or environment variables
try:
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
except:
    # Fallback to environment variables
    cfg = {
        "gemini_api_key": os.environ.get("gemini_api_key"),
        "openai_api_key": os.environ.get("openai_api_key"),
        "embedding_model": os.environ.get("embedding_model", "openai/gpt-3.5-turbo"),
        "chunk_size": int(os.environ.get("chunk_size", 512)),
        "max_chunks": int(os.environ.get("max_chunks", 20)),
        "session_timeout_minutes": int(os.environ.get("session_timeout_minutes", 60))
    }

def get_paths(session_id):
    base_dir = os.path.join("data", f"session_{session_id}", "backup")
    return {
        "INDEX_PATH": os.path.join(base_dir, "faiss.index"),
        "META_PATH": os.path.join(base_dir, "chunks.pkl")
    }


def normalize_embeddings(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

def build_index(text_chunks, session_id, force_rebuild=False, batch_size=100):
    paths = get_paths(session_id)
    INDEX_PATH = paths["INDEX_PATH"]
    META_PATH = paths["META_PATH"]
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH) and not force_rebuild:
        print("Index already exists.")
        return

    print("Building FAISS index...")
    
    try:
        # Process in batches to manage memory
        all_chunks = []
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            
            # Generate embeddings for batch
            vectors = embed_texts(batch)
            vectors = normalize_embeddings(np.array(vectors).astype("float32"))
            
            # Initialize or add to index
            if i == 0:
                dim = vectors.shape[1]
                index = faiss.IndexFlatIP(dim)
            
            index.add(vectors)
            all_chunks.extend(batch)
            
            # Clear batch memory
            del vectors
            del batch
            gc.collect()
            
            # Check memory usage
            if check_memory_usage():
                print("Memory threshold reached, performing cleanup")
        
        # Save index and metadata
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(all_chunks, f)
            
        print("FAISS index saved.")
        
    except Exception as e:
        print(f"Error building index: {str(e)}")
        raise
    finally:
        # Cleanup
        if 'index' in locals():
            del index
        if 'all_chunks' in locals():
            del all_chunks
        gc.collect()

def load_index(session_id):
    paths = get_paths(session_id)
    INDEX_PATH = paths["INDEX_PATH"]
    META_PATH = paths["META_PATH"]

    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("FAISS index not found.")
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def retrieve_chunks(query, session_id, k=5):
    try:
        # Load index and chunks with memory check
        index, chunks = load_index(session_id)
        
        # Limit query length and process embedding
        query = query[:1000]  # Limit query length
        q_vec = embed_texts([query])
        q_vec = normalize_embeddings(np.array(q_vec).astype("float32"))
        
        # Perform search
        _, I = index.search(q_vec, k)
        results = [chunks[i] for i in I[0]]
        
        # Clear memory
        del q_vec
        del index
        del chunks
        gc.collect()
        
        return results
        
    except Exception as e:
        print(f"Error in retrieve_chunks: {str(e)}")
        raise
    finally:
        # Ensure memory cleanup
        gc.collect()
