# Well-Bot RAG Backend

## Overview
Backend system for **Well-Bot**, a context-aware conversational AI using Retrieval-Augmented Generation (RAG).  
Built with **FastAPI**, **Haystack**, **Ollama**, and **Qdrant**, it combines a static knowledge base with dynamic, personalized memory for real-time, multi-turn conversations.

---

## 1. Project Directory Structure
```
Well-Bot_RAG/
├── context_doc/           # Static knowledge base docs
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── routers/           # WebSocket chat endpoint
│   ├── services/          # RAG, retrieval, memory, embeddings
│   ├── state/             # Session store
│   ├── utils/             # Logging & prompts
│   └── testing/           # Smoke tests, CLI tools
├── Documentation/         # components.md, workflow_summary.md, features_checklist.md
├── qdrant_store/           # Local Qdrant data (if not using Docker)
└── requirements.txt
```

---

## 2. Main Components
- **RAGPipeline**: Orchestrates query embedding, KB + memory retrieval, and LLM response.
- **DualRetriever**: Searches both `kb_docs` (static KB) and `user_memory` (personalized facts).
- **MemorySummarizer**: Extracts, embeds, and stores bullet-point user facts asynchronously.
- **WebSocket Chat**: `/ws/chat` endpoint for multi-turn streaming conversation.
- **Session Store**: Maintains short-term in-memory conversation history.

---

## 3. Technical Architecture
- **FastAPI + WebSocket** for real-time chat.
- **Haystack** for retrieval pipelines and embedding integration.
- **Ollama** (`gemma3`, `nomic-embed-text`) for LLM and embeddings.
- **Qdrant** for vector storage (collections: `kb_docs`, `user_memory`).
- **Async Memory Pipeline** to build long-term user context without blocking chat.

---

## 4. Installation Guide
**Prerequisites**: Python 3.13+, Docker (Qdrant), Ollama.

```bash
# 1. Clone the repository
git clone https://github.com/eefei22/Well-Bot_RAG2.git
cd Well-Bot_RAG2

# 2. Set up Python virtual environment
python -m venv well-bot_venv
.\well-bot_venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Start Qdrant (Vector DB)
docker run -p 6333:6333 -p 6334:6334 `
  -v "<<storage path>>" `
  qdrant/qdrant
  
# 4. Start Ollama (LLM server)
#    - Download and install from https://ollama.com
#    - Pull model for chat:
      ollama pull gemma3
#    - Optional: pull model for embeddings (e.g., nomic-embed-text)
```

Initialize KB:
```bash
python app/services/embedder.py
```
Run server:
```bash
uvicorn app.main:app --reload
```

---

## 5. Usage Example
**Smoke test**:
```bash
python app/testing/smoke_test.py
```
**Multi-turn memory example**:
```
You: I love eating mangoes
Well-Bot: That’s wonderful! Mangoes are…
You: What fruit do I like?
Well-Bot: Based on our conversation, you like mangoes.
```

---

## 6. Dependencies
- `fastapi`, `uvicorn`, `websockets`, `pydantic`
- `haystack-ai`, `haystack-integrations` (ollama, qdrant)
- `qdrant-client`, `httpx`, `python-dotenv`
- **External**: Ollama (local LLM server), Qdrant (Docker or local)

---

## 7. Workflow Summary
See [`Documentation/workflow_summary.md`](Documentation/workflow_summary.md) for details.  
High-level flow:
1. User connects → sends message via `/ws/chat`.
2. RAGPipeline embeds query, retrieves KB + memory docs.
3. Combined context sent to LLM → streams tokens back.
4. MemorySummarizer distills turn → stores in `user_memory` for future personalization.

---

## More Details
- **Components**: [`Documentation/components.md`](Documentation/components.md)  
- **Workflow**: [`Documentation/workflow_summary.md`](Documentation/workflow_summary.md)  
- **Features**: [`Documentation/features_checklist.md`](Documentation/features_checklist.md)  
