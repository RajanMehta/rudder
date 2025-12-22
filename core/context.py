from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DialogContext:
    session_id: str
    current_state: str
    slots: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)
    previous_state: Optional[str] = None
    
    def add_turn(self, role: str, text: str):
        self.history.append({"role": role, "text": text})

    def update_slot(self, key: str, value: Any):
        self.slots[key] = value

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "slots": self.slots,
            "last_turn": self.history[-1] if self.history else None
        }
