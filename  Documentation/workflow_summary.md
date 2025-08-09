# Well-Bot RAG Workflow (Phase 1–3)

## Core Components

### **1. External Dependencies**
- **Ollama**: Local LLM server (`http://localhost:11434`) running:
  - `gemma3`: Chat/generation model
  - `nomic-embed-text`: Text embedding model (768-dimensional)
- **Qdrant**: Vector database (`http://localhost:6333`) with two 
- **Docker**: Containerization for Qdrant

### 2. FastAPI App Structure
```
app/
├── main.py                     # FastAPI entry point, app lifecycle
├── config.py                   # Environment settings & configurations
├── schemas.py                  # Pydantic data models for API
├── routers/
│   └── ws_chat.py              # WebSocket chat endpoint
├── services/                   
│   ├── embedder.py             # Document embedding 
│   ├── generator.py            # LLM response generation
│   ├── RAG_pipeline.py         # RAG pipeline orchestration
│   ├── memory_summarizer.py    # Chat history summarization
│   ├── ollama_client.py        # Direct Ollama API client
│   ├── qdrant_store.py         # Vector database operations
│   └── retriever.py            # Document retrieval service
├── state/
│   └── session_store.py       # In-memory session management
├── utils/
│   ├── logging.py               # Logging utilities
│   └── prompts.py               # System prompts
└── testing/                     # Test scripts
```


## Data Flow by File Relationships

### A. Chat Flow (Real-time Conversation)
1. **`app/routers/ws_chat.py`**
   - Accepts WebSocket connection on `/ws/chat`
   - Parses incoming message (`app/schemas.py::ChatIn`)
   - Updates short-term conversation history in `app/state/session_store.py`
   - Calls `RAGPipeline.run_rag(...)` from `app/services/haystack_pipeline.py`

2. **`app/services/haystack_pipeline.py`**
   - Delegates retrieval to `DualRetriever` in `app/services/retriever.py`
   - Steps:
     - **Embed query** → `OllamaTextEmbedder` from `haystack_integrations` (model in `.env`)
     - **Retrieve KB docs** from Qdrant via `QdrantEmbeddingRetriever` (`kb_docs` collection)
     - **Retrieve memory docs** from Qdrant (`user_memory` collection)
     - **Combine results** → forward to LLM via `app/services/generator.py`
   - Streams generated tokens back to WebSocket via the `on_token` callback

3. **`app/services/generator.py`**
   - Sends the combined context + query to the LLM (Gemma3 on Ollama)
   - Yields tokens incrementally to `ws_chat.py`

4. **`app/routers/ws_chat.py`**
   - Sends streaming tokens as `TokenOut` to client
   - Sends retrieval metadata as `MetaOut`

5. **`app/services/memory_summarizer.py`**
   - Triggered asynchronously after each turn
   - Processes `(user_text, bot_text)` into bullet-point facts
   - Calls `_embed_and_upsert` to store in Qdrant `user_memory` collection via `app/services/qdrant_store.py`

---

### B. Memory Building (User Memory Pipeline)
1. **Input Source** → Triggered from `ws_chat.py` after a turn is complete  
2. **`app/services/memory_summarizer.py`**
   - Summarises conversation into concise factual memory
   - Embeds summary (OllamaTextEmbedder)
3. **`app/services/qdrant_store.py`**
   - Upserts embedded document into `user_memory` collection
4. **`app/services/retriever.py`**
   - On future queries, uses these embedded memories for personalised retrieval


## Key Collections in Qdrant
- **`kb_docs`** → Static knowledge base
- **`user_memory`** → Dynamic, summarised user facts



## Testing
### 1. Embedding Context Docs
```bash
python app/services/embedder.py
```
### 2. Real-time Chat
```bash
uvicorn app.main:app --reload
python app/testing/cli_chat.py
```

### Example Conversation
```
Well-Bot: Hi! How can I help you today?
User: I like to eat mangoes
Well-Bot: Okay, you enjoy mangoes. Is there anything specific you'd like to discuss about them?
User: What do I like to eat?
Well-Bot: Based on our previous conversations, you enjoy mangoes.
```

## Next Improvements
- Configurable prompts in utils/prompts.py
- Adjustable LLM generation parameters via .env
- Memory merge/overwrite policy
- Persistent session history in MongoDB