# AI Front Desk — Project Design

## Business

Name: Talha Stationery
Purpose: Answer common questions and calculate stationery order quotes.

These are example business details and prices.

## Customer Intents

| Intent | Keywords | Reply or action |
|---|---|---|
| Complaint | refund, complaint, order is late | Ask the customer to contact support. |
| Greeting | exact message: hi or hello | Welcome the customer by name. |
| Hours | hours, timings | Open Monday–Saturday, 9 am–6 pm. |
| Location | location, where | Give the shop's actual location. |
| Delivery | delivery, shipping | Delivery costs 200 PKR; free for orders of 3,000 PKR or more after discount. |
| Payment | payment, pay | Bank transfer and cash on delivery accepted. |
| Quote | exact message: /quote | Ask for item and quantity, then calculate the total. |
| Exit | exact message: bye | Print goodbye and a session report. |
| Unknown question | no matching rule | Prepare an AI prompt and estimate its cost. |

## Business Rules

| Rule | Value |
|---|---|
| Notebook price | 250 PKR each |
| Pen price | 50 PKR each |
| Backpack price | 1,500 PKR each |
| Bulk discount | 10% when quantity is 10 or more |
| Delivery fee | 200 PKR |
| Free delivery | Discounted subtotal is at least 3,000 PKR |
| Private keywords | phone, cnic, address |
| Private question routing | Local model: llama3.2; estimated AI cost is zero |
| Other fallback questions | Example cloud model; example price of 0.10 PKR per 1,000 tokens |
| Question length limit | First 150 characters |
| Token estimate | Rounded character count divided by 4 |

## Calculation Order

1. Subtotal = item price × quantity.
2. Calculate the bulk discount.
3. Subtract the discount from the subtotal.
4. Decide delivery charges using the discounted subtotal.
5. Total = discounted subtotal + delivery.

## Session Report Rules

- Count every non-empty chat message, including bye.
- Do not count item and quantity answers as separate chat messages.
- Count FAQ replies and complaint replies as answered by rules.
- Count questions handled by the AI fallback as unanswered.
- Count only successfully calculated quotes.
- Add successful quote totals to the total quoted value.
- Add fallback cost estimates to the total estimated AI cost.

## Test Results

Fill in Pass or Fail only after running each test.

| Test | Expected result | Pass or Fail |
|---|---|---|
| Type "  WHAT ARE YOUR HOURS?  " | Opening hours | Pass | 
| Type "which product is best?" | Fallback, not a greeting | Pass | 
| Type "my order is late" | Complaint response | | 
| /quote → backpack → 1 | Subtotal 1,500; discount 0; delivery 200; total 1,700 PKR | Pass | 
| /quote → backpack → 3 | Subtotal 4,500; discount 0; delivery 0; total 4,500 PKR | Pass | 
| /quote → notebook → 12 | Subtotal 3,000; discount 300; delivery 200; total 2,900 PKR | Pass |
| /quote → unknown item | Not on our menu; no successful quote recorded | Pass | 
| Type "can I change my phone number?" | Local model; cost zero | Pass | 
| Press Enter without text | Ask again | Pass |  
| Type "BYE" | Goodbye and session report | Pass | 