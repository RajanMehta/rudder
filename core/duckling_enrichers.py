import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


class DucklingEnricher:
    def __init__(
        self, base_url: str = "http://duckling-server:8000", locale: str = "en_GB"
    ):
        self.base_url = base_url
        self.locale = locale

    def _parse(self, text: str) -> List[Dict[str, Any]]:
        """
        Calls the Duckling API to parse the given text.
        """
        try:
            payload = {"text": text, "locale": self.locale}
            response = requests.post(f"{self.base_url}/parse", data=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to parse text with Duckling: {e}")
            return []

    def _get_first_value_for_dim(self, text: str, dim: str) -> Any:
        """
        Helper method to get the value of the first entity matching the dimension.
        Returns the original text if no match is found.
        """
        entities = self._parse(text)
        for entity in entities:
            if entity.get("dim") == dim:
                return entity.get("value")
        return text

    # --- Pre-defined Enrichers ---

    def enrich_amount_of_money(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "amount-of-money")

    def enrich_credit_card_number(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "credit-card-number")

    def enrich_distance(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "distance")

    def enrich_duration(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "duration")

    def enrich_email(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "email")

    def enrich_numeral(self, value: str) -> Any:
        return self._get_first_value_for_dim(
            value, "number"
        )  # Duckling dim can be 'number' or 'ordinal'

    def enrich_ordinal(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "ordinal")

    def enrich_phone_number(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "phone-number")

    def enrich_quantity(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "quantity")

    def enrich_temperature(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "temperature")

    def enrich_time(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "time")

    def enrich_url(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "url")

    def enrich_volume(self, value: str) -> Any:
        return self._get_first_value_for_dim(value, "volume")
