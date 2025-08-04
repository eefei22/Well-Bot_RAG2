from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline

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
location = "Malaysia"

messages = [
    ChatMessage.from_system(
        "do not ever use emojis"
        "Use a friendly and empathetic tone in all replies."
    ),
    ChatMessage.from_user(input("Your Message: "))
]

result = pipe.run(
    data={
        "prompt_builder": {
            "template_variables": {"location": location},
            "template": messages
        }
    }
)

reply = result["llm"]["replies"][0].text
meta = result["llm"]["replies"][0].meta

# print(f"\nLLM Reply:\n{reply}\n")
# print("Metadata:")
# print(meta)
