import os
import json
import gc
import psutil

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

# Load API key lazily
def get_api_key():
    try:
        import yaml
        with open("config/config.yaml") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("openai_api_key", os.environ.get("openai_api_key"))
    except:
        return os.environ.get("openai_api_key")

COT = """
You are a claims evaluation assistant. You are provided with:
- A customer query
- Retrieved policy document clauses

Your job is to:
1. Identify the important fields from the query (e.g., age, procedure, location, policy duration).
2. Think step-by-step to determine if the policy covers this case.
3. Reference specific clauses to justify your reasoning.
4. Give a structured JSON response with:
    - decision ("approved" or "rejected")
    - amount (if any)
    - justification

---

Query:
{query}

Retrieved Clauses:
{clauses}

---

⚠️ DO NOT return markdown, explanations, or extra text.
✅ Just return valid JSON. No triple backticks.
"""

def evaluate_decision(query, session_id):
    """Ultra memory-efficient decision evaluation"""
    try:
        # Lazy imports
        retrieve_chunks = lazy_import('app.core.retriever', 'retrieve_chunks')()
        openai = lazy_import('openai')()
        
        # Ultra-strict limits
        query = query[:100]  # Severe query truncation
        
        # Get chunks with minimal memory
        retrieved_chunks = retrieve_chunks(query, session_id)
        
        # Drastic chunk limits
        retrieved_chunks = retrieved_chunks[:1]  # Only 1 chunk
        clauses = "\n".join(chunk[:200] for chunk in retrieved_chunks)  # 200 chars max
        
        # Compact prompt
        prompt = f"Query: {query}\nPolicy: {clauses}\nReturn JSON: {{\"decision\":\"approved/rejected\",\"justification\":\"brief\"}}"
        
        # Check memory aggressively
        check_memory_usage()
        
        # Configure OpenAI
        openai.api_key = get_api_key()
        
        # Minimal API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50  # Extremely limited response
        )
        
        # Parse minimal response
        content = response['choices'][0]['message']['content'].strip()
        try:
            parsed = json.loads(content)
        except:
            parsed = {"decision": "error", "justification": "parse failed"}
        
        # Minimal result
        result = {
            "decision": parsed.get("decision", "error"),
            "justification": parsed.get("justification", "")[:100]
        }
        
        # Ultra cleanup
        del response, content, parsed, retrieved_chunks
        for _ in range(2):
            gc.collect()
        
        return result

    except Exception as e:
        gc.collect()
        return {"decision": "error", "justification": str(e)[:50]}
    finally:
        gc.collect()
        check_memory_usage()
