# Well-Bot RAG Backend

## Overview
This backend system provides context-aware conversational AI using Retrieval-Augmented Generation (RAG). It leverages Haystack pipelines, Ollama LLM, and Qdrant vector database to retrieve relevant context and generate empathetic, concise responses.

## Project Directory Structure
```
Well-Bot_RAG/
├── README.md                     # This documentation file
├── requirements.txt              # Python dependencies
├── notes.txt                     # Development notes
├── FunctionalRequirement.md      # System functional requirements
├── .gitignore                    # Git ignore rules
├── context_doc/                  # Context documents for RAG
│   ├── Islamic_Bulletin.txt
│   └── Alex_userContext.txt
├── app/                         # FastAPI application
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # App configuration
│   ├── schemas.py               # Pydantic data models
│   ├── routers/
│   │   └── ws_chat.py           # WebSocket chat router
│   ├── services/                # Core business logic
│   │   ├── embedder.py          # Document embedding service
│   │   ├── generator.py         # LLM response generation
│   │   ├── haystack_pipeline.py # Haystack pipeline management
│   │   ├── memory_summarizer.py # Chat history summarization
│   │   ├── qdrant_store.py      # Qdrant database operations
│   │   └── retriever.py         # Document retrieval service
│   ├── state/
│   │   └── session_store.py     # Session management
│   ├── utils/
│   │   └── logging.py          # Logging utilities
│   └── testing/                # Testing scripts
│       ├── smoke_test.py       # Simple WebSocket test
│       ├── chat_history.py     # Chat history tests
│       └── embedder.py         # Embedding tests
├── qdrant_store/               # Qdrant vector database files
└── well-bot_venv/              # Python virtual environment 
```

### Main Components
- **app/**: FastAPI web application with WebSocket support
  - **main.py**: FastAPI server entry point
  - **routers/ws_chat.py**: WebSocket chat endpoint
  - **services/**: Core business logic
    - **embedder.py**: Document embedding using Ollama
    - **generator.py**: LLM response generation
    - **haystack_pipeline.py**: Haystack pipeline orchestration
    - **memory_summarizer.py**: Chat history summarization
    - **qdrant_store.py**: Vector database operations
    - **retriever.py**: Document retrieval and search
  - **testing/**: Test scripts including smoke_test.py for WebSocket testing

## Technical Architecture
1. **Document Embedding**: Text files in `context_doc/` are embedded using Ollama and stored in Qdrant vector database.
2. **RAG Pipeline**: For each user query, the system retrieves the most relevant document using semantic search.
3. **LLM Integration**: Combines user query with retrieved context to generate empathetic responses via Ollama.
4. **WebSocket Chat**: Real-time streaming chat interface via FastAPI WebSocket endpoints.
5. **Session Management**: Chat history logging and session state management in Qdrant.
6. **Dual Interface**: Both CLI (backend scripts) and web API (FastAPI app) available.

## Installation Guide
### Prerequisites
- Python 3.13+
- Docker (for Qdrant vector DB)
- Ollama (local LLM server)

### Steps
1. **Clone the repository**
   ```powershell
   git clone <repo-url>
   cd Well-Bot_RAG
   ```
2. **Set up Python environment**
   ```powershell
   python -m venv well-bot_venv
   .\well-bot_venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Start Qdrant (Vector DB)**
   ```powershell
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```
4. **Start Ollama (LLM server)**
   - Download and run Ollama from https://ollama.com
   - Pull the gemma3 model: `ollama pull gemma3`
   - Ensure it is running at `http://localhost:11434`
5. **Prepare context documents**
   - Place `.txt` files in `context_doc/` folder.
6. **Embed documents (first time setup)**
   ```powershell
   python app/services/embedder.py
   ```
7. **Start the FastAPI server**
   ```powershell
   uvicorn app.main:app --reload
   ```
   Or run the CLI version:
   ```powershell
   python backend/chatter_rag.py
   ```

## Usage Example
### FastAPI WebSocket Chat
1. Start the server:
   ```powershell
   uvicorn app.main:app --reload
   ```
2. Test with WebSocket client:
   ```powershell
   python app/testing/test.py
   ```

### CLI Chat
1. Run the CLI chat bot:
   ```powershell
   python backend/chatter_rag.py
   ```
2. Type your question at the prompt:
   ```
   You: What is the meaning of life?
   Well-Bot: (response generated using context)
   ```
3. Type `exit` to end the session.

## Dependencies
- **Python packages**:
  - haystack
  - haystack-integrations (Ollama, Qdrant)
  - fastapi
  - uvicorn
  - websockets
  - asyncio
- **External services**:
  - Ollama (local LLM server at localhost:11434)
  - Qdrant (vector DB via Docker at localhost:6333)

## Workflow Summary
1. **Setup**: Load and embed context documents from `context_doc/` into Qdrant vector database.
2. **Query Processing**: For each user query, retrieve the most semantically similar document.
3. **RAG Generation**: Combine user query with retrieved context to create an augmented prompt.
4. **LLM Response**: Send prompt to Ollama LLM to generate empathetic, context-aware responses.
5. **Chat Logging**: Store user queries and bot responses in Qdrant for session history.
6. **Interface**: Support both WebSocket streaming (FastAPI) and CLI interaction modes.

## Notes
- This backend does not implement emotion monitoring, journaling, meditation, entertainment, or dashboard features yet.
- For full system requirements, see `FunctionalRequirement.md`.
