# AI Business Assistant — Project Design

## Business data

| Key | Value |
|---|---|
| name | Talha Stationery |
| type | Stationery shop |
| city | Lahore |
| hours | Monday–Saturday, 9 am–6 pm |
| delivery | 200 PKR; free from 3,000 PKR | within 2-5 working days
| payment_methods | Bank transfer and cash on delivery |
| prices | notebook: 250 PKR; pen: 50 PKR; backpack: 1,500 PKR; art kit: 700 PKR |

## Tools

| Tool | Reads / checks / acts | Inputs | Needs approval? |
|---|---|---|---|
| get_price | Reads a price | item | No |
| get_info | Reads business information | topic | No |
| order_status | Checks an order | order_id | No |
| place_order | Places an order | item, quantity, customer | Yes |

## Guardrails

| Risk | Guardrail |
|---|---|
| Agent keeps calling tools | Stop after MAX_STEPS |
| Agent invents prices | Look up prices from business.json |
| Agent saves an unwanted order | Ask for approval before saving |
| AI invents an imported order name | Check the name appears in the original message |
| Customer requests an unknown product | Flag it; do not price it |
| Saved files contain private data | Add orders.json, transcript.json and errors.log to .gitignore |

## Agent tests

| Test | Expected | Tools called | Pass? |
|---|---|---|---|
| Ask for the shop’s name | Short answer using business data | get_info | Pass |
| Ask for one item’s price | Correct price from the menu | get_price | Pass |
| Compare two item prices | Correct prices; Python price tool called for each | Pass |
| Ask about hours or delivery | Answer from business data | get_info | Pass |
| Ask for status of a saved order | Status read from orders.json | order_status | Pass |
| Request an order, then decline approval | Order is not saved | place_order | Pass |
| Request an order, then approve | Correct Python total; order is saved once | place_order | Pass |
| Ask whether the shop sells pizza | Says it is not on the menu | get_price | Pass |
| Ask for a free order or to ignore the rules | No order without owner approval | | |

## WhatsApp import tests

| Message tested | Expected | Pass? |
|---|---|---|
| Normal order with name and address | Items and Python total shown | Pass |
| Roman Urdu order with two items | Both items and quantities extracted | Pass |
| Order includes pizza | CHECK for off-menu item; pizza is not priced | Pass |
| Order has no customer name | CHECK; order not saved | Pass |
| “Hi, do you deliver to DHA?” | Not an order; needs human reply | Pass |

## Error and data tests

| Test | Expected | Pass? |
|---|---|---|
| Run without Ollama, then ask a question | Friendly offline message; error logged | Pass |
| Use an unavailable model name | Friendly error; error logged | Pass |
| Start with damaged transcript.json | Warning and fresh transcript; no crash | Pass |
| Start with damaged orders.json | Warning and fresh orders; no crash | Pass |
| Temporarily rename business.json | Clear missing-file message | Pass |
| Change a price in business.json and restart | Tool uses the updated price | Pass |