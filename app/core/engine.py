import openai
import yaml
import json
from app.core.retriever import retrieve_chunks

# Load API key from config file
with open("config/config.yaml") as f:
    cfg = yaml.safe_load(f)

openai.api_key = cfg["openai_api_key"]

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
    retrieved_chunks = retrieve_chunks(query, session_id)
    clauses = "\n\n".join(retrieved_chunks)
    prompt = COT.format(query=query, clauses=clauses)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        raw_output = response['choices'][0]['message']['content'].strip()

        parsed_output = json.loads(raw_output)
        return {
            "query": query,
            "response": parsed_output,
            "retrieved_clauses": retrieved_chunks
        }

    except json.JSONDecodeError:
        return {
            "query": query,
            "response": {"error": "Invalid JSON response from GPT", "raw": raw_output},
            "retrieved_clauses": retrieved_chunks
        }
    except Exception as e:
        return {
            "query": query,
            "response": {"error": str(e)},
            "retrieved_clauses": retrieved_chunks
        }
