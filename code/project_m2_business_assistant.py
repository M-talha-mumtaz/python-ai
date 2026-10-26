"""Run a business assistant that answers questions and manages approved orders."""

import json

import httpx
import ollama
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import ValidationError

MODEL_NAME = "qwen2.5:3b"
MAX_STEPS = 5
MAX_MEMORY_MESSAGES = 8

ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "is_order": {"type": "boolean"},
        "customer": {"type": "string"},
        "address": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["item", "quantity"],
            },
        },
    },
    "required": ["is_order", "customer", "address", "items"],
}


def load_json(file_name: str, default_value):
    """Load JSON or return a default for missing or damaged data."""
    try:
        with open(file_name, "r", encoding="utf-8") as input_file:
            return json.load(input_file)
    except FileNotFoundError:
        if file_name == "business.json":
            raise SystemExit(
                "business.json is missing. Create it in the code folder."
            )
        print(f"Warning: {file_name} is missing; starting fresh.")
        return default_value
    except (json.JSONDecodeError, OSError):
        print(f"Warning: {file_name} is damaged; starting fresh.")
        return default_value


def save_json(file_name: str, data) -> None:
    """Save JSON in a readable UTF-8 format."""
    with open(file_name, "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2, ensure_ascii=False)


def log_error(error_text: str) -> None:
    """Append a technical error to the private local error log."""
    with open("errors.log", "a", encoding="utf-8") as error_file:
        error_file.write(f"{error_text}\n")


business = load_json("business.json", {})

if not isinstance(business, dict) or not isinstance(business.get("prices"), dict):
    raise SystemExit("business.json must contain a prices dictionary.")


def normalize_item(item_name: str) -> str:
    """Normalize an item name and accept a matching simple plural."""
    normalized = item_name.strip().lower()

    # Match "pens" to "pen" only when the singular is on the menu.
    if normalized.endswith("s") and normalized[:-1] in business["prices"]:
        normalized = normalized[:-1]

    return normalized


def calculate_total(items: list) -> int:
    """Calculate the item subtotal using the verified price list."""
    subtotal = 0

    for item in items:
        name = normalize_item(item.get("item", ""))
        quantity = item.get("quantity", 0)
        price = business["prices"].get(name)

        if price is not None and price > 0 and quantity > 0:
            subtotal += price * quantity

    return subtotal


def calculate_delivery(subtotal: int) -> int:
    """Calculate delivery from the configured fee and free-delivery limit."""
    fee = business.get("delivery_fee", 200)
    free_limit = business.get("free_delivery_limit", 3000)

    if subtotal >= free_limit:
        return 0
    return fee


# Check Python price math without spending tokens on an AI call.
priced_items = [
    (name, price)
    for name, price in business["prices"].items()
    if isinstance(price, int) and price > 0
]
if priced_items:
    test_item, test_price = priced_items[0]
    assert calculate_total([{"item": test_item, "quantity": 2}]) == test_price * 2
assert calculate_total([{"item": "unknown item", "quantity": 2}]) == 0
assert calculate_delivery(1250) == business.get("delivery_fee", 200)


orders = load_json("orders.json", [])
if not isinstance(orders, list):
    print("Warning: orders.json has the wrong format; starting fresh.")
    orders = []

orders = [order for order in orders if isinstance(order, dict)]
orders_changed = False

# Migrate records from earlier exercises so the order list has consistent fields.
for number, order in enumerate(orders, start=101):
    if not order.get("id"):
        order["id"] = f"A{number}"
        orders_changed = True
    if not order.get("status"):
        order["status"] = "received"
        orders_changed = True

    old_items = order.get("items", [])
    items_are_verifiable = (
        isinstance(old_items, list)
        and len(old_items) > 0
        and all(
            isinstance(item, dict)
            and normalize_item(item.get("item", "")) in business["prices"]
            and isinstance(item.get("quantity"), int)
            and item.get("quantity") > 0
            for item in old_items
        )
    )

    # Correct old totals only when every saved item can be priced from business.json.
    if items_are_verifiable and (
        "subtotal" not in order or "delivery" not in order
    ):
        subtotal = calculate_total(old_items)
        delivery = calculate_delivery(subtotal)
        order["subtotal"] = subtotal
        order["delivery"] = delivery
        order["total"] = subtotal + delivery
        orders_changed = True

if orders_changed:
    save_json("orders.json", orders)
    print("Updated older order records with IDs, statuses and verified totals.")


transcript = load_json("transcript.json", [])
if not isinstance(transcript, list):
    print("Warning: transcript.json has the wrong format; starting fresh.")
    transcript = []

# Keep only plain dictionaries; model/tool objects are never saved to JSON.
transcript = [
    entry for entry in transcript
    if isinstance(entry, dict)
    and entry.get("role") in ("user", "assistant")
    and isinstance(entry.get("content"), str)
]


def save_transcript() -> None:
    """Save plain user and assistant messages to transcript.json."""
    save_json("transcript.json", transcript)


def next_order_id() -> str:
    """Return the first unused order ID."""
    existing_ids = {order.get("id") for order in orders}
    order_number = 101

    while f"A{order_number}" in existing_ids:
        order_number += 1

    return f"A{order_number}"


tool_usage = {
    "get_price": 0,
    "get_info": 0,
    "order_status": 0,
    "place_order": 0,
}

questions = 0
answered = 0
error_count = 0
whatsapp_imports = 0
orders_placed = 0
current_request = ""


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Read a product price from the business data.

    Args:
        item: The product name to look up.
    """
    item_name = normalize_item(item)
    price = business["prices"].get(item_name)

    if price is None:
        return f"Sorry, {item_name} is not on the menu."
    if price == 0:
        return f"{item_name.title()} is coming soon."
    return f"{item_name.title()} costs {price:,} PKR."


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Read business information such as hours, city or delivery.

    Args:
        topic: The business fact to look up.
    """
    fact_key = topic.strip().lower()
    fact_value = business.get(fact_key)

    if fact_value is None:
        return f"I do not have verified information about {fact_key}."
    return f"{fact_key}: {fact_value}"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of a saved order.

    Args:
        order_id: The order ID, for example A101.
    """
    requested_id = order_id.strip().upper()

    for order in orders:
        if str(order.get("id", "")).upper() == requested_id:
            return (
                f"Order {requested_id} for {order.get('customer', 'unknown')} "
                f"is {order.get('status', 'unknown')}, "
                f"total {order.get('total', 0):,} PKR."
            )

    return f"I could not find order {requested_id}."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Ask for approval, calculate and save a new order.

    Args:
        item: A product from the business price list.
        quantity: A positive whole number of items.
        customer: The customer's name from the conversation.
    """
    global orders_placed

    request_text = current_request.lower()

    # Never turn a request to change an order into a second new order.
    if any(word in request_text for word in ("update", "change", "modify", "cancel")):
        return "Order changes are not supported yet. No new order was created."

    item_name = normalize_item(item)
    customer_name = customer.strip().title()
    price = business["prices"].get(item_name)

    if price is None:
        return f"Cannot place order: {item_name} is not on the menu."
    if price == 0:
        return f"Cannot place order: {item_name} is coming soon."
    if quantity <= 0:
        return "Cannot place order: quantity must be positive."
    if customer_name.lower() in ("", "customer", "unknown", "n/a"):
        return "Please ask the customer for their real name before ordering."

    items = [{"item": item_name, "quantity": quantity}]
    subtotal = calculate_total(items)
    delivery = calculate_delivery(subtotal)
    total = subtotal + delivery

    # Ask before saving, showing the complete Python-calculated amount.
    approval = input(
        f"[approve] {quantity} x {item_name} for {customer_name}: "
        f"subtotal {subtotal:,} PKR + delivery {delivery:,} PKR "
        f"= {total:,} PKR. Place it? (yes/no) "
    ).strip().lower()

    if approval != "yes":
        return "Order not placed; approval was not given."

    order_id = next_order_id()
    orders.append({
        "id": order_id,
        "customer": customer_name,
        "items": items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "status": "received",
    })
    save_json("orders.json", orders)
    orders_placed += 1

    return (
        f"Order {order_id} placed: subtotal {subtotal:,} PKR, "
        f"delivery {delivery:,} PKR, total {total:,} PKR."
    )


TOOLS = {
    "get_price": get_price,
    "get_info": get_info,
    "order_status": order_status,
    "place_order": place_order,
}

system_message = f"""
You are the assistant for {business.get("name", "this business")}.
Verified business facts:
{json.dumps(business, ensure_ascii=False)}

Use get_price for prices, get_info for business details, and order_status
for order status. Use place_order only for a new order when the customer
has given an item, quantity and real name. It asks for approval.
Never guess products, prices, delivery fees, delivery times or order statuses.
Use the exact total returned by place_order. Never recalculate an order total.
Never say an order is placed unless the tool confirms it.
Never call place_order to update, change, modify or cancel an existing order.
If asked to change an order, say that changes are not supported yet.
"""

try:
    precise_model = init_chat_model(
        MODEL_NAME,
        model_provider="ollama",
        temperature=0.2,
    )
    agent = precise_model.bind_tools(list(TOOLS.values()))

    extractor = init_chat_model(
        MODEL_NAME,
        model_provider="ollama",
        temperature=0,
        format=ORDER_SCHEMA,
    )
except (httpx.ConnectError, ollama.ResponseError) as error:
    log_error(f"Model setup error: {error}")
    raise SystemExit("Something went wrong with the model. Check errors.log.")


def import_whatsapp_order(raw_message: str) -> None:
    """Extract, validate, total and optionally save a WhatsApp order."""
    global whatsapp_imports, error_count, orders_placed

    whatsapp_imports += 1

    try:
        response = extractor.invoke([
            (
                "system",
                "Extract order details from the message. Do not invent anything. "
                "If it is not an order, set is_order to false. Include requested "
                "off-menu products so the program can flag them. Use an empty "
                "string when the name or address is missing.",
            ),
            ("human", raw_message),
        ])
        extracted = json.loads(response.text)

    except json.JSONDecodeError as error:
        print("CHECK: extractor returned invalid JSON; order not saved.")
        log_error(f"Invalid extractor JSON: {error}")
        error_count += 1
        return
    except httpx.ConnectError as error:
        print("Assistant: Ollama is offline. Open Ollama and try again.")
        log_error(f"Connection error during import: {error}")
        error_count += 1
        return
    except ollama.ResponseError as error:
        print("Assistant: The model could not process the import.")
        log_error(f"Ollama import error: {error}")
        error_count += 1
        return

    if not isinstance(extracted, dict):
        print("CHECK: extractor response was not an object; order not saved.")
        error_count += 1
        return

    if not extracted.get("is_order", False):
        print("Not an order: needs a human reply.")
        return

    customer = extracted.get("customer", "")
    address = extracted.get("address", "")
    raw_items = extracted.get("items", [])

    if not isinstance(customer, str):
        customer = ""
    if not isinstance(address, str):
        address = ""
    if not isinstance(raw_items, list):
        raw_items = []

    customer = customer.strip()
    address = address.strip()
    checks = []

    if not customer:
        checks.append("CHECK: customer name is missing.")
    elif customer.casefold() not in raw_message.casefold():
        checks.append(f"CHECK: customer '{customer}' is not in the message.")
        customer = ""

    valid_items = []

    for extracted_item in raw_items:
        if not isinstance(extracted_item, dict):
            checks.append("CHECK: malformed item entry.")
            continue

        item_name = normalize_item(extracted_item.get("item", ""))
        quantity = extracted_item.get("quantity", 0)
        price = business["prices"].get(item_name)

        if price is None:
            checks.append(f"CHECK: '{item_name}' is not on the menu.")
            continue
        if price == 0:
            checks.append(f"CHECK: '{item_name}' is coming soon.")
            continue
        if type(quantity) is not int or quantity <= 0:
            checks.append(f"CHECK: invalid quantity for '{item_name}'.")
            continue

        valid_items.append({"item": item_name, "quantity": quantity})

    if not valid_items:
        print("No valid menu items to save.")

    subtotal = calculate_total(valid_items)
    delivery = calculate_delivery(subtotal) if valid_items else 0
    total = subtotal + delivery

    for item in valid_items:
        item_total = calculate_total([item])
        print(f"  {item['quantity']} x {item['item']} = {item_total:,} PKR")

    print(f"  Customer: {customer or 'not confirmed'}")
    print(f"  Address: {address or 'not provided'}")
    print(f"  Subtotal: {subtotal:,} PKR")
    print(f"  Delivery: {delivery:,} PKR")
    print(f"  Total: {total:,} PKR")

    for check in checks:
        print(check)

    if not valid_items or not customer:
        print("Order not saved until valid items and customer name are confirmed.")
        return

    # A pasted order is saved only after explicit approval.
    approval = input(
        f"[approve] Save this order? Total {total:,} PKR (yes/no) "
    ).strip().lower()

    if approval != "yes":
        print("Not saved.")
        return

    order_id = next_order_id()
    orders.append({
        "id": order_id,
        "customer": customer,
        "address": address,
        "items": valid_items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "status": "received",
    })
    save_json("orders.json", orders)
    orders_placed += 1
    print(f"Saved order {order_id}.")


def save_chat_turn(user_text: str, assistant_text: str) -> None:
    """Add one exchange to the transcript and save it."""
    transcript.append({"role": "user", "content": user_text})
    transcript.append({"role": "assistant", "content": assistant_text})
    del transcript[:-MAX_MEMORY_MESSAGES]
    save_transcript()


print("============================================================")
print(f"   {business.get('name', 'Business')} AI Business Assistant")
print("============================================================")
print("Ask anything, or use: /import, /orders, /reset, bye")

while True:
    user_input = input("You: ").strip()
    current_request = user_input
    command = user_input.lower()

    if not user_input:
        print("Assistant: Please enter a question or command.")
        continue

    if command == "bye":
        save_transcript()
        print("Assistant: Goodbye! Everything is saved.")
        break

    if command == "/reset":
        # Clear chat while keeping the order records intact.
        transcript = []
        save_transcript()
        print("Assistant: Chat cleared. Orders are still saved.")
        continue

    if command == "/orders":
        if not orders:
            print("No orders are saved yet.")
        else:
            for number, order in enumerate(orders, start=1):
                print(
                    f"  {number}. {order.get('id', '?')} | "
                    f"{order.get('customer', 'Unknown')} | "
                    f"{order.get('total', 0):,} PKR | "
                    f"{order.get('status', 'unknown')}"
                )
        continue

    if command == "/import":
        pasted_message = input("Paste the WhatsApp message: ").strip()
        if pasted_message:
            import_whatsapp_order(pasted_message)
        else:
            print("No message entered.")
        continue

    # Refuse order changes directly so the model cannot create a second order.
    if "order" in command and any(
        word in command for word in ("update", "change", "modify", "cancel")
    ):
        answer = (
            "Order changes are not supported yet. "
            "No new order was created."
        )
        print(f"Assistant: {answer}")
        save_chat_turn(user_input, answer)
        answered += 1
        continue

    # Answer delivery-time questions from the owner's data, not AI guesses.
    if "when" in command and any(
        word in command for word in ("get", "arrive", "deliver", "receive")
    ):
        delivery_time = business.get("delivery_time", "2–5 working days")
        answer = f"Delivery takes {delivery_time}."
        print(f"Assistant: {answer}")
        save_chat_turn(user_input, answer)
        answered += 1
        continue

    questions += 1
    working_messages = [
        {"role": "system", "content": system_message},
        *[
            HumanMessage(content=entry["content"])
            if entry["role"] == "user"
            else {"role": "assistant", "content": entry["content"]}
            for entry in transcript[-MAX_MEMORY_MESSAGES:]
        ],
        HumanMessage(content=user_input),
    ]

    answer = ""
    action_response = None

    try:
        for step in range(MAX_STEPS):
            response = agent.invoke(working_messages)
            working_messages.append(response)

            if not response.tool_calls:
                answer = str(response.content)
                print(f"Assistant: {answer}")
                answered += 1
                break

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]

                if tool_name not in TOOLS:
                    tool_result = f"Unknown tool: {tool_name}"
                else:
                    try:
                        tool_result = TOOLS[tool_name].invoke(tool_args)
                        tool_usage[tool_name] += 1
                    except ValidationError as error:
                        tool_result = f"Invalid tool arguments: {error}"

                print(f"  [tool] {tool_name}({tool_args}) -> {tool_result}")
                working_messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call_id,
                    )
                )

                # Print the exact saved-order result; do not ask the model to rewrite it.
                if tool_name == "place_order":
                    action_response = str(tool_result)
                    break

            if action_response is not None:
                answer = action_response
                print(f"Assistant: {answer}")
                answered += 1
                break
        else:
            # Stop after a fixed number of calls to prevent an endless agent loop.
            answer = "I could not complete that request within the step limit."
            print(f"Assistant: {answer}")

    except httpx.ConnectError as error:
        answer = "Ollama is offline. Open the Ollama app and try again."
        print(f"Assistant: {answer}")
        log_error(f"Connection error: {error}")
        error_count += 1
    except ollama.ResponseError as error:
        answer = "Something went wrong with the model. Please try again."
        print(f"Assistant: {answer}")
        log_error(f"Ollama response error: {error}")
        error_count += 1
    except ValidationError as error:
        answer = "I could not process that request. Please rephrase it."
        print(f"Assistant: {answer}")
        log_error(f"Tool validation error: {error}")
        error_count += 1

    save_chat_turn(user_input, answer)

print("============================================================")
print("Session report")
print(f"Questions: {questions} | Answered: {answered} | Errors: {error_count}")
print(f"WhatsApp imports: {whatsapp_imports} | Orders placed: {orders_placed}")
print(f"Orders on file: {len(orders)}")
print("Tool calls:")
for tool_name, count in tool_usage.items():
    print(f"  {tool_name}: {count}")
print("============================================================")