"""Build an AI prompt from a user's business details."""

user_name = input("Your name: ")
business_type = input("Business type: ")
business_problem = input("Biggest problem: ")

# Personalize the greeting so the user knows the tool is responding to them.
print(f"\nWelcome, {user_name}!")

# Include the business context so the AI can suggest relevant solutions.
prompt = (
    f"Suggest 3 AI solutions for a {business_type} "
    f"that struggles with {business_problem}."
)

print("--- Your AI Prompt ---")
print(prompt)