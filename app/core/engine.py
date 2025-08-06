import os
import openai
import yaml
import json
import gc
import psutil
from app.core.retriever import retrieve_chunks

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
    openai.api_key = cfg["openai_api_key"]
except:
    # Fallback to environment variables
    openai.api_key = os.environ.get("openai_api_key")

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
    try:
        # Limit query length
        query = query[:1000]  # Limit to 1000 characters
        
        # Get relevant chunks with memory check
        retrieved_chunks = retrieve_chunks(query, session_id)
        
        # Limit number of chunks and their size
        retrieved_chunks = retrieved_chunks[:3]  # Limit to top 3 chunks
        clauses = "\n\n".join(chunk[:1000] for chunk in retrieved_chunks)  # Limit each chunk to 1000 chars
        
        # Format prompt
        prompt = COT.format(query=query, clauses=clauses)
        
        # Check memory before API call
        check_memory_usage()
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500  # Limit response length
        )
        
        raw_output = response['choices'][0]['message']['content'].strip()
        parsed_output = json.loads(raw_output)
        
        result = {
            "query": query,
            "response": parsed_output,
            "retrieved_clauses": retrieved_chunks
        }
        
        # Clear variables
        del response
        del raw_output
        del parsed_output
        gc.collect()
        
        return result

    except json.JSONDecodeError as e:
        return {
            "query": query,
            "response": {"error": "Invalid JSON response from GPT"},
            "retrieved_clauses": retrieved_chunks[:3]  # Limit chunks in error response
        }
    except Exception as e:
        return {
            "query": query,
            "response": {"error": str(e)},
            "retrieved_clauses": []
        }
    finally:
        # Ensure cleanup
        gc.collect()
        check_memory_usage()
