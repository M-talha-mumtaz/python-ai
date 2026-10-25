"""Explain a topic at the student's level using a local AI model."""

from langchain.chat_models import init_chat_model

topic = input("Topic: ").strip()
level = input("Level (beginner or expert): ").strip().lower()

# Set the level and length so the explanation fits the student's needs.
system_message = (
    f"You are a patient tutor teaching a student at {level} level. "
    "Explain the requested topic in 3 short lines. "
    "Use simple language for beginners and technical detail for experts."
)

# Use a local model and a low temperature for more consistent explanations.
llm = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)

response = llm.invoke([
    ("system", system_message),
    ("human", f"Explain this topic: {topic}"),
])

total_tokens = response.usage_metadata["total_tokens"]

# Ollama reports duration in nanoseconds; convert it to seconds.
seconds = response.response_metadata["total_duration"] / 1_000_000_000

print("========================================")
print(response.text)
print("========================================")
print(f"{total_tokens} tokens in {seconds:.1f} seconds")