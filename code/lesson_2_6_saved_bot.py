"""Answer questions using business facts and saved chat history."""

import json

import httpx
import ollama
from langchain.chat_models import init_chat_model

# Load the owner's facts so they can update business details without editing code.
try:
    with open("faq.json", "r", encoding="utf-8") as faq_file:
        facts = json.load(faq_file)
except FileNotFoundError:
    raise SystemExit("Could not find faq.json. Run this script from the code folder.")

system_message = f"""
You are the assistant for {facts.get("business_name", "this business")}.
Only use these business facts:
{facts}
If you do not know an answer from the facts, say so.
Do not invent prices, hours, delivery rules or promises.
"""

# Keep chat history as plain role/content dictionaries so JSON can save it.
try:
    with open("chat_history.json", "r", encoding="utf-8") as history_file:
        old_messages = json.load(history_file)

    if isinstance(old_messages, list):
        messages = [{"role": "system", "content": system_message}]
        messages.extend(
            message
            for message in old_messages
            if isinstance(message, dict)
            and message.get("role") in ("user", "assistant")
            and isinstance(message.get("content"), str)
        )
        print(f"Loaded {len(messages) - 1} old messages.")
    else:
        messages = [{"role": "system", "content": system_message}]
        print("History file was damaged. Starting a fresh chat.")

except FileNotFoundError:
    messages = [{"role": "system", "content": system_message}]
except (json.JSONDecodeError, OSError):
    messages = [{"role": "system", "content": system_message}]
    print("History file was damaged. Starting a fresh chat.")

llm = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)


def save_history():
    """Save only the conversation, leaving system instructions out of the file."""
    with open("chat_history.json", "w", encoding="utf-8") as history_file:
        json.dump(messages[1:], history_file, indent=2, ensure_ascii=False)


def log_error(error_text: str):
    """Append a technical error to the private local error log."""
    with open("errors.log", "a", encoding="utf-8") as error_file:
        error_file.write(f"{error_text}\n")


print(f"{facts.get('business_name', 'Business')} Bot: Ask me anything.")
print("Commands: /reset, bye")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        save_history()
        print("Bot: Goodbye! Your chat is saved.")
        break

    elif user_input.lower() == "/reset":
        # Preserve the system facts when the customer clears chat memory.
        messages = [{"role": "system", "content": system_message}]
        save_history()
        print("Bot: Memory cleared.")
        continue

    elif user_input == "":
        print("Bot: Please type a question.")
        continue

    messages.append({"role": "user", "content": user_input})

    try:
        response = llm.invoke(messages)
        answer = response.text
        print(f"Bot: {answer}")
        messages.append({"role": "assistant", "content": answer})

    except httpx.ConnectError as error:
        # Give the customer a clear next step instead of a Python traceback.
        print("Bot: I am offline right now. Please open the Ollama app and try again.")
        log_error(f"Connection error: {error}")
        messages.pop()

    except ollama.ResponseError as error:
        print("Bot: I could not get an answer from the model. Please try again.")
        log_error(f"Ollama response error: {error}")
        messages.pop()

    # Save after each turn so a later restart can restore successful exchanges.
    save_history()