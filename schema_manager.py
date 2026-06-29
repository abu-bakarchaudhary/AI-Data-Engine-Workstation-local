import os
import json
import pyodbc
import setup_wizard
import intent_enhancer

MANIFEST_FILE = "db_manifest.json"

def get_connection_string():
    config = setup_wizard.load_config()
    if not config: return ""
    base_str = f"Driver={config['driver']};Server={config['server']};Database={config['database']};"
    if config['auth_type'] == "Windows":
        base_str += "Trusted_Connection=yes;"
    else:
        base_str += f"UID={config['username']};PWD={config['password']};"
    return base_str

def fetch_complete_database_schema():
    conn_str = get_connection_string()
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        column_query = """
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
              AND TABLE_NAME NOT IN ('sysdiagrams')
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
        """
        cursor.execute(column_query)
        rows = cursor.fetchall()
        
        schema_map = {}
        for row in rows:
            schema, table, column, dtype = row[0], row[1], row[2], row[3]
            full_table_name = f"{schema}.{table}"
            if full_table_name not in schema_map: 
                schema_map[full_table_name] = []
            schema_map[full_table_name].append(f"  - {column} ({dtype.upper()})")
            
        cursor.close()
        conn.close()
        
        rag_payload = {}
        schema_text = "### HARDWARE PRODUCTION DATABASE ARCHITECTURE MANIFEST\n\n"
        for table_name, columns in schema_map.items():
            table_block = f"#### TABLE OBJECT: {table_name}\nCOLUMNS REGISTERED:\n" + "\n".join(columns)
            schema_text += table_block + "\n\n"
            rag_payload[table_name] = table_block
            
        # Automatically updates ChromaDB index coordinates upon database mapping
        intent_enhancer.sync_rag_vector_database(rag_payload)
        
        return schema_text
    except Exception as e:
        raise Exception(f"Live metadata collection failed: {e}")

def execute_raw_sql(query):
    conn = pyodbc.connect(get_connection_string())
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    data = [list(row) for row in rows]
    cursor.close()
    conn.close()
    return columns, data