# Example 1: Simple FAQ

This example demonstrates the most basic usage of Rudder: a purely intent-driven FAQ bot with static responses.

## Scenario
A user asks about store hours and locations. No dynamic data or slots are involved.

## Features Used
*   **Static Responses**: `response_template` is used for all replies.
*   **Intent Transitions**: Simple mapping from user intent to nodes.
*   **Cyclic Navigation**: Users can jump between `hours` and `location` freely.

## Walkthrough

**User**: "When are you open?"
*   **Intent**: `ask_hours`
*   **Transition**: `root` -> `hours_info`
*   **Bot**: "We are open Monday-Friday, 9am to 9pm."

**User**: "Where is the store?"
*   **Intent**: `ask_location`
*   **Transition**: `hours_info` -> `location_info`
*   **Bot**: "We are located at 123 Main St, Springfield."

**User**: "Thanks!"
*   **Intent**: `thanks`
*   **Transition**: `location_info` -> `root`
*   **Bot**: "Hi! I can help you with store hours and locations."
