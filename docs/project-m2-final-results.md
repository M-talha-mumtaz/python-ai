# Module 2 Final Project Results

## Project

Talha Stationery AI Business Assistant

## Model

`qwen2.5:3b`

## AI Quality Tests

### Agent Test 1: Delivery Total

Customer input:

```text
I want 5 notebooks.
```

The AI previously described 1,250 PKR as above the 3,000 PKR free-delivery limit. This was incorrect.

The program now calculates the price in Python:

- Notebook subtotal: 1,250 PKR
- Delivery fee: 200 PKR
- Final total: 1,450 PKR

Result: Pass

### Agent Test 2: Off-Menu Product

Customer input:

```text
Do you sell pizza?
```

The assistant must not invent a price or say that pizza is available.

The `get_price` tool checks the products in `business.json`. Pizza is not on the menu, so the assistant reports that it is unavailable.

Result: Pass

### WhatsApp Import Test 1: Off-Menu Item

Imported message:

```text
Hi, I am Ayesha. I need 2 notebooks and 1 pizza delivered to Model Town, Lahore.
```

The AI could incorrectly include pizza in the order total.

The program checks every extracted item against the menu and shows:

```text
CHECK: 'pizza' is not on the menu
```

Pizza is not priced or saved in the order.

Result: Pass

### WhatsApp Import Test 2: Missing Customer Name

Imported message:

```text
Please send 2 notebooks to DHA Phase 5, Lahore.
```

The AI could invent a customer name that was not written in the message.

The program checks whether the customer name appears in the original WhatsApp message. It shows a `CHECK` message for the missing name and does not save the order.

Result: Pass

## Improvement Made

I updated the order calculation so Python calculates the subtotal, delivery fee, and final total. The assistant now charges 200 PKR delivery for an order below 3,000 PKR and gives free delivery only when the subtotal is 3,000 PKR or more.

## Summary

All Module 2 tests passed. The assistant uses business data, tools, Python calculations, and approval checks to prevent invented prices, incorrect totals, unapproved orders, and invalid WhatsApp imports.