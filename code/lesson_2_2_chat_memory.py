"""Run an AI tutor with limited conversation memory and reset commands."""

from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)

# Keep the tutor's instructions separate so resetting memory preserves them.
messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly personal tutor. "
            "Answer in 3 short lines using clear language. "
            "Use information from the conversation when relevant. "
            "If you do not know something, say so."
        ),
    }
]

print("Tutor: Ask me anything. Commands: /reset, /count, bye")

while True:
    user_input = input("You: ").strip()
    command = user_input.lower()

    if command == "bye":
        print("Tutor: Goodbye!")
        break
    elif command == "/reset":
        messages = [messages[0]]
        print("Tutor: Memory cleared.")
    elif command == "/count":
        print(f"Tutor: {len(messages)} messages in memory.")
    elif user_input == "":
        print("Tutor: Please type a question.")
    else:
        messages.append({"role": "user", "content": user_input})

        # Limit the history sent to the model to control input token usage.
        messages = [messages[0]] + messages[1:][-8:]

        response = llm.invoke(messages)
        print(f"Tutor: {response.text}")

        # Store both sides so the model can follow the conversation.
        messages.append({"role": "assistant", "content": response.text})

        # Keep stored memory within the same limit after adding the reply.
        messages = [messages[0]] + messages[1:][-8:]

        input_tokens = response.usage_metadata["input_tokens"]
        print(f"       (tokens sent: {input_tokens})")