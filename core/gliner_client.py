from typing import Dict, Any, List
from gliner2 import GLiNER2

class GlinerClient:
    def __init__(self, model_id: str = "fastino/gliner2-base-v1"):
        print(f"Loading GLiNER model: {model_id}...")
        self.extractor = GLiNER2.from_pretrained(model_id)
        print("GLiNER model loaded.")

    def predict(self, text: str, schema_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses GLiNER to extract entities and classify intent based on schema.
        """
        # Create schema object from config
        schema = self.extractor.create_schema()
        
        if "entities" in schema_config:
            schema = schema.entities(schema_config["entities"])
            
        if "classification" in schema_config:
            label, classes = schema_config["classification"]
            schema = schema.classification(label, classes)
            
        # Perform extraction
        include_confidence = True
        results = self.extractor.extract(text, schema, include_confidence=include_confidence)

        output = {
            "entities": results.get("entities", {}),
            "intent": results.get("intent", "UNKNOWN").get("label", "UNKNOWN") if include_confidence else results.get("intent", "UNKNOWN")
        }
        
        print(f"\n[GLiNER Raw Output]: {results}\n")
        return output

    def generate_response(self, prompt: str) -> str:
        """
        Gliner is not a generative model, so it returns the prompt as is.
        """
        return prompt
