# Example 4: Error & Out-of-Scope Handling

This example demonstrates how Rudder handles **Validation Failures** and **Action Errors**.

## Scenario
A secure login flow. The system must validate the PIN format and check it against an API.

## Features Used
*   **Validators**: `is_4_digits` ensures the slot isn't accepted unless valid.
*   **Action Result Mapping**: `verify_pin_api` can return `invalid_pin` (logic error) or `api_down` (system error).
*   **Fallback Behavior**: `ask_reclassify` helps when the user says something totally unrelated.

## Walkthrough

**Bot**: "Please say your 4-digit PIN."

**User**: "My PIN is 12345" (5 digits)
*   **Validator**: `is_4_digits` returns False. Slot rejected.
*   **Bot**: "I didn't capture that. Please say your 4-digit PIN." (Implicit loop)

**User**: "1234" (4 digits)
*   **Slot**: `pin` = "1234"
*   **Transition**: `login` -> `verify_pin`
*   **Action**: Returns `"invalid_pin"`.
*   **Transition**: `verify_pin` -> `login_error`
*   **Bot**: "That PIN is invalid. Please try again."

**User**: "2000" (Correct)
*   **Transition**: `login_error` -> `verify_pin`
*   **Action**: Returns `"success"`.
*   **Bot**: "Welcome to your dashboard!"
