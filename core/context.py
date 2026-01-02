from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DialogContext:
    session_id: str
    current_state: str
    slots: Dict[str, Any] = field(default_factory=dict)
    slot_metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    previous_state: Optional[str] = None

    def record_turn(
        self,
        user_input: str,
        state_in: str,
        state_out: str,
        bot_response: str,
        slots: Dict[str, Any] = None,
    ):
        turn = {
            "role": "user",  # Initiator
            "text": user_input,
            "state_in": state_in,
            "state_out": state_out,
            "bot_response": bot_response,
            "slots": slots or {},
        }
        self.history.append(turn)

    def update_slot(self, key: str, value: Any):
        # Normalize: Try to extract value if it looks like an NLU/Enricher result
        # Expected NLU result signature: List of dicts, often with 'value' key (from enricher) or 'text'
        extracted_value = value
        metadata = value

        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # It's likely a list of entities. We take the first one (highest confidence).
            first_item = value[0]
            if "value" in first_item:
                # Enricher result often has nested value
                val = first_item["value"]
                if isinstance(val, dict) and "value" in val:
                    # Duckling style: {'value': {'type': 'value', 'value': 100, ...}}
                    extracted_value = val["value"]
                else:
                    extracted_value = val
            elif "text" in first_item:
                extracted_value = first_item["text"]

        self.slots[key] = extracted_value
        self.slot_metadata[key] = metadata

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "slots": self.slots,
            "last_turn": self.history[-1] if self.history else None,
        }
