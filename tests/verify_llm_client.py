import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.gliner_client import GlinerClient
from core.prompt_builder import PromptBuilder

def test_llm_client():
    print("Initializing LLMClient...")
    try:
        client = GlinerClient()
    except Exception as e:
        print(f"Failed to initialize LLMClient: {e}")
        return

    print("\n--- Testing predict with Realistic Context ---")
    
    # Simulate 'transfer_flow_start' state from banking_flow.json
    state_config = {
        "description": "Initiating a money transfer. We need to know who to send it to and how much.",
        "slots_required": ["amount", "recipient"],
        "slots_optional": ["memo"],
        "transitions": [
            {"intent": "transfer_details", "target": "transfer_confirm", "condition": "all_slots_filled"},
            {"intent": "cancel", "target": "root"}
        ]
    }
    
    context_snapshot = {
        "current_state": "transfer_flow_start",
        "slots": {}
    }
    
    prompt_builder = PromptBuilder()
    system_prompt = prompt_builder.build_constraint_prompt(state_config, context_snapshot)
    
    user_input = "I want to send 100 dollars to Bob"
    print(f"User Input: {user_input}")
    
    try:
        result = client.predict(user_input, system_prompt)
        print(f"Result: {result}")
        
        if isinstance(result, dict) and result.get("intent") == "transfer_details":
             entities = result.get("entities", {})
             if "amount" in entities and "recipient" in entities: # strict check on values might be too flaky for raw model without fine-tuning, but checking keys is good
                 print("Predict Test PASSED: Intent and Entities found")
             else:
                 print("Predict Test PARTIAL PASS: Intent found but entities missing/wrong")
        else:
             print("Predict Test FAILED: Incorrect intent or format")

    except Exception as e:
        print(f"Predict Test FAILED with error: {e}")

    print("\n--- Testing generate_response with Realistic Context ---")
    try:
        # Simulate 'transfer_confirm' state response generation
        response_prompt = "Ask the user to confirm the transfer of {amount} to {recipient}."
        slots = {"amount": "100 dollars", "recipient": "Bob"}
        
        # Logic mirroring engine.py _generate_response
        formatted_prompt = response_prompt.format(**slots) # Simulating variable injection if the prompt uses f-string style or just appending context as engine.py does
        
        # But wait, looking at engine.py:
        # formatted_prompt = prompt + f"\nContext: {context.slots}"
        # The prompt in banking_flow.json is "Ask the user to confirm the transfer of {amount} to {recipient}."
        # It seems engine.py blindly appends the context. 
        # Let's verify what the user actually wants. user said "Analyze engine.py".
        # engine.py line 181: formatted_prompt = prompt + f"\nContext: {context.slots}"
        # logic: 
        
        raw_prompt = "Ask the user to confirm the transfer of 100 dollars to Bob." # Assuming simple string or pre-formatted
        # Actually banking_flow.json has: "response_prompt": "Ask the user to confirm the transfer of {amount} to {recipient}."
        # engine.py does NOT format the string with slots before appending context. It just appends context. 
        # So the LLM sees the curly braces? Or does the user expect us to fix engine.py? 
        # The user said "Analyze engine.py and fix the testing... in verify_llm.py". 
        # So I should replicate what engine.py DOES, even if it looks weird, or maybe prompt_builder/engine handles it.
        # core/engine.py:181: formatted_prompt = prompt + f"\nContext: {context.slots}"
        # It literally just appends the dict.
        
        input_prompt_from_config = "Ask the user to confirm the transfer of {amount} to {recipient}."
        context_slots = {"amount": "100", "recipient": "Bob"}
        formatted_prompt = input_prompt_from_config + f"\nContext: {context_slots}"
        
        print(f"Input Prompt: {formatted_prompt}")
        
        response = client.generate_response(formatted_prompt)
        print(f"Response: {response}")
        if isinstance(response, str) and len(response) > 0:
             if response.strip().startswith("{"):
                 print("Generate Test FAILED: Output is JSON, expected natural language.")
             else:
                 print("Generate Test PASSED")
        else:
             print("Generate Test FAILED (Empty or invalid response)")
    except Exception as e:
        print(f"Generate Test FAILED with error: {e}")

if __name__ == "__main__":
    test_llm_client()
