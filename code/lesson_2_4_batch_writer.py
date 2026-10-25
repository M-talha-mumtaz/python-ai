"""Generate stationery product descriptions and report token usage and time."""

from langchain.chat_models import init_chat_model

products = {
    "notebook": 250,
    "pen": 50,
    "backpack": 1500,
    "pencil case": 350,
    "old stock": 0,
}

# Create the model once so every product uses the same configuration.
llm = init_chat_model(
    "qwen2.5:3b",
    model_provider="ollama",
    temperature=0.2,
)

results = []

# Start totals before the loop so usage accumulates across all AI calls.
total_tokens = 0
total_seconds = 0.0

for name, price in products.items():
    # Skip unpriced products rather than generating descriptions we cannot use.
    if price == 0:
        print(f"Skipping {name} (no price)")
        continue

    print(f"Writing description for {name}...")

    response = llm.invoke([
        (
            "system",
            "You write short product descriptions for a stationery shop. "
            "Write exactly one sentence. "
            "Do not invent brands, materials, sizes, discounts or guarantees.",
        ),
        (
            "human",
            f"Write a description for: {name}. Price: {price} PKR.",
        ),
    ])

    results.append({
        "item": name,
        "price": price,
        "text": response.text,
    })

    total_tokens += response.usage_metadata["total_tokens"]

    # Convert Ollama's nanosecond duration into seconds.
    total_seconds += (
        response.response_metadata["total_duration"] / 1_000_000_000
    )

print("\n==================================================")
print("Talha Stationery — Product Catalogue")
print("==================================================")

for number, product in enumerate(results, start=1):
    print(f"\n{number}. {product['item'].title()} ({product['price']:,} PKR)")
    print(f"   {product['text']}")

print("\n==================================================")
print(
    f"{len(results)} descriptions, "
    f"{total_tokens} tokens, "
    f"{total_seconds:.1f} seconds"
)