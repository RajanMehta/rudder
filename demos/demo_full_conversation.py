#!/usr/bin/env python3
"""Demo: Full Conversation Flow

Demonstrates switching between capabilities while maintaining context.
This is the sample conversation from the original requirements.
"""
import sys
sys.path.insert(0, '.')

from core.engine import DialogEngine
from core.gliner_client import GlinerClient
from core.duckling_enrichers import DucklingEnricher
from main import (
    get_balance, query_transactions, execute_transfer, get_credit_card_info,
    validate_positive, normalize_account_name, normalize_card_name,
    check_transfer_ready, has_txn_results,
    process_balance_query, display_balance, process_txn_query, display_txn_summary,
    display_txn_list, ask_transfer_info, confirm_transfer_details,
    display_transfer_result, process_credit_card_query, display_credit_card
)

def setup_engine():
    client = GlinerClient()
    engine = DialogEngine('config/banking_flow.json', client)
    duckling = DucklingEnricher()

    engine.actions.register("execute_transfer", execute_transfer)
    engine.validators.register_validator("validate_positive", validate_positive)
    engine.validators.register_enricher("enrich_amount_of_money", duckling.enrich_amount_of_money)
    engine.validators.register_enricher("enrich_time", duckling.enrich_time)
    engine.validators.register_enricher("normalize_account_name", normalize_account_name)
    engine.validators.register_enricher("normalize_card_name", normalize_card_name)
    engine.conditions.register("check_transfer_ready", check_transfer_ready)
    engine.conditions.register("has_txn_results", has_txn_results)
    engine.responses.register("process_balance_query", process_balance_query)
    engine.responses.register("display_balance", display_balance)
    engine.responses.register("process_txn_query", process_txn_query)
    engine.responses.register("process_credit_card_query", process_credit_card_query)
    engine.responses.register("display_txn_summary", display_txn_summary)
    engine.responses.register("display_txn_list", display_txn_list)
    engine.responses.register("ask_transfer_info", ask_transfer_info)
    engine.responses.register("confirm_transfer_details", confirm_transfer_details)
    engine.responses.register("display_transfer_result", display_transfer_result)
    engine.responses.register("display_credit_card", display_credit_card)

    return engine

def main():
    print("=" * 60)
    print("DEMO: Full Conversation (Sample from Requirements)")
    print("=" * 60)
    print("\nThis demonstrates switching between capabilities:\n")
    print("  1. Transaction Query (Amazon purchases)")
    print("  2. Credit Card Inquiry (travel card due)")
    print("  3. Balance Inquiry (spending account)")
    print("  4. Transfer (pay credit card)")
    print("  5. Farewell")
    print()

    engine = setup_engine()
    context = engine.start_session("demo_full")

    # The sample conversation from the requirements
    # Note: "transfer" phrasing works better than "pay" for GLiNER classification
    messages = [
        "What's the damage I did on Amazon purchases in the last 18 months?",
        "Can you show me those transactions?",
        "How much is due on my travel card?",
        "How much do I have in my spending account?",
        "Transfer 158 to my travel card from spending",
        "Yes",
        "Goodbye",
    ]

    print("─" * 60)

    for msg in messages:
        print(f"\n👤 User: {msg}")
        response = engine.process_turn(msg, context)
        print(f"\n🤖 Bot: {response}")
        print(f"\n   [State: {context.current_state}]")
        print("─" * 60)

    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
