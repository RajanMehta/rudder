# Rudder Card Management Examples

This folder contains a series of examples demonstrating how to build a banking conversational AI for card management, increasing in complexity from basic FAQs to robust error handling.

## Use Case: Card Management
The system handles requests for:
- Activating a card
- Cancelling a card
- Rewards information
- Credit limit increases
- Freezing a card
- Reporting lost/stolen cards
- Card replacements

---

### [Level 1: Simple FAQ](1_faq_simple/flow.json)
**Focus:** Intents and Static Responses.
- Uses `response_template` for fixed answers.
- Simple state transitions based on classified intents.
- Smart fallback behavior that returns to the main menu.

### [Level 2: FAQ + Entity Extraction](2_faq_slots/flow.json)
**Focus:** Basic Slots and Conditions.
- Demonstrates extraction of entities like `limit_amount` and `card_type`.
- Uses `condition: "all_slots_filled"` to ensure information is captured before proceeding.
- Uses `response_template` to prompt for missing information.

### [Level 3: Dynamic Slot Updates](3_complex_slots/flow.json)
**Focus:** User Corrections and State Updates.
- Shows how the engine automatically updates slots if the user provides new information during the flow.
- Demonstrates a "confirm" state where users can verify and correct their details (e.g., lost card location) before processing.

### [Level 4: Robust Error Handling](4_error_handling/flow.json)
**Focus:** Validations, Fallbacks, and Handoffs.
- Uses `slot_config` with validators (e.g., `validate_4_digits`) to ensure data quality.
- Implements `fallback_behavior: "ask_reclassify"` for more natural recovery.
- Includes a human agent handoff state for complex or out-of-scope requests.

---

## How to Run
To run these examples with the `GlinerClient`, update your `main.py` or initialization script to point to the desired JSON file:

```python
config_path = "examples/X_folder_name/flow.json"
client = GlinerClient() # or your preferred client
engine = DialogEngine(config_path, client)
```
