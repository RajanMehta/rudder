import json
import logging
from typing import Dict, Optional

from .context import DialogContext
from .llm_client import LLMClient
from .prompt_builder import GlinerPromptBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register(self, name, func):
        self._actions[name] = func

    def execute(self, name, context: DialogContext):
        if name not in self._actions:
            raise ValueError(f"Action {name} not found")
        return self._actions[name](context)


class ValidatorRegistry:
    def __init__(self):
        self._validators = {}
        self._enrichers = {}

    def register_validator(self, name, func):
        self._validators[name] = func

    def register_enricher(self, name, func):
        self._enrichers[name] = func

    def validate(self, name, value):
        if name not in self._validators:
            return True  # Default valid
        return self._validators[name](value)

    def enrich(self, name, value):
        if name not in self._enrichers:
            return value
        return self._enrichers[name](value)


class DialogEngine:
    def __init__(self, config_path: str, llm_client: LLMClient):
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.llm_client = llm_client
        self.prompt_builder = GlinerPromptBuilder()
        self.actions = ActionRegistry()
        self.validators = ValidatorRegistry()
        self.states = self.config["states"]

    def start_session(self, session_id: str) -> DialogContext:
        start_state = self.config["settings"]["start_state"]
        return DialogContext(session_id=session_id, current_state=start_state)

    def process_turn(self, user_input: str, context: DialogContext) -> str:
        logger.info(f"Processing turn: {user_input} in state {context.current_state}")
        context.add_turn("user", user_input)

        current_state_config = self.states[context.current_state]

        # 1. Check if current state has an Action (Immediate Execution)
        # This usually happens if we transitioned to an action state in the previous turn
        # If current state is Terminal, go back to start state
        if current_state_config.get("type") == "action":
            return self._handle_action_state(context, current_state_config)
        elif current_state_config.get("type") == "terminal":
            context.current_state = self.config["settings"]["start_state"]
            current_state_config = self.states[context.current_state]

        # 2. NLU Step: Determine Intent
        nlu_result = self._run_nlu(user_input, current_state_config, context)
        intent = nlu_result.get("intent")
        entities = nlu_result.get("entities", {})

        # 3. Validate & Enrich Slots
        slot_config = current_state_config.get("slot_config", {})
        for k, v in entities.items():
            # Validation
            config_item = slot_config.get(k, {})
            validator_name = config_item.get("validator")
            if validator_name:
                if not self.validators.validate(validator_name, v):
                    logger.warning(f"Slot {k}={v} failed validation {validator_name}")
                    continue  # Skip invalid slot

            # Enrichment
            enricher_name = config_item.get("enricher")
            if enricher_name:
                # v is a list of entities. Assuming the first one is the one we want to enrich.
                enricher_response = self.validators.enrich(enricher_name, v[0]["text"])
                v[0]["value"] = enricher_response

            context.update_slot(k, v)

        # 4. Handle State Transitions
        next_state = self._resolve_transition(current_state_config, intent, context)
        print(f"\nNext State: {next_state}\n")

        if next_state:
            context.previous_state = context.current_state
            context.current_state = next_state
            # Check if the new state is an action state and run it immediately?
            # Ideally, we return the response for the NEW state.
            new_state_config = self.states[next_state]
            if new_state_config.get("type") == "action":
                return self._handle_action_state(context, new_state_config)
            return self._generate_response(new_state_config, context)
        else:
            # Fallback
            return self._handle_fallback(context, current_state_config)

    def _run_nlu(
        self, user_input: str, state_config: Dict, context: DialogContext
    ) -> Dict:
        schema_config = self.prompt_builder.build_schema(state_config)
        return self.llm_client.predict(user_input, schema_config=schema_config)
        # For now, I'm not using generative models for NLU as I couldn't find a good open source option.
        # system_prompt = self.prompt_builder.build_constraint_prompt(state_config, context.get_snapshot())
        # return self.llm_client.predict(user_input, system_prompt=system_prompt)

    def _resolve_transition(
        self, state_config: Dict, intent: str, context: DialogContext
    ) -> Optional[str]:
        transitions = state_config.get("transitions", [])
        for t in transitions:
            if t["intent"] == intent:
                # Check conditions
                if "condition" in t:
                    if t["condition"] == "all_slots_filled":
                        required = state_config.get("slots_required", [])
                        # Only check REQUIRED slots
                        if not all(k in context.slots for k in required):
                            continue  # Condition failed

                # Context Updates (Clearing Slots)
                if "context_updates" in t:
                    to_clear = t["context_updates"].get("clear_slots", [])
                    for slot_name in to_clear:
                        if slot_name in context.slots:
                            del context.slots[slot_name]

                return t["target"]
        return None

    def _handle_action_state(self, context: DialogContext, state_config: Dict) -> str:
        action_name = state_config.get("action_name")
        result = "success"  # Default
        try:
            # Action can now return a result string
            exec_result = self.actions.execute(action_name, context)
            if exec_result:
                result = str(exec_result)
        except Exception as e:
            logger.error(f"Action failed: {e}")
            result = "error"

        # Resolve transition based on result
        transitions = state_config.get("transitions", {})

        # Fallback to legacy on_success/on_error if transitions not defined
        # But per new design, we check transitions first
        next_state = transitions.get(result)

        if not next_state:
            # Backward compatibility / Simple binary handling handling
            if result == "success":
                next_state = state_config.get("on_success")
            else:
                next_state = state_config.get("on_error")

        if not next_state:
            logger.error(
                f"No transition found for action result: {result} in state {context.current_state}"
            )
            return "System Error: Invalid State Transition"

        context.previous_state = context.current_state
        context.current_state = next_state

        # Recursive call to handle the NEXT state (which usually has the response)
        return self._generate_response(self.states[next_state], context)

    def _generate_response(self, state_config: Dict, context: DialogContext) -> str:
        # Static Template
        if "response_template" in state_config:
            return state_config["response_template"]

        # LLM Generation
        if "response_prompt" in state_config:
            prompt = state_config["response_prompt"]
            # Formatting slots into prompt
            formatted_prompt = prompt + f"\nContext: {context.slots}"
            return self.llm_client.generate_response(formatted_prompt)

        return "Thinking..."

    def _handle_fallback(self, context: DialogContext, state_config: Dict) -> str:
        behavior = state_config.get("fallback_behavior", "oos")
        if behavior == "oos":
            context.current_state = "out_of_scope"
            return self._generate_response(self.states["out_of_scope"], context)
        elif behavior == "ask_reclassify":
            return "I didn't quite get that. Could you clarify?"  # Simplified for now
        return "I am confused."
