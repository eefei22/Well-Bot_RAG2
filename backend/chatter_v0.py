from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline
from retriever import retrieve_top_document

# Initialize once outside the loop
prompt_builder = ChatPromptBuilder()
generator = OllamaChatGenerator(
    model="gemma3",
    url="http://localhost:11434", 
    streaming_callback=lambda chunk: print(chunk.content, end="", flush=True),
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
    print("\nWell-Bot: ")
    if user_query.lower() == "exit":
        print("Exiting chat.")
        break

    context = retrieve_top_document(user_query)

    # Build prompt with context and history
    messages = [
        ChatMessage.from_system(
            "Responses should only asnwer to user's query, do not mention anything unnecessary"
            f"Response MUST not exceed 200 words"
            f"Do not ever use emojis. "
            f"Use a friendly and empathetic tone in all replies."
            f"You are talking to your owner, Alex"
            f"Here is extra context: {context}"),
        ChatMessage.from_user(user_query),
    ]

    result = pipe.run(
        data={"prompt_builder": {"template": messages}}
    )

    # reply = result["llm"]["replies"][0].text
    # print("\nWell-Bot:", reply)

# ================================================================
# DEPENDENCIES REQUIRED:
# ================================================================
# haystack
# haystack-integrations
# ollama (Ollama server running at localhost:11434)
# retriever.py (local module)
#
# ================================================================
# WORKFLOW SUMMARY:
# ================================================================
# 1. User inputs a query.
# 2. The query is passed to `retrieve_top_document` to fetch relevant context.
# 3. A prompt is built using the context and user query, with system instructions.
# 4. The prompt is sent to the OllamaChatGenerator (LLM) via a Haystack pipeline.
# 5. The LLM generates a response, streamed to the console.
# 6. The conversation continues until the user types 'exit'.

