import sqlglot
from sqlglot.errors import ParseError
from openai import OpenAI
import setup_gui

LOCAL_LLM_URL = "http://localhost:11434/v1"
LOCAL_MODEL_NAME = "qwen2.5-coder:1.5b"

def offline_syntax_check(sql_query, dialect):
    dialect_map = {
        "Microsoft SQL Server": "tsql",
        "MySQL": "mysql",
        "PostgreSQL": "postgres",
        "Oracle": "oracle",
        "SQLite": "sqlite"
    }
    target_dialect = dialect_map.get(dialect, "sql")
    try:
        sqlglot.transpile(sql_query, read=target_dialect)
        return True, None
    except ParseError as e:
        return False, str(e)

def execute_auto_heal_loop(original_prompt, broken_sql, error_message, dialect):
    config = setup_gui.load_config()
    if not config: return broken_sql
        
    client = OpenAI(api_key="local-machine-token", base_url=LOCAL_LLM_URL)
    
    heal_directive = f"""
    The SQL query you generated for the {dialect} dialect failed local linter validation or threw a database driver error.
    
    ORIGINAL SPECIFICATION: {original_prompt}
    BROKEN SQL GENERATED: {broken_sql}
    RAISED ERROR CRASH LOG: {error_message}
    
    TASK: Correct the syntax mistake immediately. Fix mismatched parentheses, wrong table joins, or illegal keywords.
    OUTPUT CONSTRAINT: Return ONLY the raw corrected SQL query string text block. Do not add markdown backticks or explanations.
    """
    
    try:
        response = client.chat.completions.create(
            model=LOCAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": f"You are an automated self-healing SQL repair agent specialized in {dialect} syntax."},
                {"role": "user", "content": heal_directive}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content
        return content.strip() if content else broken_sql
    except Exception:
        return broken_sql