from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline
from retriever import retrieve_top_document

user_query = input("Your Message: ")
context = retrieve_top_document(user_query)

prompt_builder = ChatPromptBuilder()
generator = OllamaChatGenerator(model="deepseek-r1",
                            url = "http://localhost:11434",
                            streaming_callback=lambda chunk: print(chunk.content, end="", flush=True),
                            generation_kwargs={
                              "temperature": 0.9,
                              })

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)
pipe.connect("prompt_builder.prompt", "llm.messages")

messages = [
    ChatMessage.from_system(
        "Do not ever use emojis"
        "Use a friendly and empathetic tone in all replies."
        "Extra context" + context
    ),
    ChatMessage.from_user(user_query)
]
result = pipe.run(
    data={
        "prompt_builder": {
            "template": messages
        }
    }
)

reply = result["llm"]["replies"][0].text
meta = result["llm"]["replies"][0].meta

# print(f"\nLLM Reply:\n{reply}\n")
# print("Metadata:")
# print(meta)