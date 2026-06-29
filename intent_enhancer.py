import chromadb
from openai import OpenAI

LOCAL_LLM_URL = "http://localhost:11434/v1"
LOCAL_MODEL_NAME = "qwen2.5-coder:1.5b"  # Replace with 'local-small-brain' if Modelfile context is generated

# Initialize local disk-persisted vector storage
chroma_client = chromadb.PersistentClient(path="./chroma_rag_store")
collection = chroma_client.get_or_create_collection(name="database_schema_rag")

PROMPT_ENHANCER_LAYOUT = """
[ROLE]
You are a strict, silent translation layer that optimizes messy human text into an explicit analytical specification sentence.

[CONTEXT DATA]
The user's database contains these highly relevant tables to answer their question:
{candidate_tables}

[STRICT RULES]
1. Rewrite the user's intent to explicitly include table names, column rules, and required structural joins.
2. DO NOT explain anything. DO NOT introduce your answer. DO NOT write an introduction or greeting.
3. CRITICAL: NEVER write SQL code (e.g., SELECT, FROM, WHERE). Only output a plain English sentence.
4. If you output a backtick, conversational fillers, or a single line of SQL syntax code, the system breaks.

[FEW-SHOT TRAINING EXAMPLE]
Input Question: "show me active customers"
Correct Output: A list of all customer records from dbo.Customers where their account status column equals 'Active' sorted by creation date.

[YOUR TASK]
Optimize this input string expression:
"""

def sync_rag_vector_database(schema_map):
    """Indexes your entire database structure into local vectors."""
    for table_name, schema_text in schema_map.items():
        collection.upsert(
            ids=[table_name],
            documents=[f"Table: {table_name}\nFields Manifest:\n{schema_text}"],
            metadatas=[{"table": table_name}]
        )

def enhance_user_prompt(raw_input_prompt):
    # Perform a local semantic query to isolate the 2 best matched structures max
    rag_results = collection.query(
        query_texts=[raw_input_prompt],
        n_results=2  
    )
    
    extracted_context = "\n\n".join(rag_results["documents"][0]) if rag_results["documents"] else "None"
    formatted_system = PROMPT_ENHANCER_LAYOUT.format(candidate_tables=extracted_context)
    
    client = OpenAI(api_key="local-machine-token", base_url=LOCAL_LLM_URL)
    response = client.chat.completions.create(
        model=LOCAL_MODEL_NAME,
        messages=[
            {"role": "system", "content": formatted_system},
            {"role": "user", "content": f"Optimize this input string expression: {raw_input_prompt}"}
        ],
        temperature=0.0
    )
    
    content = response.choices[0].message.content
    return content.strip() if content else raw_input_prompt