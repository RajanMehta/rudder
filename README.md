# 🧭 Rudder: Simplified Conversational Engine (WIP)

Rudder is a lightweight, JSON-configurable dialog engine that orchestrates LLM intelligence with deterministic state control. It serves as the "rudder" for your LLM, ensuring it stays on course through defined business flows.

## Core Flow
1.  **State Lookup**: The engine identifies the user's current state from the session context (or starts at `root`).
2.  **Constraint Construction**: A `PromptBuilder` generates a prompt containing *only* the valid transitions, slots, and instructions for that specific state.
3.  **LLM Inference**: The LLM (stateless) analyzes the query against these constraints to extract an **Intent** and **Entities (Slots)**.
4.  **Validation & Enrichment**: Python-based validators check the slots (e.g., `is_positive_number`). Enrichers transform them (e.g., `to_float`).
5.  **State Transition**:
    *   **Intent-Based**: User intent matches a transition target.
    *   **Action-Result**: An action executes and returns a result string (e.g., "insufficient_funds") which maps to a new state.
6.  **Response**: The system returns a static template or generates a natural language response using the LLM.

## Configuration Schema (`flow.json`)

The entire conversational logic is defined in a single JSON file.

### Structure
```json
{
  "settings": { "start_state": "root" },
  "states": {
    "state_name": {
      "description": "Context for the LLM",
      "slots_required": ["slot_name"],
      "slots_optional": ["opt_slot"],
      "slot_config": {
         "slot_name": { 
             "validator": "func_name", 
             "enricher": "func_name" 
         }
      },
      "type": "standard | action",
      "action_name": "python_func_name", // If type is action
      "transitions": [
         // Intent Transition
         { "intent": "user_intent", "target": "next_state", "context_updates": {"clear_slots": ["slot_name"]} },
         
         // Action Result Transition (in 'transitions' map if type is 'action')
         // See below
      ],
      "response_template": "Static text response",
      "response_prompt": "Prompt for LLM generation"
    }
  }
}
```

### Key Concepts

*   **States**: Nodes in your conversation graph.
*   **Slots**: Variables extracted from user input.
    *   **Required**: Flow waits until these are filled.
    *   **Optional**: Captured if present, but don't block.
*   **Context Updates**: Surgical modification of memory (e.g., clearing `amount` when canceling).
*   **Actions**: Python functions that execute business logic. They return result strings to drive transitions.

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
