"""Help stationery customers using verified shop tools and approved orders."""

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import ValidationError

PRICES = {
    "notebook": 250,
    "pen": 50,
    "backpack": 1500,
}

ORDER_STATUS = {
    "A102": "Out for delivery",
    "A103": "Being prepared",
}

next_order_number = 104
MAX_STEPS = 5


def normalize_item(item: str) -> str:
    """Match an item name to the shop menu, including simple plurals."""
    item_name = item.strip().lower()

    # Match simple plurals such as "pens" to their singular menu names.
    if item_name.endswith("s") and item_name[:-1] in PRICES:
        item_name = item_name[:-1]

    return item_name


@tool(parse_docstring=True)
def list_products() -> str:
    """List products the stationery shop sells or plans to sell."""
    product_lines = []

    for item, price in PRICES.items():
        if price == 0:
            product_lines.append(f"{item}: coming soon")
        else:
            product_lines.append(f"{item}: {price:,} PKR")

    return "Shop menu: " + "; ".join(product_lines)


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Look up the price of a stationery item.

    Args:
        item: The product name to look up.
    """
    item_name = normalize_item(item)
    price = PRICES.get(item_name)

    if price is None:
        return f"Sorry, {item_name} is not on the menu."
    if price == 0:
        return f"{item_name.title()} is coming soon."

    return f"{item_name.title()} costs {price:,} PKR."


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of an existing sample order.

    Args:
        order_id: The order reference, such as A102.
    """
    normalized_order_id = order_id.strip().upper()
    status = ORDER_STATUS.get(normalized_order_id)

    if status is None:
        return f"I could not find order {normalized_order_id}."

    return f"Order {normalized_order_id} is {status.lower()}."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Ask the customer to approve, then place a stationery order.

    Args:
        item: A product name that appears on the shop menu.
        quantity: The number of units requested.
        customer: The customer's name, as provided in the conversation.
    """
    global next_order_number

    item_name = normalize_item(item)
    customer_name = customer.strip().title()
    price = PRICES.get(item_name)

    if price is None:
        return f"Cannot place the order: {item_name} is not on the menu."
    if price == 0:
        return f"Cannot place the order: {item_name} is coming soon."
    if quantity <= 0:
        return "Cannot place the order: quantity must be greater than zero."
    if not customer_name:
        return "Cannot place the order: please ask for the customer's name."

    total = price * quantity

    # Require approval before creating the sample order.
    approval = input(
        f"[approve] {quantity} x {item_name} for {customer_name} "
        f"= {total:,} PKR. Place it? (yes/no) "
    ).strip().lower()

    if approval != "yes":
        return "Order not placed; approval was not given."

    order_id = f"A{next_order_number}"
    next_order_number += 1
    ORDER_STATUS[order_id] = "Being prepared"

    return (
        f"Order {order_id} placed: {quantity} x {item_name}, "
        f"total {total:,} PKR."
    )


TOOLS = {
    "list_products": list_products,
    "get_price": get_price,
    "order_status": order_status,
    "place_order": place_order,
}

llm = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)
agent = llm.bind_tools(list(TOOLS.values()))

messages = [
    {
        "role": "system",
        "content": (
            "You are the assistant for Talha Stationery. "
            "Use list_products when asked what the shop sells. "
            "Use get_price to check a named product's availability or price. "
            "Use order_status to check an order reference. "
            "Use place_order only when the customer has provided the item, "
            "quantity, and their name. The tool asks for approval. "
            "Never claim an order is placed unless the tool confirms it. "
            "Only claim products and prices returned by tools. "
            "Never invent products, stock, prices, names, or order details. "
            "Ask the customer for missing order information."
        ),
    }
]

print("Talha Stationery Agent: ask about products, prices, or orders.")
print("Type 'bye' to exit.")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        print("Agent: Goodbye!")
        break

    if user_input == "":
        print("Agent: Please enter a question.")
        continue

    messages.append(HumanMessage(content=user_input))

    for step in range(MAX_STEPS):
        response = agent.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            print(f"Agent: {response.content}")
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
                except ValidationError as error:
                    tool_result = f"Invalid tool arguments: {error}"

            print(f"  [tool] {tool_name}({tool_args}) -> {tool_result}")
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id,
                )
            )

    else:
        # Stop after a fixed number of steps to prevent endless tool calls.
        print("Agent: I could not finish that request within the step limit.")