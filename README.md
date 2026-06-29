# AI Data Engine Workstation

A fully offline, local AI-powered SQL generation workstation. Uses a local LLM (via Ollama) with RAG-based context enhancement (ChromaDB) to convert natural language into executable SQL queries. No cloud dependencies.

## How It Works

The app processes your request through a four-stage pipeline:

```
You: "show me active customers"
        |
        v
[Setup Wizard] â€” Configure DB connection on first launch
        |
        v
[Intent Enhancer] â€” RAG + LLM rewrites your vague request
  - ChromaDB indexes your entire DB schema as vectors
  - Queries the 2 most relevant tables for context
  - LLM produces a structured analytical specification
        |
        v
[SQL Compiler] â€” LLM generates SQL from the spec
  - Uses the full DB schema as context
  - Targets your chosen SQL dialect
        |
        v
[SQL Linter] â€” Validates and auto-heals
  - sqlglot checks syntax offline
  - LLM auto-heals any syntax errors
  - Retries on DB driver errors too
        |
        v
[Schema Manager] â€” Executes SQL & shows results
  - Runs the query against your DB
  - Displays results in a table grid
```

## Features

- **Fully Offline**: Everything runs locally â€” Ollama + ChromaDB + sqlglot, no internet required
- **RAG Context Enhancement**: ChromaDB automatically indexes your database schema for smarter, context-aware query generation
- **Multi-Dialect Support**: Microsoft SQL Server, MySQL, PostgreSQL, Oracle, SQLite, and custom dialects
- **SQL Linting & Auto-Healing**: sqlglot validates syntax offline; if it fails, the LLM automatically repairs the query
- **Interactive GUI**: Tkinter-based desktop interface with real-time status, SQL output panel, and results grid
- **Intent Clarification Gate**: Review and edit the LLM's interpretation of your request before SQL generation
- **Database Schema Discovery**: Auto-discovers databases and schemas from your SQL Server instance
- **Persistent Configuration**: Saves DB connection settings for subsequent launches

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) with a code model (default: `qwen2.5-coder:1.5b`)
- ODBC Driver for SQL Server (e.g., "ODBC Driver 17 for SQL Server")
- A Microsoft SQL Server instance (local or remote)

## Installation

```bash
# Clone the repository
git clone https://github.com/abu-bakarchaudhary/AI-Data-Engine-Workstation-local.git
cd AI-Data-Engine-Workstation-local

# Install dependencies
pip install openai chromadb sqlglot pyodbc

# Pull the LLM model
ollama pull qwen2.5-coder:1.5b

# Run the application
python app.py
```

### Custom Ollama Model

You can use a custom Ollama model by modifying the `Modelfile`:

```
FROM qwen2.5-coder:1.5b
PARAMETER num_ctx 8192
```

Then build: `ollama create local-small-brain -f Modelfile`

The app references the model in `sql_compiler.py` and `intent_enhancer.py` â€” update `LOCAL_MODEL_NAME` there if you change it.

## Configuration

On first launch, the setup wizard will ask for:

1. **ODBC Driver** â€” Select your SQL Server ODBC driver
2. **Instance Path** â€” Server address (e.g., `localhost`, `.\SQLEXPRESS`)
3. **Authentication** â€” Windows Trusted or SQL Server login
4. **Database** â€” Click "Discover Instance Catalogs" to scan available databases
5. **API Key** â€” Dummy key for local LLM (default: `local-machine-token`)

Settings are saved to `config.json` automatically.

## Usage

1. Launch the app: `python app.py`
2. If no config exists, the setup wizard appears â€” fill in your DB details
3. The main window shows:
   - **Input field** at the top â€” type your query in natural language
   - **SQL Dialect** dropdown â€” select your target dialect
   - **Status bar** â€” shows pipeline progress
   - **SQL output panel** â€” displays the generated query
   - **Results grid** â€” shows query execution results
4. Type something like `"show me all customers who placed orders last month"` and press Enter
5. Review the enhanced specification in the **Intent Clarification Gate** dialog, edit if needed, then confirm
6. The generated SQL appears in the output panel with results below

### Tips

- Be specific about column names and filters for better results
- The intent clarification dialog lets you edit the spec before SQL generation â€” use it to correct table names
- Running the app with an existing config prompts to reload it; choose "No" to reconfigure

## Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Main entry point â€” Tkinter GUI and pipeline orchestration |
| `setup_wizard.py` | Database connection setup wizard |
| `intent_enhancer.py` | RAG-based prompt enhancement using ChromaDB + LLM |
| `sql_compiler.py` | Natural language to SQL translation via LLM |
| `sql_linter.py` | SQL syntax validation (sqlglot) and LLM auto-healing |
| `schema_manager.py` | Database schema discovery, RAG sync, and query execution |
| `config.json` | Saved database connection configuration |
| `Modelfile` | Ollama model definition |

## Architecture

```
                    +-----------+
                    |  app.py   |
                    |  (GUI)    |
                    +-----+-----+
                          |
          +---------------+---------------+
          |               |               |
    +-----v------+  +----v-------+  +----v-------+
    | setup_     |  | intent_    |  | sql_       |
    | wizard     |  | enhancer   |  | compiler   |
    | .py        |  | .py        |  | .py        |
    +------------+  +-----+------+  +------+-----+
                          |                 |
                          | (RAG: ChromaDB) |
                          +--------+--------+
                                   |
                            +------v------+
                            | schema_     |
                            | manager     |
                            | .py         |
                            +------+------+
                                   |
                            +------v------+
                            | sql_linter  |
                            | .py         |
                            +------+------+
                                   |
                            +------v------+
                            |  Database   |
                            +-------------+
```

## Safety

- All SQL generation is read-only â€” the system prompt explicitly prohibits INSERT, UPDATE, DELETE
- The linter catches malformed SQL before execution
- Auto-healing is limited to syntax fixes only

## License

MIT
