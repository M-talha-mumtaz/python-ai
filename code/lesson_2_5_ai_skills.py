"""Provide reusable AI skills for a stationery shop."""

from langchain.chat_models import init_chat_model

# Create models once so each skill can reuse the right settings.
precise_model = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)
creative_model = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.8,
)

usage = {
    "summarize": 0,
    "translate": 0,
    "reply": 0,
}


def ask_ai(prompt: str, system: str = "You are a helpful assistant.", creative_mode: bool = False) -> str:
    """Send a prompt to the selected model and return its text."""
    selected_model = precise_model

    if creative_mode:
        selected_model = creative_model

    response = selected_model.invoke([
        ("system", system),
        ("human", prompt),
    ])
    return response.text


def summarize(text: str) -> str:
    """Summarize a customer message in one short sentence."""
    system = (
        "You help a stationery shop. Summarize the customer's message "
        "in one clear sentence without adding facts."
    )
    return ask_ai(f"Summarize this message: {text}", system=system)


def translate(text: str, language: str = "Urdu") -> str:
    """Translate a message into the requested language."""
    system = (
        "You are a careful translator. Translate the text faithfully. "
        "Do not add explanations."
    )
    return ask_ai(
        f"Translate this text into {language}: {text}",
        system=system,
    )


def reply_to_review(review: str) -> str:
    """Write a polite reply to a shop review."""
    system = (
        "You write warm, professional replies for a stationery shop. "
        "Do not invent actions, discounts or promises."
    )
    return ask_ai(
        f"Write a short reply to this customer review: {review}",
        system=system,
        creative_mode=True,
    )


def estimate_tokens(text: str) -> int:
    """Estimate tokens using roughly four characters per token."""
    return round(len(text) / 4)


# Check this simple helper without making an AI call.
assert estimate_tokens("") == 0
assert estimate_tokens("12345678") == 2

print("Talha Stationery AI Toolkit.")
print("Commands: /summarize, /translate, /reply, bye")

while True:
    command = input("\nCommand: ").strip().lower()

    if command == "bye":
        print("Goodbye!")
        break

    elif command == "/summarize":
        text = input("Customer message: ").strip()
        answer = summarize(text)
        usage["summarize"] += 1
        print(f"AI: {answer}")

    elif command == "/translate":
        text = input("Text to translate: ").strip()
        language = input("Language (Enter for Urdu): ").strip()

        # Use the default language when the user presses Enter.
        if language == "":
            answer = translate(text)
        else:
            answer = translate(text, language)

        usage["translate"] += 1
        print(f"AI: {answer}")

    elif command == "/reply":
        review = input("Customer review: ").strip()
        answer = reply_to_review(review)
        usage["reply"] += 1
        print(f"AI: {answer}")
        print(f"    (review was about {estimate_tokens(review)} tokens)")

    else:
        print("Unknown command. Try /summarize, /translate, /reply or bye.")

print("\nSkills used today:")
for skill_name, times_used in usage.items():
    print(f"  {skill_name}: {times_used}")