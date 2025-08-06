import os
import numpy as np
import faiss
import pickle
import yaml
import gc
import psutil
from datetime import datetime

# Lazy import helper
def lazy_import(module_name, attr_name=None):
    """Lazy import to reduce memory usage"""
    def _import():
        module = __import__(module_name, fromlist=[attr_name] if attr_name else [])
        return getattr(module, attr_name) if attr_name else module
    return _import

# Memory monitoring
def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    if memory_info.rss > 350 * 1024 * 1024:  # 350MB threshold (aggressive)
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

def build_index(text_chunks, session_id, force_rebuild=False, batch_size=25):
    """Ultra memory-efficient index building"""
    paths = get_paths(session_id)
    INDEX_PATH = paths["INDEX_PATH"]
    META_PATH = paths["META_PATH"]
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH) and not force_rebuild:
        return

    try:
        # Ultra-small batches
        all_chunks = []
        embed_texts = lazy_import('app.core.embedder', 'embed_texts')()
        
        for i in range(0, min(len(text_chunks), 1000), batch_size):  # Hard limit 1000 chunks
            batch = text_chunks[i:i + batch_size]
            
            # Generate embeddings with memory cleanup
            vectors = embed_texts(batch)
            vectors = normalize_embeddings(np.array(vectors).astype("float32"))
            
            if i == 0:
                dim = vectors.shape[1]
                index = faiss.IndexFlatIP(dim)
            
            index.add(vectors)
            all_chunks.extend(batch)
            
            # Aggressive cleanup
            del vectors, batch
            gc.collect()
            check_memory_usage()
        
        # Save with compression
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(all_chunks, f, protocol=pickle.HIGHEST_PROTOCOL)
            
    except Exception as e:
        raise
    finally:
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

def retrieve_chunks(query, session_id, k=2):
    """Ultra memory-efficient chunk retrieval"""
    try:
        # Lazy import
        embed_texts = lazy_import('app.core.embedder', 'embed_texts')()
        
        # Load with size limits
        index, chunks = load_index(session_id)
        
        # Severe query limits
        query = query[:200]  # Drastically reduce query length
        
        # Generate embedding
        q_vec = embed_texts([query])
        q_vec = normalize_embeddings(np.array(q_vec).astype("float32"))
        
        # Search with minimal results
        _, I = index.search(q_vec, min(k, len(chunks)))
        results = [chunks[i][:500] for i in I[0]]  # Truncate chunks
        
        # Aggressive cleanup
        del q_vec, index, chunks
        gc.collect()
        
        return results
        
    except Exception as e:
        gc.collect()
        return []
    finally:
        gc.collect()
