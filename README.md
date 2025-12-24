# Rudder: Simplified Conversational Engine (WIP)

Rudder is a lightweight, JSON-configurable dialog engine that orchestrates LLM intelligence with deterministic state control. It serves as the "rudder" for your LLM, ensuring it stays on course through pre-defined conversational flows.

## Core Flow
1.  **State Lookup**: The engine identifies the user's current state from the session context (or starts at `root`).
2.  **Constraint Construction**: A `PromptBuilder` generates a prompt containing *only* the valid transitions, slots, and instructions for that specific state.
3.  **LLM Inference**: The LLM (stateless) analyzes the query against these constraints to extract an **Intent** and **Entities (Slots)**.
4.  **Validation & Enrichment**: Python-based validators check the slots (e.g., `is_positive_number`). Enrichers transform them (e.g., `to_float`).
5.  **State Transition**:
    *   **Intent-Based**: User intent matches a transition target.
    *   **Action-Result**: An action executes and returns a result string (e.g., "insufficient_funds") which maps to a new state.
6.  **Response**: The system returns a static template or generates a natural language response using the LLM.

## Config Schema (`flow.json`)

The entire conversational logic is defined in a JSON file. This schema allows for both simple intent-based navigation and complex slot-filling or action-oriented flows.

### Complete Example
```json
{
  "settings": {
    "start_state": "root"
  },
  "states": {
    "root": {
      "description": "Greeting state where we identify user intent.",
      "type": "standard",
      "transitions": [
        { "intent": "book_flight", "target": "collect_city" },
        { "intent": "check_status", "target": "get_booking_id" }
      ],
      "response_template": "Welcome! How can I help you today?"
    },
    "collect_city": {
      "description": "Collect the destination city.",
      "slots_required": ["destination"],
      "slot_config": {
        "destination": { 
          "validator": "is_valid_city", 
          "enricher": "to_airport_code" 
        }
      },
      "transitions": [
        { 
          "intent": "provide_info", 
          "target": "verify_booking", 
          "condition": "all_slots_filled" 
        },
        { 
          "intent": "cancel", 
          "target": "root", 
          "context_updates": { "clear_slots": ["destination"] } 
        }
      ],
      "response_prompt": "Ask the user where they want to fly to."
    },
    "verify_booking": {
      "type": "action",
      "action_name": "check_availability",
      "transitions": {
        "success": "booking_confirmed",
        "unavailable": "collect_city",
        "error": "system_failure"
      },
      // Legacy fallback (optional)
      "on_success": "booking_confirmed",
      "on_error": "system_failure"
    },
    "booking_confirmed": {
      "response_template": "Your flight to {{destination}} is confirmed!",
      "fallback_behavior": "ask_reclassify"
    }
  }
}
```

### Field Reference

#### Global Settings
| Field | Type | Description |
| :--- | :--- | :--- |
| `settings.start_state` | `string` | The ID of the state where every new session begins. |

#### State Object
Each key in the `states` object represents a unique state ID.

| Field | Type | Description |
| :--- | :--- | :--- |
| `description` | `string` | **Required.** Context provided to the LLM to help it understand the purpose of this state. |
| `type` | `enum` | `standard` (default) or `action`. Action states execute code immediately upon entry. |
| `slots_required` | `string[]` | List of slot names that *must* be filled to satisfy certain transition conditions. |
| `slots_optional` | `string[]` | List of slot names that the engine should try to extract if present. |
| `slot_config` | `object` | Map of slot names to their logic: `validator` (Python function name) and `enricher` (Python function name). |
| `transitions` | `list \| object` | **Standard State:** A list of intent-based transition objects (see below).<br>**Action State:** A map of action result strings (e.g., "success", "error") to target state IDs. |
| `action_name` | `string` | The name of the Python function to execute (only for `type: action`). |
| `on_success` | `string` | Legacy fallback for action states if `transitions` map doesn't match a "success" result. |
| `on_error` | `string` | Legacy fallback for action states if `transitions` map doesn't match an "error" result. |
| `response_template` | `string` | A static text string to return to the user. |
| `response_prompt` | `string` | A prompt for the LLM to generate a dynamic, natural language response. |
| `fallback_behavior` | `enum` | `oos` (default): Go to `out_of_scope` state.<br>`ask_reclassify`: Prompt the user for clarification. |

#### Transition Object (Standard State)
| Field | Type | Description |
| :--- | :--- | :--- |
| `intent` | `string` | The user intent that triggers this transition. |
| `target` | `string` | The ID of the state to transition to. |
| `condition` | `enum` | `all_slots_filled`: Only transition if all `slots_required` are present in context. |
| `context_updates` | `object` | Logic to modify memory. Supported: `clear_slots` (list of strings). |

## Features
*   **Stateless LLM Logic**: The LLM never sees the whole graph, only the immediate valid options.
*   **Dynamic Validations**: Plug in Python functions to validate data before it enters the context.
*   **Graceful Fallbacks**: Configurable behavior for "Unknown" intents or "Action Errors".

## Advanced Usage
See the `examples/` directory for detailed patterns:
1.  **Simple FAQ**: Intent-based navigation.
2.  **Slot Filling**: Collecting required data with validation.
3.  **Complex Flow**: Shared slots and multi-step processes.
4.  **Error Handling**: Robust recovery from system failures.
