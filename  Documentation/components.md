# Well-Bot RAG System: Python Components Reference

### Overview
This document provides a comprehensive reference of all Python files in the Well-Bot RAG system, organized by their location and functionality.


## Python Files Directory

| **File Path** | **Description & Purpose** |
|---------------|---------------------------|
| **Core Application** |  |
| `app/main.py` | • **FastAPI Application Entry Point**<br/>• Creates and configures FastAPI app instance<br/>• Registers WebSocket router for `/ws/chat` endpoint<br/>• Implements startup event for Qdrant bootstrap<br/>• Provides health check endpoint at `/health` |
| `app/config.py` | • **Application Configuration Management**<br/>• Defines `Settings` class using Pydantic BaseSettings<br/>• Manages environment variables and default values<br/>• Configures Ollama URLs and model names (gemma3, nomic-embed-text)<br/>• Sets Qdrant database connection and collection names<br/>• Handles CORS origins and session backend configuration |
| `app/schemas.py` | • **Pydantic Data Models for API**<br/>• Defines `ChatIn` schema for incoming WebSocket messages<br/>• Implements streaming response schemas: `TokenOut`, `MetaOut`, `DoneOut`, `ErrorOut`<br/>• Provides `RetrievalDocMeta` for retrieval metadata<br/>• Includes `UsageMeta` for telemetry and performance tracking |
| **WebSocket & Routing** |  |
| `app/routers/ws_chat.py` | • **WebSocket Chat Endpoint Handler**<br/>• Manages real-time WebSocket connections at `/ws/chat`<br/>• Orchestrates complete chat pipeline: input → RAG → streaming output<br/>• Handles session management and conversation history<br/>• Implements error handling and connection lifecycle management<br/>• Triggers asynchronous memory summarization after responses |
| **Core Services** |  |
| `app/services/haystack_pipeline.py` | • **RAG Pipeline Orchestration**<br/>• Implements `RAGPipeline` class for end-to-end retrieval-augmented generation<br/>• Coordinates dual retrieval (knowledge base + user memory)<br/>• Manages conversation history integration with configurable limits<br/>• Formats retrieved context and constructs LLM prompts<br/>• Provides metadata collection for retrieval sources and performance |
| `app/services/retriever.py` | • **Dual Retrieval System Implementation**<br/>• Implements `DualRetriever` for parallel knowledge base and memory search<br/>• Uses Ollama text embedder for query vectorization<br/>• Provides Qdrant embedding retrieval with filtering capabilities<br/>• Handles user isolation, session scoping, and temporal filtering<br/>• Combines and deduplicates results with memory prioritization |
| `app/services/generator.py` | • **LLM Response Generation Service**<br/>• Implements `LLMGenerator` class for Ollama-based text generation<br/>• Converts Haystack ChatMessages to Ollama API format<br/>• Simulates streaming by chunking complete responses<br/>• Handles generation parameters (temperature, top_p)<br/>• Provides usage metadata for monitoring and optimization |
| `app/services/ollama_client.py` | • **Direct Ollama API Client**<br/>• Implements `DirectOllamaClient` for HTTP communication with Ollama<br/>• Handles `/api/chat` endpoint calls with proper error handling<br/>• Uses non-streaming mode for reliability and consistency<br/>• Manages request timeouts and response parsing<br/>• Configurable model selection and generation options |
| `app/services/memory_summarizer.py` | • **Conversation Memory Processing**<br/>• Implements `MemorySummarizer` for extracting durable user facts<br/>• Uses LLM to identify stable preferences, habits, and personal information<br/>• Filters out temporary states and chat logistics<br/>• Embeds and stores memory snippets in user_memory collection<br/>• Provides asynchronous processing to avoid blocking chat responses |
| `app/services/embedder.py` | • **Document Embedding and Indexing**<br/>• Loads text documents from `context_doc/` folder<br/>• Uses Ollama document embedder (nomic-embed-text) for vectorization<br/>• Stores embedded documents in kb_docs Qdrant collection<br/>• Implements upsert policy for document updates<br/>• Provides initial knowledge base setup functionality |
| `app/services/qdrant_store.py` | • **Vector Database Management**<br/>• Implements Qdrant collection creation and configuration<br/>• Sets up vector parameters (768 dimensions, cosine similarity)<br/>• Creates payload indexes for efficient filtering (user_id, session_id, timestamp)<br/>• Provides bootstrap functionality for application startup<br/>• Handles collection existence checks and creation |
| **State Management** |  |
| `app/state/session_store.py` | • **In-Memory Session Storage**<br/>• Implements `SessionStore` class for temporary conversation state<br/>• Provides get/set/delete operations for session data<br/>• Stores conversation history and user context during active sessions<br/>• Designed for horizontal scaling (future Redis integration)<br/>• Maintains session isolation and data consistency |
| **Utilities** |  |
| `app/utils/logging.py` | • **Centralized Logging Configuration**<br/>• Provides `get_logger()` function for consistent logging across services<br/>• Implements structured logging with configurable levels<br/>• Handles log formatting and output destination management<br/>• Supports debugging and production monitoring requirements |
| `app/utils/prompts.py` | • **System Prompt Management**<br/>• Defines core system prompts for Well-Bot personality<br/>• Implements `build_system()` function for context integration<br/>• Maintains prompt consistency across different conversation contexts<br/>• Provides foundation for response tone and behavior control |
| **Testing Scripts** |  |
| `app/testing/smoke_test.py` | • **WebSocket Integration Test**<br/>• Tests complete chat pipeline with multi-turn conversations<br/>• Validates memory persistence across conversation turns<br/>• Demonstrates WebSocket message format and flow<br/>• Provides regression testing for core functionality<br/>• Tests user preference learning and retrieval |
| `app/testing/cli_chat.py` | • **Command-Line Chat Interface**<br/>• Provides interactive CLI for testing WebSocket chat<br/>• Implements user-friendly input/output formatting<br/>• Handles WebSocket connection lifecycle and errors<br/>• Supports session management with generated session IDs<br/>• Enables manual testing and demonstration of chat capabilities |
| `app/testing/memory_probe.py` | • **Memory System Direct Testing**<br/>• Tests memory embedding and storage without LLM summarization<br/>• Validates Qdrant user_memory collection operations<br/>• Provides debugging capabilities for memory persistence<br/>• Demonstrates direct vector store read/write operations<br/>• Enables memory system validation and troubleshooting |
| `app/testing/chat_history.py` | • **Chat History Retrieval Tool**<br/>• Connects to Qdrant chat_history collection (if exists)<br/>• Retrieves and displays stored conversation messages<br/>• Implements timestamp-based sorting for chronological view<br/>• Provides chat session analysis and debugging capabilities<br/>• Supports conversation history auditing and review |
| `app/testing/embedder.py` | • **Embedding System Unit Test**<br/>• Tests Ollama document embedder functionality<br/>• Validates embedding generation and dimensionality<br/>• Provides quick verification of embedding service health<br/>• Demonstrates basic embedding pipeline operation<br/>• Enables embedding system debugging and validation |

---

## File Organization Structure

### **Core Application Layer**
- **Entry Point**: `main.py` - FastAPI application lifecycle
- **Configuration**: `config.py` - Environment and settings management  
- **Data Models**: `schemas.py` - API request/response structures

### **Communication Layer**
- **WebSocket Handler**: `ws_chat.py` - Real-time chat endpoint
- **Session Management**: `session_store.py` - Temporary state storage

### **Business Logic Layer**
- **Pipeline Orchestration**: `haystack_pipeline.py` - RAG workflow coordination
- **Information Retrieval**: `retriever.py` - Dual search implementation
- **Response Generation**: `generator.py` - LLM text generation
- **Memory Processing**: `memory_summarizer.py` - Conversation learning
- **Knowledge Indexing**: `embedder.py` - Document vectorization

### **Infrastructure Layer**  
- **AI Services**: `ollama_client.py` - LLM API communication
- **Data Persistence**: `qdrant_store.py` - Vector database management
- **Utilities**: `logging.py`, `prompts.py` - Support functions

### **Testing & Validation Layer**
- **Integration Tests**: `smoke_test.py` - End-to-end validation
- **User Interfaces**: `cli_chat.py` - Interactive testing
- **Component Tests**: `memory_probe.py`, `embedder.py` - Unit validation
- **Data Analysis**: `chat_history.py` - Conversation review

---

## Key Design Patterns

### **Service-Oriented Architecture**
- Each service has a single responsibility and clear interface
- Services communicate through well-defined data structures
- Dependency injection through constructor parameters

### **Async/Streaming Patterns** 
- WebSocket for real-time bidirectional communication
- Async processing for non-blocking memory operations
- Chunked streaming for improved user experience

### **Configuration-Driven Design**
- Environment-based configuration via Pydantic Settings
- Model and service parameters externalized to config
- Easy deployment across different environments

### **Testing Infrastructure**
- Comprehensive test coverage from unit to integration levels
- Multiple testing interfaces (CLI, WebSocket, direct API)
- Debugging tools for each major system component

This component reference serves as a technical guide for understanding, maintaining, and extending the Well-Bot RAG system architecture.
