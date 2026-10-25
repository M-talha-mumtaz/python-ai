"""Chat using business facts, selectable styles and direct price lookups."""

from langchain.chat_models import init_chat_model

config = {
    "model": "qwen2.5:3b",
    "temperature": 0.2,
    "memory_size": 8,
}

facts = {
    "business_name": "Talha Stationery",
    "business_type": "stationery shop",
    "hours": "Monday to Saturday, 9 am to 6 pm",
    "delivery": "200 PKR; free from 3,000 PKR after discount",
    "payment_methods": "Bank transfer and cash on delivery",
    "prices": {
        "notebook": 250,
        "pen": 50,
        "backpack": 1500,
    },
}

personas = {
    "friendly": "Warm and cheerful, using simple words.",
    "formal": "Professional and polite, using complete sentences.",
    "sales": (
        "Enthusiastic and helpful. Suggest one relevant extra item "
        "from the price list without pressuring the customer."
    ),
}

style = personas["friendly"]

# Keep factual instructions in the system message to reduce invented details.
system_message = f"""
You are the assistant for {facts["business_name"]}.
Speaking style: {style}
Only use these facts for claims about the business:
{facts}
Prices are in PKR.
If information is missing, say you do not know and suggest contacting support.
Do not invent products, discounts, policies or promises.
Answer in 3 short lines.
"""

messages = [{"role": "system", "content": system_message}]

llm = init_chat_model(
    config["model"],
    model_provider="ollama",
    temperature=config["temperature"],
)

print("Bot ready.")
print("Commands: /persona friendly|formal|sales, /price <item>, bye")

while True:
    user_input = input("You: ").strip()
    command = user_input.lower()

    if command == "bye":
        print("Bot: Goodbye!")
        break

    elif command == "":
        print("Bot: Please type a question.")

    elif command == "/persona":
        print("Bot: Try /persona friendly, /persona formal or /persona sales.")

    elif command.startswith("/persona "):
        persona_name = command[len("/persona "):].strip()

        # An unknown persona falls back to friendly instead of causing an error.
        style = personas.get(persona_name, personas["friendly"])

        messages[0]["content"] = f"""
You are the assistant for {facts["business_name"]}.
Speaking style: {style}
Only use these facts for claims about the business:
{facts}
Prices are in PKR.
If information is missing, say you do not know and suggest contacting support.
Do not invent products, discounts, policies or promises.
Answer in 3 short lines.
"""
        print(f"Bot: Style changed to: {style}")

    elif command == "/price":
        print("Bot: Try /price notebook, /price pen or /price backpack.")

    elif command.startswith("/price "):
        item = command[len("/price "):].strip()
        price = facts["prices"].get(item)

        # Answer exact prices directly so the model cannot change the amount.
        if price is None:
            print(f"Bot: Sorry, {item} is not on our menu.")
        else:
            print(f"Bot: {item.title()} costs {price:,} PKR.")

    else:
        messages.append({"role": "user", "content": user_input})

        # Preserve the system instructions while limiting conversation history.
        messages = (
            [messages[0]]
            + messages[1:][-config["memory_size"]:]
        )

        response = llm.invoke(messages)
        print(f"Bot: {response.text}")

        messages.append({
            "role": "assistant",
            "content": response.text,
        })

        messages = (
            [messages[0]]
            + messages[1:][-config["memory_size"]:]
        )