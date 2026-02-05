#!/usr/bin/env python3
"""Demo: Interactive Chat

Run an interactive session with the personal finance assistant.
Type 'quit' or 'exit' to end the session.
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

def print_help():
    print("""
╔════════════════════════════════════════════════════════════╗
║           Personal Finance Assistant - Help                ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  BALANCE INQUIRIES                                         ║
║    • "What's my balance?"                                  ║
║    • "How much in my spending account?"                    ║
║    • "Show me all my balances"                             ║
║                                                            ║
║  TRANSACTION QUERIES                                       ║
║    • "Show me my Amazon purchases"                         ║
║    • "What did I spend on groceries last month?"           ║
║    • "Transactions over $100"                              ║
║                                                            ║
║  CREDIT CARD INFO                                          ║
║    • "How much is due on my travel card?"                  ║
║    • "Show me my credit cards"                             ║
║                                                            ║
║  TRANSFERS                                                 ║
║    • "Transfer $100 from savings to spending"              ║
║    • "Pay $50 to my travel card"                           ║
║                                                            ║
║  COMMANDS                                                  ║
║    • help  - Show this help message                        ║
║    • state - Show current state and slots                  ║
║    • quit  - Exit the demo                                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

def main():
    print("=" * 60)
    print("DEMO: Interactive Personal Finance Assistant")
    print("=" * 60)
    print("\nLoading models...")

    engine = setup_engine()
    context = engine.start_session("interactive")

    print("\n✅ Ready! Type 'help' for example commands.\n")
    print("─" * 60)
    print("🤖 Bot: Hello! I'm your personal finance assistant.")
    print("        How can I help you today?")
    print("─" * 60)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye! Have a great day!")
            break

        if user_input.lower() == 'help':
            print_help()
            continue

        if user_input.lower() == 'state':
            print(f"\n📍 Current State: {context.current_state}")
            print(f"📦 Slots: {dict(context.slots)}")
            continue

        response = engine.process_turn(user_input, context)
        print(f"\n🤖 Bot: {response}")
        print(f"\n   [State: {context.current_state}]")

if __name__ == "__main__":
    main()
