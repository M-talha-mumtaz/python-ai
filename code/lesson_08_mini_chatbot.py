"""Answer common customer questions for an online shop."""

business_name = "Example Online Shop"

print(f"{business_name} Bot: Welcome!")
print("Ask about hours, delivery, payment or returns. Type 'bye' to exit.")

# Ask once so the customer does not repeat their name for every message.
customer_name = input("Your name: ").strip().title()

# Initialize counters before the loop so they accumulate across messages.
message_count = 0
unanswered_count = 0

while True:
    message = input(f"{customer_name}: ").strip().lower()

    if message == "":
        print("Bot: Please type a question.")
    else:
        message_count += 1

        # Prioritize complaints even when the message also mentions another topic.
        if (
            "refund" in message
            or "complaint" in message
            or "order is late" in message
        ):
            print(
                f"Bot: {customer_name}, please contact our support team "
                "for help with this issue."
            )
        elif message == "bye":
            print(f"Bot: Goodbye, {customer_name}!")
            break

        # Exact greeting checks avoid matching 'hi' inside words like 'which'.
        elif message == "hi" or message == "hello":
            print(f"Bot: Hello, {customer_name}! How can I help?")
        elif "hours" in message or "timings" in message:
            print("Bot: Support is available Monday–Saturday, 9 am–6 pm.")
        elif "delivery" in message or "shipping" in message:
            print("Bot: Delivery normally takes 3–5 working days.")
        elif "payment" in message or "pay" in message:
            print("Bot: We accept bank transfers and cash on delivery.")
        elif "return" in message:
            print("Bot: Contact support to check return eligibility.")
        else:
            unanswered_count += 1

            # Prepare a prompt for questions that our fixed rules cannot answer.
            prompt = f"""
You are the customer support assistant for {business_name}.
Answer {customer_name} in 2 short lines.
Do not invent business policies. Ask the customer to contact support
if the answer needs information you do not have.
Question: {message}
"""
            print("Bot: I cannot answer that yet. Here is a prompt for AI:")
            print(prompt)

print("========================================")
print(
    f"Chat summary: {message_count} messages, "
    f"{unanswered_count} unanswered."
)