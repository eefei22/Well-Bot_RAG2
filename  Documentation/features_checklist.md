# Features Checklist (Phase 1–3)

## 1. Core Conversational AI
- [x] Real-time WebSocket chat (`/ws/chat`)
- [x] Multi-turn conversation loop
- [x] Streaming token responses
- [x] Session-based context tracking

## 2. RAG Pipeline
- [x] Dual retrieval (KB + user memory) via Qdrant
- [x] Single embedding per query (OllamaTextEmbedder)
- [x] Combined context passed to LLM (Gemma3)
- [x] Configurable top-K retrieval

## 3. Memory & Personalization
- [x] Memory summarization into bullet-point facts
- [x] Embedded & upserted into `user_memory`
- [x] Query-time merge of KB + memory context
- [ ] Temporal filtering automation (planned)

## 4. Testing & Validation
- [x] Smoke test for WebSocket RAG loop
- [x] Memory probe test
- [ ] Concurrent multi-user stress test (planned)

## 5. Next Steps
- [ ] Document database storage for full chat logs
- [ ] Auto-update KB embeddings on file changes
- [ ] Expand multi-user scalability testing
