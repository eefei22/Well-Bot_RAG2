from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline
from retriever import retrieve_top_document

# Initialize once outside the loop
prompt_builder = ChatPromptBuilder()
generator = OllamaChatGenerator(
    model="deepseek-r1",
    url="http://localhost:11434",
    streaming_callback=lambda chunk: print(chunk.content, end="", flush=True),
    generation_kwargs={"temperature": 0.9},
)

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)
pipe.connect("prompt_builder.prompt", "llm.messages")

# Conversation loop
while True:
    user_query = input("\nYou: ")
    if user_query.lower() == "exit":
        print("Exiting chat.")
        break

    context = retrieve_top_document(user_query)

    # Build prompt with context and history
    messages = [
        ChatMessage.from_system(
            "Response MUST not exceed 200 words"
            f"Do not ever use emojis. "
            f"Use a friendly and empathetic tone in all replies."
            f"Here is extra context: {context}"),
        ChatMessage.from_user(user_query),
    ]

    result = pipe.run(
        data={"prompt_builder": {"template": messages}}
    )

    reply = result["llm"]["replies"][0].text
    print("\nWell-Bot:", reply)

