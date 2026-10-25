"""Choose an AI model by task type and estimate an example cost."""

# Normalize input so values like " Code " match our rules.
task_type = input("Task (code / private / chat): ").strip().lower()
estimated_tokens = int(input("Estimated tokens: "))

# Keep private requests local so their data stays on the user's computer.
if task_type == "private":
    model_name = "qwen2.5:3b (local, Ollama)"
    price_per_1k_tokens = 0.0
elif task_type == "code":
    model_name = "Example strong cloud model"
    price_per_1k_tokens = 0.8
else:
    model_name = "Example cheap cloud model"
    price_per_1k_tokens = 0.2

estimated_cost = (estimated_tokens / 1000) * price_per_1k_tokens

# Flag long requests so the user can consider reducing their size.
if estimated_tokens > 4000:
    print("Warning: long request, consider shortening it.")
else:
    print("Length is fine.")

print(f"Chosen model: {model_name}")
print(f"Estimated cost: {estimated_cost:.2f} PKR")
print("Cloud model names and prices are examples.")