"""Create marketing content and answer questions for Talha Stationery."""

from langchain.chat_models import init_chat_model

config = {
    "model": "qwen2.5:3b",
    "max_messages": 8,
}

facts = {
    "name": "Talha Stationery",
    "city": "Lahore",
    "hours": "Monday–Saturday, 9 am–6 pm",
    "delivery": "200 PKR; free from 3,000 PKR after discount",
    "payment_methods": "Bank transfer and cash on delivery",
    "prices": {
        "notebook": 250,
        "pen": 50,
        "backpack": 1500,
        "art kit": 0,
    },
}

tones = {
    "fun": "Playful and energetic, using short sentences.",
    "formal": "Professional, clear and polite.",
    "premium": "Elegant and calm, without inventing product features.",
}

# Use different temperatures for factual answers and creative writing.
precise = init_chat_model(
    config["model"],
    model_provider="ollama",
    temperature=0.2,
)

creative = init_chat_model(
    config["model"],
    model_provider="ollama",
    temperature=0.8,
)

# Ground every AI task in the same business information.
system_message = f"""
You are the assistant for {facts["name"]}.
Only use these facts for claims about the business:
{facts}

Prices are in PKR.
A price of 0 means coming soon, not free or currently available.
Do not invent products, features, discounts, policies or promises.
If information is missing, say you do not know.
"""

messages = [{"role": "system", "content": system_message}]

chat_answers = 0
menu_descriptions = 0
posts = 0
price_answers = 0
total_tokens = 0
total_seconds = 0.0

print("==================================================")
print(f"{facts['name']} — AI Content Studio")
print("==================================================")
print("Commands: /menu, /post fun|formal|premium,")
print("          /price <item>, /reset, bye")

while True:
    user_input = input("\nYou: ").strip()
    command = user_input.lower()

    if command == "":
        print("Studio: Please enter a command or question.")

    elif command == "bye":
        print("Studio: Goodbye!")
        break

    elif command == "/reset":
        # Preserve the business facts when clearing conversation memory.
        messages = [messages[0]]
        print("Studio: Chat memory cleared.")

    elif command == "/menu":
        results = []

        for name, price in facts["prices"].items():
            # Skip coming-soon items before making any AI call.
            if price == 0:
                print(f"Studio: Skipping {name} (coming soon)")
                continue

            print(f"Studio: Writing description for {name}...")

            response = creative.invoke([
                ("system", system_message),
                (
                    "human",
                    f"Write one sentence describing {name}, "
                    f"priced at {price} PKR. "
                    "Use only known facts; do not invent specifications.",
                ),
            ])

            results.append({
                "item": name,
                "price": price,
                "text": response.text,
            })

            menu_descriptions += 1
            total_tokens += response.usage_metadata["total_tokens"]
            total_seconds += (
                response.response_metadata["total_duration"]
                / 1_000_000_000
            )

        print("--------------------------------------------------")

        for number, product in enumerate(results, start=1):
            print(
                f"{number}. {product['item'].title()} "
                f"({product['price']:,} PKR)"
            )
            print(f"   {product['text']}")

    elif command == "/post" or command.startswith("/post "):
        tone_name = command[len("/post"):].strip()

        # Unknown or missing tones use a default instead of raising an error.
        tone = tones.get(tone_name, tones["fun"])

        print(f"Studio ({tone}):")
        full_response = None

        for chunk in creative.stream([
            ("system", system_message),
            (
                "human",
                f"Write a short social media post for this business. "
                f"Tone: {tone} "
                "End with one call to action. "
                "Do not advertise coming-soon items as available.",
            ),
        ]):
            print(chunk.text, end="", flush=True)

            # Combine chunks to retain the complete response and usage metadata.
            if full_response is None:
                full_response = chunk
            else:
                full_response += chunk

        print()

        if full_response is not None:
            posts += 1
            total_tokens += full_response.usage_metadata["total_tokens"]
            total_seconds += (
                full_response.response_metadata["total_duration"]
                / 1_000_000_000
            )

    elif command == "/price":
        print("Studio: Enter an item, for example /price notebook.")

    elif command.startswith("/price "):
        item = command[len("/price "):].strip()

        # Direct lookup gives exact prices without spending AI tokens.
        price = facts["prices"].get(item)
        price_answers += 1

        if price is None:
            print(f"Studio: Sorry, {item} is not on our menu.")
        elif price == 0:
            print(f"Studio: {item.title()} is coming soon.")
        else:
            print(f"Studio: {item.title()} costs {price:,} PKR.")

    else:
        messages.append({"role": "user", "content": user_input})

        # Limit chat history while keeping the business instructions.
        messages = (
            [messages[0]]
            + messages[1:][-config["max_messages"]:]
        )

        response = precise.invoke(messages)
        print(f"Studio: {response.text}")

        messages.append({
            "role": "assistant",
            "content": response.text,
        })

        messages = (
            [messages[0]]
            + messages[1:][-config["max_messages"]:]
        )

        chat_answers += 1
        total_tokens += response.usage_metadata["total_tokens"]
        total_seconds += (
            response.response_metadata["total_duration"]
            / 1_000_000_000
        )

        input_tokens = response.usage_metadata["input_tokens"]
        print(
            f"       (memory: {len(messages)} messages, "
            f"{input_tokens} tokens sent)"
        )

print("==================================================")
print("Session report")
print(f"Chat answers: {chat_answers}")
print(f"Menu descriptions: {menu_descriptions}")
print(f"Posts: {posts}")
print(f"Price answers: {price_answers}")
print(f"Total AI tokens: {total_tokens:,}")
print(f"Total AI seconds: {total_seconds:.1f}")
print("==================================================")