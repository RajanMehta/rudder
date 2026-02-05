import json
from typing import Any, Dict


class PromptBuilder:
    def __init__(self):
        pass

    def build_constraint_prompt(
        self, state_config: Dict[str, Any], context_snapshot: Dict[str, Any]
    ) -> str:
        """
        Constructs the strict constraint prompt for the NLU.
        """
        transitions = state_config.get("transitions", [])
        intent_list = [t["intent"] for t in transitions]

        required_slots = state_config.get("slots_required", [])
        optional_slots = state_config.get("slots_optional", [])

        if not required_slots and not optional_slots:
            extraction_instructions = "2. Entity Extraction: Do NOT extract any entities. Return an empty dictionary."
            entities_json_template = '"entities": {}'
        else:
            extraction_instructions = f"""
2. Entity Extraction: Extract values for the following slots if present in the input:
   - Required Slots: {json.dumps(required_slots)}
   - Optional Slots: {json.dumps(optional_slots)}
   - Return entities as a dictionary where keys are the specific slot names from the lists above."""
            entities_json_template = """"entities": {
    "<slot_name>": "<extracted_value>"
  }"""

        system_prompt = f"""
You are a Dialog Decision Engine. Your task is to analyze User Input and extract structured data.

Context:
- Current State: {context_snapshot['current_state']}
- State Description: {state_config.get('description', 'No description')}

Constraints:
1. Intent Classification: You MUST classify the User Input into EXACTLY ONE of the following Intents:
{json.dumps(intent_list, indent=2)}
   - If the input matches one of these intents, use that exact string as the "intent".
   - If the input does NOT match any of these (e.g., gibberish, unrelated), use "UNKNOWN".

{extraction_instructions}

output strict JSON:
{{
  "intent": "<classified_intent>",
  {entities_json_template}
}}
"""
        return system_prompt


class GlinerPromptBuilder:
    def __init__(self):
        pass

    def build_schema(self, state_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the schema for Gliner extraction.
        """
        transitions = state_config.get("transitions", [])
        intent_labels = [t["intent"] for t in transitions]

        required_slots = state_config.get("slots_required", [])
        optional_slots = state_config.get("slots_optional", [])
        slot_config = state_config.get("slot_config", {})

        entities = {}
        for slot in required_slots + optional_slots:
            # Check for custom description in slot_config
            slot_cfg = slot_config.get(slot, {})
            if "description" in slot_cfg:
                entities[slot] = slot_cfg["description"]
            else:
                # Default description
                entities[slot] = f"Extract the {slot} from the text"

        return {"entities": entities, "classification": ("intent", intent_labels)}
