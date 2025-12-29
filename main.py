import sys
import os

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import DialogEngine
from core.gliner_client import GlinerClient
from core.duckling_enrichers import DucklingEnricher

# Define Mock Actions
def execute_transfer(context):
    print("\n[SYSTEM] Executing Transfer...")
    if "amount" not in context.slots:
        raise ValueError("Missing amount")
    
    amount = float(context.slots.get("amount")[0])
    if amount > 1000:
        print("[SYSTEM] Transfer Failed: Insufficient Funds")
        return "insufficient_funds"
        
    print(f"[SYSTEM] Transferred {amount} to {context.slots.get('recipient')}")
    return "success"

def get_balance(context):
    print(f"\n[SYSTEM] Balance is $5,000")

# Validators & Enrichers
def validate_positive(value):
    try:
        return float(value) > 0
    except ValueError:
        return False

def to_float(value):
    return float(value)

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
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()
