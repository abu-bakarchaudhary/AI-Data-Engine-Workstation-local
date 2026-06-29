from openai import OpenAI
import setup_wizard
import schema_manager

LOCAL_LLM_URL = "http://localhost:11434/v1"
LOCAL_MODEL_NAME = "qwen2.5-coder:1.5b"

DB_SQL_COMPILER_LAYOUT = """
You are a deterministic, senior database engineer specialized in compiling native {target_dialect} syntax execution maps.
You are given a strict, verified metadata catalog layout describing the exact live infrastructure database landscape.

{dynamic_schema}

CRITICAL COMPILING CONSTRAINTS & LOGICAL RULES:
1. DETERMINISTIC SCHEMA TRACKING: You can ONLY look up columns and tables explicitly declared in the layout manifest above. Never guess or assume fields exist.
2. FULL PREFIX QUALIFIERS: Every single table lookup inside the SELECT statement must explicitly carry its verified schema-qualified prefix (e.g., use `dbo.TableName`).
3. STRICT SECURITY LOCKDOWN: Never generate modifications (INSERT, UPDATE, DELETE). Output ONLY the executable query statement string.
4. NO MARKDOWN FORMATTING: Do not wrap your response inside markdown blocks (e.g. ```sql). Return only raw plaintext code.
"""

def translate_english_to_sql(approved_prompt, target_dialect):
    config = setup_wizard.load_config()
    if not config: return None
        
    complete_schema = schema_manager.fetch_complete_database_schema()
    formatted_system = DB_SQL_COMPILER_LAYOUT.format(target_dialect=target_dialect, dynamic_schema=complete_schema)
    
    client = OpenAI(api_key="local-machine-token", base_url=LOCAL_LLM_URL)
    response = client.chat.completions.create(
        model=LOCAL_MODEL_NAME,
        messages=[
            {"role": "system", "content": formatted_system}, 
            {"role": "user", "content": f"Compile exact executable statement code matrix for: {approved_prompt}"}
        ],
        temperature=0.0
    )
    content = response.choices[0].message.content
    return content.strip() if content else None