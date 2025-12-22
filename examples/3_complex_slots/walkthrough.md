# Example 3: Shared Slots & Complex Transitions

This example demonstrates **State Persistence** (shared slots) and **Action-Result Transitions**.

## Scenario
A user checks their "savings" balance, then immediately decides to transfer money. The system remembers the `account_type` is "savings" so it doesn't ask again.

## Features Used
*   **Shared Slots**: `account_type` extracted in `view_balance` is automatically available in `transfer_start`.
*   **Action-Result**: `get_balance_action` transitions based on function success.
*   **Multi-Step Flow**: A conversation spanning multiple intents and actions.

## Walkthrough

**User**: "Check my balance."
*   **State**: `view_balance`
*   **Bot**: "Checking or Savings?"

**User**: "Savings"
*   **Slot**: `account_type` = "savings"
*   **Action**: `get_balance` executes.
*   **Bot**: "Your savings balance is $5,000."

**User**: "Transfer 50 to John"
*   **Intent**: `transfer_money` -> `transfer_start`
*   **Slots**:
    *   `amount` = "50" (New)
    *   `recipient` = "John" (New)
    *   `account_type` = "savings" (**Existing/Shared**)
*   **Condition**: `all_slots_filled` is TRUE. No need to ask for account type!
*   **Action**: `transfer_exec`
*   **Bot**: "Transferred 50 to John from savings."
