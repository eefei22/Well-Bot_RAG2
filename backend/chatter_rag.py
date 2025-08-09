from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline, Document
from retriever import retrieve_top_document
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from datetime import datetime, timezone, timedelta
import uuid

# Setup document store for chat logs
document_store = QdrantDocumentStore(
    url="http://localhost:6333",
    index="chat_history",
    recreate_index=False,  # Keep existing history
    return_embedding=True,
    wait_result_from_api=True,
    embedding_dim=768,
    similarity="cosine"
)

# Initialize once outside the loop
prompt_builder = ChatPromptBuilder()
generator = OllamaChatGenerator(
    model="gemma3",                     #try with llama2-chinese
    url="http://localhost:11434", 
    generation_kwargs={"temperature": 0.9},
)

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)
pipe.connect("prompt_builder.prompt", "llm.messages")

# Conversation loop
print("\nWell-Bot: Hi there, how are you feeling today?")
while True:
    user_query = input("\n\nYou: ")
    if user_query.lower() == "exit":
        print("Exiting chat.")
        break

    context = retrieve_top_document(user_query)

    # Build prompt with context and history
    messages = [
        ChatMessage.from_system(
            f"Responses should only asnwer to user's query, do not mention anything unnecessary"
            f"Response MUST not exceed 200 words"
            f"Do not ever use emojis. "
            f"Use a friendly and empathetic tone in all replies."
            f"You are Well-Bot and You are talking to your owner, Alex"
            f"Here is extra context: {context}"),
        ChatMessage.from_user(user_query),
    ]

    result = pipe.run(
        data={"prompt_builder": {"template": messages}}
    )

    reply_text = result["llm"]["replies"][0].text
    print("\n\n Copy:", reply_text)

    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    chat_docs = [
        Document(content=user_query, meta={"role": "user", "timestamp": now}),
        Document(content=reply_text, meta={"role": "assistant", "timestamp": now}),
    ]

    document_store.write_documents(chat_docs)

    # reply = result["llm"]["replies"][0].text
    # print("\nWell-Bot:", reply)


# ================================================================
# DEPENDENCIES REQUIRED:
# ================================================================
# haystack
# haystack-integrations (Ollama, Qdrant)
# ollama (Ollama server running at http://localhost:11434)
# qdrant (vector DB running at http://localhost:6333)
# retriever.py (local module)
#
# ================================================================
# WORKFLOW SUMMARY:
# ================================================================
# 1. User inputs a query.
# 2. The query is passed to `retrieve_top_document` to fetch relevant context from Qdrant.
# 3. A prompt is built using the context and user query, with system instructions.
# 4. The prompt is sent to the OllamaChatGenerator (LLM) via a Haystack pipeline.
# 5. The LLM generates a response, which is printed to the console.
# 6. Both user query and bot reply are logged as documents in the Qdrant vector database (chat_history index).
# 7. The conversation continues until the user types 'exit'.

