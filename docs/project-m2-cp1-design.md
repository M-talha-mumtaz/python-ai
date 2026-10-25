# AI Content Studio — Project Design

## Business

Talha Stationery: a stationery shop that needs product descriptions,
social media posts, and answers to common customer questions.

The details below are examples. Replace them with verified business
information before submission.

## Facts

| Key | Value |
|---|---|
| name | Talha Stationery |
| city | Replace with the business's actual city |
| hours | Monday–Saturday, 9 am–6 pm |
| delivery | 200 PKR; free from 3,000 PKR after discount |
| payment_methods | Bank transfer and cash on delivery |
| prices | notebook: 250 PKR; pen: 50 PKR; backpack: 1,500 PKR; art kit: 0, meaning coming soon |

## Post Tones

| Tone | Description sent to the AI |
|---|---|
| fun | Playful and energetic, using short sentences |
| formal | Professional, clear and polite |
| premium | Elegant and calm, without inventing product features |

## Model Choices

| Job | Model and temperature | Why |
|---|---|---|
| Customer chat | qwen2.5:3b at 0.2 | More consistent factual answers |
| Product descriptions | qwen2.5:3b at 0.8 | More varied marketing wording |
| Social media posts | qwen2.5:3b at 0.8 | More varied phrasing and tone |
| Price lookup | Python dictionary; no AI | Exact prices without AI token usage |

## Memory

Keep the system instructions plus the last 8 conversation messages.
Reset clears the conversation but preserves the system instructions.

## Session Report

Print:
- Number of chat answers
- Number of product descriptions generated
- Number of posts generated
- Number of price-command answers
- Total AI tokens
- Total AI seconds

## Feature Tests

Complete the final column after testing the program.

| Test | Expected result | Pass or Fail |
|---|---|---|
| /menu | Skip art kit; print 3 numbered descriptions and prices | PASS |
| /post fun | Stream a playful post | PASS |
| /post formal | Stream a professional post | PASS |
| /post premium | Stream an elegant post | PASS |
| /post pirate | Use the default tone without crashing | PASS |
| /price NOTEBOOK | 250 PKR | PASS |
| /price art kit | Coming soon | PASS |
| /price pizza | Not on our menu | PASS |
| My name is Ali, then What is my name? | Remember Ali | PASS |
| /reset, then What is my name? | No longer know the name | PASS |
| Empty input | Ask again | PASS |
| BYE | Exit and print all session totals | PASS |