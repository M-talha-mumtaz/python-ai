"""Clean a user's name and question to build a Python tutor prompt."""

user_name = input("Your name: ").strip().title()

# Remove surrounding spaces and standardize capitalization for readable output.
question = input("Your question: ").strip().capitalize()

character_count = len(question)

# Characters divided by four gives a rough token estimate.
estimated_tokens = round(character_count / 4)

mentions_python = "python" in question.lower()

print("\n========================================")
print(f"Cleaned question: {question}")
print(f"Characters: {character_count}, about {estimated_tokens} tokens")
print(f"Mentions Python: {mentions_python}")
print("========================================")

# Limit the question length to keep the generated prompt short.
prompt = f"""
You are a friendly Python tutor.
Greet {user_name} by name and answer in 3 short lines.
Question: {question[:150]}
"""

print(prompt)