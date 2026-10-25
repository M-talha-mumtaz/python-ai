"""Display an AI model profile and estimate a chat's example cost."""

model_name = "Example Cloud Model"
context_window = 32000
price_per_1k_tokens = 0.5
runs_locally = False

print("--- AI Model Profile Card ---")
print(f"Model: {model_name} {type(model_name)}")
print(f"Context window: {context_window} tokens {type(context_window)}")
print(f"Example price per 1K tokens: {price_per_1k_tokens} PKR {type(price_per_1k_tokens)}")
print(f"Runs locally: {runs_locally} {type(runs_locally)}")

# Convert the user's text to a whole number so we can calculate the cost.
tokens_per_chat = int(input("Tokens per chat: "))

# Divide by 1000 because the example price is for every thousand tokens.
estimated_cost = round(
    (tokens_per_chat / 1000) * price_per_1k_tokens, 2
)

print(f"Estimated cost: {estimated_cost:.2f} PKR")
print("The model details and price above are examples.")