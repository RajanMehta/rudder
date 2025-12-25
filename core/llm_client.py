import json
from typing import Any, Dict, List

from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMClient:
    def __init__(self):
        # Load model and tokenizer
        self.model_id = "LiquidAI/LFM2-350M-Extract"
        print(f"Loading model: {self.model_id}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="auto",
            dtype="bfloat16",
            # attn_implementation="flash_attention_2" # uncomment on compatible GPU
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        print("Model loaded.")

    def _generate(
        self, messages: List[Dict[str, str]], max_new_tokens: int = 1024
    ) -> str:
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            tokenize=True,
        ).to(self.model.device)

        output = self.model.generate(
            input_ids,
            do_sample=False,
            max_new_tokens=max_new_tokens,
        )

        # Decode only the new tokens
        generated_ids = output[0][len(input_ids[0]) :]
        return self.tokenizer.decode(
            generated_ids, skip_special_tokens=True, temperature=0
        )

    def predict(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Uses LFM2-350M-Extract to predict intent and entities.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Input: {prompt}"},
        ]
        response_text = self._generate(messages)
        print(f"\n[LLM Raw Output]: {response_text}\n")

        # Extract JSON
        try:
            # simple heuristic to find JSON block
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                print("Error: No JSON found in response")
                return {"intent": "UNKNOWN", "entities": {}}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {"intent": "UNKNOWN", "entities": {}}

    def generate_response(self, prompt: str) -> str:
        """
        Generates natural language response.
        Enforces JSON output to reliably extract text despite model bias.
        """
        # Attempt to split provided prompt and context to reformat for the model
        parts = prompt.split("\nContext: ")
        core_instruction = parts[0]
        context_str = parts[1] if len(parts) > 1 else "{}"

        system_instructions = """Your task is to generate natural language responses based on the provided 
instruction and context. Replace values in the instruction with the ones in context to understand required 
tone of the response. You MUST output strict JSON in the following format:
{
  "answer": "Your natural language response here"
}
"""

        formatted_user_content = (
            f"Context: {context_str}\nInstruction: {core_instruction}\nOutput:"
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": formatted_user_content},
        ]

        response_text = self._generate(messages)
        # Primary: try to parse extracted JSON and return the text content.
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                if "answer" in data:
                    return data["answer"]
        except Exception:
            pass

        # Fallback: assume raw text if parsing failed
        return response_text
