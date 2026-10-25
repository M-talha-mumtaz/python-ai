"""Answer stationery shop questions, calculate quotes and prepare AI prompts."""

BOT_NAME = "Talha Stationery"
DELIVERY_FEE = 200
FREE_DELIVERY_LIMIT = 3000
CLOUD_PRICE_PER_1K = 0.10  # Example price, not a real provider's rate.

print("==================================================")
print(f"{BOT_NAME}: Your online front desk")
print("Ask a question, type /quote for a price, or bye to exit.")
print("==================================================")

# Ask once so the customer's name stays available throughout the chat.
customer_name = input("Your name: ").strip().title()

message_count = 0
answered_by_rules = 0
unanswered_count = 0
quote_count = 0
total_quoted_value = 0.0
total_ai_cost = 0.0

while True:
    message = input(f"{customer_name}: ").strip().lower()

    if message == "":
        print("Bot: Please type a question.")
    else:
        message_count += 1

        # Handle complaints before ordinary FAQs so they get priority.
        if (
            "refund" in message
            or "complaint" in message
            or "order is late" in message
        ):
            answered_by_rules += 1
            print("Bot: Please contact our support team for help.")

        elif message == "bye":
            print(f"Bot: Goodbye, {customer_name}!")
            break

        elif message == "/quote":
            item = input("Item (notebook / pen / backpack): ").strip().lower()

            if item == "notebook":
                item_price = 250
            elif item == "pen":
                item_price = 50
            elif item == "backpack":
                item_price = 1500
            else:
                item_price = 0

            if item_price == 0:
                print("Bot: Sorry, that item is not on our menu.")
            else:
                quantity_text = input("Quantity: ").strip()

                # Check before conversion so letters do not crash the program.
                if quantity_text.isascii() and quantity_text.isdigit():
                    quantity = int(quantity_text)

                    if quantity > 0:
                        subtotal = item_price * quantity

                        if quantity >= 10:
                            discount = subtotal * 0.10
                        else:
                            discount = 0

                        discounted_subtotal = subtotal - discount

                        # Apply delivery rules after discount, as designed.
                        if discounted_subtotal >= FREE_DELIVERY_LIMIT:
                            delivery = 0
                        else:
                            delivery = DELIVERY_FEE

                        total = discounted_subtotal + delivery

                        print(f"Subtotal: {subtotal:,.2f} PKR")
                        print(f"Discount: -{discount:,.2f} PKR")
                        print(f"Delivery: {delivery:,.2f} PKR")
                        print(f"Total: {total:,.2f} PKR")

                        quote_count += 1
                        total_quoted_value += total
                    else:
                        print("Bot: Quantity must be greater than zero.")
                else:
                    print("Bot: Please enter a positive whole number.")

        # Match greetings exactly to avoid finding 'hi' inside 'which'.
        elif message == "hi" or message == "hello":
            answered_by_rules += 1
            print(f"Bot: Welcome, {customer_name}! How can I help?")

        elif "hours" in message or "timings" in message:
            answered_by_rules += 1
            print("Bot: Open Monday–Saturday, 9 am–6 pm.")

        elif "location" in message or "where" in message:
            answered_by_rules += 1
            print("Bot: Please contact support for our shop location.")

        elif "delivery" in message or "shipping" in message:
            answered_by_rules += 1
            print(
                f"Bot: Delivery costs {DELIVERY_FEE} PKR; free from "
                f"{FREE_DELIVERY_LIMIT:,} PKR after discount."
            )

        elif "payment" in message or "pay" in message:
            answered_by_rules += 1
            print("Bot: We accept bank transfers and cash on delivery.")

        else:
            unanswered_count += 1
            question = message.capitalize()[:150]
            estimated_tokens = round(len(question) / 4)

            # Check the full message so truncation cannot hide private keywords.
            if (
                "phone" in message
                or "cnic" in message
                or "address" in message
            ):
                chosen_model = "qwen2.5:3b (local, private)"
                estimated_cost = 0.0
            else:
                chosen_model = "Example cheap cloud model"
                estimated_cost = (
                    estimated_tokens / 1000
                ) * CLOUD_PRICE_PER_1K

            total_ai_cost += estimated_cost

            print(f"Bot: Prepared for {chosen_model}")
            print(f"Estimated question tokens: {estimated_tokens}")
            print(f"Example AI cost: {estimated_cost:.4f} PKR")

            prompt = f"""
You are the assistant for {BOT_NAME}.
Answer {customer_name} in 2 short lines.
Do not invent prices, policies or promises.
If information is missing, ask the customer to contact support.
Question: {question}
"""
            print("--- AI-ready prompt ---")
            print(prompt)

print("==================================================")
print("Session report")
print(f"Messages: {message_count}")
print(f"Answered by rules: {answered_by_rules}")
print(f"Unanswered: {unanswered_count}")
print(f"Successful quotes: {quote_count}")
print(f"Total quoted value: {total_quoted_value:,.2f} PKR")
print(f"Total estimated AI cost: {total_ai_cost:.4f} PKR")
print("==================================================")