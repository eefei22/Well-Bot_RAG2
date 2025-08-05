# Well-Bot RAG Backend

## Overview
This backend system provides context-aware conversational AI using Retrieval-Augmented Generation (RAG). It leverages Haystack pipelines, Ollama LLM, and Qdrant vector database to retrieve relevant context and generate empathetic, concise responses.

### Main Components
- **chatter_rag.py**: Main conversational loop, builds prompts, interacts with LLM.
- **retriever.py**: Retrieves top relevant document for a user query using Qdrant and Ollama embeddings.
- **embedder.py**: Loads, embeds, and stores context documents in Qdrant for retrieval.

## Technical Architecture
1. **Document Embedding**: Text files in `context_doc/` are embedded using Ollama and stored in Qdrant via `embedder.py`.
2. **Retrieval**: For each user query, `retriever.py` finds the most relevant document using semantic search.
3. **Prompt Building**: `chatter_rag.py` builds a prompt with user query and retrieved context, then sends it to the LLM (Ollama) for response generation.
4. **Conversation**: The system streams responses and maintains a simple chat loop.

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
   - Ensure it is running at `http://localhost:11434`
5. **Prepare context documents**
   - Place `.txt` files in `context_doc/` folder.
6. **Embed documents**
   ```powershell
   python backend/embedder.py
   ```
7. **Start the chat bot**
   ```powershell
   python backend/chatter_rag.py
   ```

## Usage Example
1. Run the chat bot:
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
- haystack
- haystack-integrations (Ollama, Qdrant)
- ollama (local server)
- qdrant (vector DB via Docker)

## Workflow Summary
1. Load context documents from `context_doc/`.
2. Embed documents using Ollama and store in Qdrant.
3. For each user query, retrieve top relevant document.
4. Build prompt and generate response using LLM.
5. Stream response to user.

## Notes
- This backend does not implement emotion monitoring, journaling, meditation, entertainment, or dashboard features yet.
- For full system requirements, see `FunctionalRequirement.md`.
