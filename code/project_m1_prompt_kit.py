"""Create three AI prompts for a local business owner."""

business_name = input("Business name: ")
business_type = input("Business type: ")
city = input("City: ")
customers = input("Main customers: ")

# Convert the budget to a number so it can support calculations later.
budget = int(input("Monthly budget in PKR: "))

print("\n========================================")
print(f"AI Prompt Kit for {business_name}")
print("========================================")

# Give the AI an audience and a clear format to make the post relevant.
marketing_prompt = f"""
Act as a social media writer for {business_name},
a business of type '{business_type}' in {city}.
Write one short Instagram post for {customers}.
Use a friendly tone and finish with one call to action.
Do not invent prices or offers.
"""

# Avoid promising compensation without the owner's approval.
service_prompt = f"""
Act as a customer service assistant for {business_name}.
Write a polite reply to a customer whose order arrived late.
Apologize and ask for their order number.
Keep the reply under 80 words.
Do not promise refunds or discounts.
"""

# Include the budget so the suggestions fit the owner's resources.
growth_prompt = f"""
Act as a small business adviser.
Suggest 3 low-cost ways {business_name}, a business of type
'{business_type}' in {city}, can use AI to reach {customers}.
The total monthly budget is {budget} PKR.
Explain each idea simply and label any costs as estimates.
"""

print("\n[1] Marketing")
print(marketing_prompt)

print("\n[2] Customer Service")
print(service_prompt)

print("\n[3] Growth")
print(growth_prompt)