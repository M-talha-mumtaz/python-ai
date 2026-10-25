"""Extract and check stationery orders from customer messages."""

import json

from langchain.chat_models import init_chat_model

PRICES = {
    "notebook": 250,
    "pen": 50,
    "backpack": 1500,
}

messages = [
    "Hi, I want 2 notebooks please. Ali, house 12 Gulberg.",
    "Hello! 1 backpack and 3 pens, from Sara in Model Town.",
    "I need 2 notebooks and 1 printer. Bilal, Johar Town.",
    "Hi, are you open today? Fatima, Lahore.",
    "Salam, mujhay 2 printer chahiye. Ahmed, house 8 DHA.",
]

ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "is_order": {"type": "boolean"},
        "customer_name": {"type": "string"},
        "address": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["name", "quantity"],
            },
        },
    },
    "required": ["is_order", "customer_name", "address", "items"],
}

# Ask for structured data so the program can check fields consistently.
extractor = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0,
    format=ORDER_SCHEMA,
)

orders = []
total_order_value = 0
check_count = 0

for message in messages:
    print(f"\nMessage: {message}")

    response = extractor.invoke([
        (
            "system",
            "Extract order information from the customer message. "
            "Return only information stated in the message. "
            "Mark is_order false for general questions or greetings. "
            "Use the menu item name exactly when it is on this menu: "
            "notebook, pen, backpack. "
            "Include unknown requested products so they can be flagged. "
            "Do not invent a customer name or address. "
            "Use an empty string when name or address is missing.",
        ),
        ("human", message),
    ])

    try:
        extracted = json.loads(response.text)
    except json.JSONDecodeError:
        # Skip malformed model output rather than treating it as an order.
        print("  CHECK: AI response was not valid JSON; skipped.")
        check_count += 1
        continue

    if not extracted.get("is_order", False):
        print("  Not an order: needs a human reply.")
        continue

    customer_name = extracted.get("customer_name", "").strip()
    address = extracted.get("address", "").strip()
    extracted_items = extracted.get("items", [])

    # Require evidence for a customer name to catch invented names.
    if not customer_name or customer_name.lower() not in message.lower():
        print("  CHECK: customer name is missing or not in the message.")
        customer_name = ""
        check_count += 1

    order_items = []
    order_total = 0

    for item in extracted_items:
        item_name = item.get("name", "").strip().lower()
        quantity = item.get("quantity", 0)

        if item_name not in PRICES:
            print(f"  CHECK: '{item_name}' is not on the menu.")
            check_count += 1
            continue

        if not isinstance(quantity, int) or quantity <= 0:
            print(f"  CHECK: invalid quantity for '{item_name}'.")
            check_count += 1
            continue

        line_total = PRICES[item_name] * quantity
        order_total += line_total

        order_items.append({
            "name": item_name,
            "quantity": quantity,
            "line_total": line_total,
        })

        print(
            f"  {quantity} x {item_name} = "
            f"{line_total:,} PKR"
        )

    if not order_items:
        print("  No valid menu items to save.")
        continue

    print(
        f"  Customer: {customer_name or 'not confirmed'}, "
        f"Address: {address or 'not provided'}"
    )
    print(f"  Total: {order_total:,} PKR")

    # Calculate from the trusted price list, never from an AI-suggested total.
    orders.append({
        "customer": customer_name,
        "address": address,
        "items": order_items,
        "total": order_total,
    })
    total_order_value += order_total

# Keep order records readable; this file can contain customer data.
with open("orders.json", "w", encoding="utf-8") as orders_file:
    json.dump(orders, orders_file, indent=2, ensure_ascii=False)

print("\n==================================================")
print(
    f"Orders found: {len(orders)} | "
    f"Total value: {total_order_value:,} PKR | "
    f"Checks: {check_count}"
)
print(f"Saved {len(orders)} orders to orders.json")