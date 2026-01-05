import sys
import os

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import DialogEngine
from core.gliner_client import GlinerClient
from core.duckling_enrichers import DucklingEnricher

# Define Mock Actions
def execute_transfer(context):
    if "amount" not in context.slots:
        raise ValueError("Missing amount")
    
    amount = float(context.slots.get("amount"))
    if amount > 1000:
        return "insufficient_funds"
        
    return "success"

def get_balance(context):
    context.slots["balance"] = 5000
    return "success"

# Validators & Enrichers
def validate_positive(value):
    try:
        return float(value) > 0
    except ValueError:
        return False

def to_float(value):
    return float(value)

# Condition Functions
def check_transfer_slots(context, target_state):
    required = ["amount", "recipient"]
    # Check if slots exist AND have truthy values (e.g. not empty list, not None)
    if all(context.slots.get(k) for k in required):
        return target_state
    return context.current_state # Stay here if not filled

# Response Functions
def ask_transfer_info(context):
    # Check truthiness of values
    has_amount = bool(context.slots.get("amount"))
    has_recipient = bool(context.slots.get("recipient"))
    
    if not has_amount and not has_recipient:
        return "Who would you like to transfer money to, and how much?"
    if not has_amount:
        return "How much would you like to transfer?"
    if not has_recipient:
        return "Who is the recipient?"
    return "Thinking..."

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config", "banking_flow.json")
    client = GlinerClient()
    engine = DialogEngine(config_path, client)
    
    # Register Actions
    engine.actions.register("execute_transfer_func", execute_transfer)
    engine.actions.register("get_balance", get_balance)
    
    # Register Validators
    engine.validators.register_validator("is_positive_number", validate_positive)
    
    # Register Enrichers
    engine.validators.register_enricher("to_float", to_float)
    duckling = DucklingEnricher()
    engine.validators.register_enricher("enrich_amount_of_money", duckling.enrich_amount_of_money)

    engine.conditions.register("check_transfer_slots", check_transfer_slots)
    engine.responses.register("ask_transfer_info", ask_transfer_info)

    context = engine.start_session("session_123")
    
    print("--- Dialog System Started (Type 'exit' to quit) ---")
    
    # Initial Greeting
    initial_state = engine.states[context.current_state]
    print(f"Bot: {initial_state.get('response_template', 'Hello')}")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        response = engine.process_turn(user_input, context)
        print(f"Context: {context}")
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()
