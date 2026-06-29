# AI Data Engine Workstation

A local, offline AI-powered SQL generation workstation. Uses a local LLM (via Ollama) with RAG-based context enhancement to convert natural language into executable SQL queries.

## Features

- **Natural Language to SQL**: Describe what you want in plain English, get optimized SQL
- **RAG Context Enhancement**: ChromaDB vector store automatically indexes your database schema for smarter query generation
- **Multi-Dialect Support**: Microsoft SQL Server, MySQL, PostgreSQL, Oracle, SQLite, and custom dialects
- **SQL Linting & Auto-Healing**: Validates generated SQL with sqlglot and auto-fixes syntax errors
- **Interactive GUI**: Tkinter-based desktop interface with query editing and results grid
- **Offline-First**: Everything runs locally - no cloud dependencies
- **Database Schema Discovery**: Auto-discovers databases and schemas from your SQL Server instance

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) with a code model (e.g., qwen2.5-coder:1.5b)
- ODBC Driver for SQL Server
- A SQL Server instance (local or remote)

## Installation

`ash
# Clone the repo
git clone https://github.com/abu-bakarchaudhary/AI-Data-Engine-Workstation-local.git
cd AI-Data-Engine-Workstation-local

# Install dependencies
pip install openai chromadb sqlglot pyodbc

# Pull the LLM model
ollama pull qwen2.5-coder:1.5b

# Run the application
python app.py
`

## Usage

1. Launch the app - the setup wizard will prompt for database connection details
2. Select your SQL dialect from the dropdown
3. Type your query in natural language (e.g., "show me all active customers")
4. Review and edit the enhanced specification in the confirmation dialog
5. The generated SQL appears in the output panel with results in the grid below