"""Personal Finance Chatbot using Rudder Dialog Engine.

This module sets up the dialog engine with all custom actions, validators,
enrichers, conditions, and response functions for a personal finance assistant.
"""

import sys
import os
from datetime import datetime

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import DialogEngine
from core.gliner_client import GlinerClient
from core.duckling_enrichers import DucklingEnricher
from data.data_access import (
    find_account_by_name,
    find_credit_card_by_name,
    get_all_accounts,
    get_all_credit_cards,
    filter_transactions,
    calculate_txn_summary,
    format_date_for_display,
    format_currency,
)


# =============================================================================
# ACTION FUNCTIONS
# =============================================================================


def get_balance(context):
    """Get balance for a specific account or all accounts.

    If account slot is provided, returns that account's balance.
    Otherwise, returns all account balances.
    """
    account_name = context.slots.get("account")

    if account_name:
        # Single account lookup
        account = find_account_by_name(account_name)
        if not account:
            return "not_found"
        context.slots["account_data"] = account
        context.slots["balance_type"] = "single"
    else:
        # All accounts
        accounts = get_all_accounts()
        cards = get_all_credit_cards()
        context.slots["all_accounts"] = accounts
        context.slots["all_cards"] = cards
        context.slots["balance_type"] = "all"

    return "success"


def query_transactions(context):
    """Query transactions based on filters in slots."""
    filters = {}

    if context.slots.get("merchant"):
        filters["merchant"] = context.slots["merchant"]

    if context.slots.get("category"):
        filters["category"] = context.slots["category"]

    if context.slots.get("amount_filter"):
        filters["amount_filter"] = context.slots["amount_filter"]

    if context.slots.get("amount_threshold"):
        threshold = context.slots["amount_threshold"]
        if isinstance(threshold, dict):
            filters["amount_threshold"] = threshold.get("value", 0)
        else:
            try:
                filters["amount_threshold"] = float(threshold)
            except (ValueError, TypeError):
                pass

    # Handle date range from Duckling
    if context.slots.get("date_range"):
        date_val = context.slots["date_range"]
        if isinstance(date_val, dict):
            if date_val.get("type") == "interval":
                from_val = date_val.get("from", {})
                to_val = date_val.get("to", {})
                if from_val.get("value"):
                    filters["start_date"] = from_val["value"][:10]
                if to_val.get("value"):
                    filters["end_date"] = to_val["value"][:10]
            elif date_val.get("value"):
                # Single date - interpret as "since this date"
                filters["start_date"] = date_val["value"][:10]

    if context.slots.get("location"):
        filters["location"] = context.slots["location"]

    if context.slots.get("account"):
        filters["account_name"] = context.slots["account"]

    # Execute query
    transactions = filter_transactions(**filters)

    if not transactions:
        return "none_found"

    context.slots["txn_results"] = transactions
    context.slots["txn_summary"] = calculate_txn_summary(transactions)
    return "found"


def execute_transfer(context):
    """Execute a money transfer."""
    amount = context.slots.get("transfer_amount")
    if isinstance(amount, dict):
        amount = amount.get("value", 0)
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        context.slots["transfer_error"] = "Invalid amount"
        return "error"

    source_name = context.slots.get("source_account", "spending")
    dest_name = context.slots.get("destination_account")

    source = find_account_by_name(source_name)
    dest = find_account_by_name(dest_name)

    if not dest:
        context.slots["transfer_error"] = f"Could not find destination account: {dest_name}"
        return "invalid_account"

    if not source:
        source = find_account_by_name("spending")  # Default source

    # Check sufficient funds
    available = source.get("available_balance", source.get("available_credit", 0))
    if amount > available:
        context.slots["transfer_error"] = f"Insufficient funds. Available: {format_currency(available)}"
        context.slots["source_balance"] = available
        return "insufficient_funds"

    # Mock successful transfer
    transfer_date = context.slots.get("transfer_date", "today")
    if isinstance(transfer_date, dict):
        transfer_date = transfer_date.get("value", "today")
        if transfer_date != "today":
            transfer_date = transfer_date[:10]

    context.slots["transfer_confirmation"] = {
        "amount": amount,
        "source": source["name"],
        "destination": dest["name"],
        "date": transfer_date,
        "confirmation_number": f"{datetime.now().strftime('%Y%m%d%H%M%S')[-6:]}",
    }

    return "success"


def get_credit_card_info(context):
    """Get info for a specific credit card or all cards."""
    card_name = context.slots.get("card_name")

    if card_name:
        # Single card lookup
        card = find_credit_card_by_name(card_name)
        if not card:
            return "not_found"
        context.slots["card_data"] = card
        context.slots["card_type"] = "single"
    else:
        # All cards
        cards = get_all_credit_cards()
        context.slots["all_cards"] = cards
        context.slots["card_type"] = "all"

    return "success"


# =============================================================================
# VALIDATORS
# =============================================================================


def validate_positive(value):
    """Validate that a value is positive."""
    try:
        if isinstance(value, dict):
            val = value.get("value", 0)
        elif isinstance(value, list) and len(value) > 0:
            val = value[0].get("text", 0) if isinstance(value[0], dict) else value[0]
        else:
            val = value
        return float(val) > 0
    except (ValueError, TypeError):
        return False


# =============================================================================
# ENRICHERS
# =============================================================================


def normalize_account_name(value):
    """Normalize account name to standard form."""
    if isinstance(value, dict):
        text = value.get("text", value.get("value", ""))
    elif isinstance(value, list) and len(value) > 0:
        text = value[0].get("text", str(value[0])) if isinstance(value[0], dict) else str(value[0])
    else:
        text = str(value) if value else ""

    # Map common variations to standard names
    aliases = {
        "checking": "spending",
        "main": "spending",
        "primary": "spending",
        "debit": "spending",
        "emergency": "savings",
        "rainy day": "savings",
        "high yield": "savings",
        "travel fund": "vacation",
        "trip": "vacation",
        "holiday": "vacation",
        "shared": "joint",
        "household": "joint",
        "family": "joint",
    }

    normalized = text.lower().strip()
    return aliases.get(normalized, normalized)


def normalize_card_name(value):
    """Normalize credit card name to standard form."""
    if isinstance(value, dict):
        text = value.get("text", value.get("value", ""))
    elif isinstance(value, list) and len(value) > 0:
        text = value[0].get("text", str(value[0])) if isinstance(value[0], dict) else str(value[0])
    else:
        text = str(value) if value else ""

    aliases = {
        "travel": "travel_rewards",
        "travel card": "travel_rewards",
        "travel rewards": "travel_rewards",
        "rewards": "travel_rewards",
        "travel credit": "travel_rewards",
        "cash back": "cash_back",
        "cashback": "cash_back",
        "everyday": "cash_back",
        "daily": "cash_back",
        "platinum": "business",
        "work": "business",
        "corporate": "business",
    }

    normalized = text.lower().strip()
    return aliases.get(normalized, normalized)


# =============================================================================
# CONDITION FUNCTIONS
# =============================================================================


def check_transfer_ready(context, target_state):
    """Check if transfer has required slots filled."""
    required = ["transfer_amount", "destination_account"]
    if all(context.slots.get(k) for k in required):
        return target_state
    return context.current_state  # Stay here if not filled


def has_txn_results(context, target_state):
    """Check if we have transaction results to display."""
    if context.slots.get("txn_results"):
        return target_state
    return context.current_state


# =============================================================================
# RESPONSE FUNCTIONS
# =============================================================================


def process_balance_query(context):
    """Process balance query - extract account and return balance.

    This response function runs the balance action and returns results.
    """
    result = get_balance(context)

    if result == "not_found":
        account_name = context.slots.get("account", "unknown")
        return f"I couldn't find an account matching '{account_name}'. Please try a different account name."
    elif result == "error":
        return "I encountered an error while fetching your balance. Please try again."

    return display_balance(context)


def display_balance(context):
    """Display balance for single account or all accounts."""
    balance_type = context.slots.get("balance_type", "single")

    if balance_type == "single":
        account = context.slots.get("account_data", {})
        name = account.get("name", "Unknown")
        balance = account.get("available_balance", account.get("available_credit", 0))
        return f"The available balance for your {name} is {format_currency(balance)}."
    else:
        # All accounts
        accounts = context.slots.get("all_accounts", [])
        cards = context.slots.get("all_cards", [])

        lines = ["Here are all your account balances:\n"]

        lines.append("Bank Accounts:")
        for acct in accounts:
            lines.append(f"  - {acct['name']}: {format_currency(acct['available_balance'])}")

        lines.append("\nCredit Cards:")
        for card in cards:
            lines.append(
                f"  - {card['name']}: {format_currency(card['current_balance'])} balance "
                f"({format_currency(card['available_credit'])} available)"
            )

        return "\n".join(lines)


def process_txn_query(context):
    """Process transaction query - extract filters and run query.

    This response function acts as a hybrid - it extracts entities,
    runs the query action, and returns the summary.
    """
    # Run the query action directly
    result = query_transactions(context)

    if result == "none_found":
        return "No transactions found matching your criteria. Would you like to try different filters?"
    elif result == "error":
        return "I encountered an error while searching for transactions. Please try again."

    # Return the summary
    return display_txn_summary(context)


def display_txn_summary(context):
    """Display transaction summary."""
    summary = context.slots.get("txn_summary", {})
    merchant = context.slots.get("merchant", "")
    category = context.slots.get("category", "")
    amount_filter = context.slots.get("amount_filter", "")
    amount_threshold = context.slots.get("amount_threshold", "")

    # Build response
    response = f"You spent {format_currency(summary.get('total', 0))}"

    if summary.get("accounts", 0) > 1:
        response += f" from your {summary['accounts']} accounts"

    if merchant:
        response += f" on purchases at {merchant}"
    elif category:
        response += f" on {category}"

    if summary.get("earliest_date") and summary.get("latest_date"):
        response += f" from {format_date_for_display(summary['earliest_date'])} to {format_date_for_display(summary['latest_date'])}"

    if amount_filter and amount_threshold:
        threshold_val = amount_threshold
        if isinstance(threshold_val, dict):
            threshold_val = threshold_val.get("value", 0)
        response += f" (amounts {amount_filter} {format_currency(float(threshold_val))})"

    response += f", which was {summary.get('count', 0)} transactions total."

    # Calculate percentage of total spending (mock)
    total_spending = 99750.00  # Mock total spending
    percentage = (summary.get("total", 0) / total_spending) * 100
    response += f" That's {percentage:.2f}% of your total spending."

    response += "\n\nWould you like to see the transaction details?"

    return response


def display_txn_list(context):
    """Display detailed transaction list."""
    transactions = context.slots.get("txn_results", [])

    if not transactions:
        return "No transactions to display."

    # Build filter description
    filters_desc = []
    if context.slots.get("merchant"):
        filters_desc.append(f"at {context.slots['merchant']}")
    if context.slots.get("amount_filter") and context.slots.get("amount_threshold"):
        threshold = context.slots["amount_threshold"]
        if isinstance(threshold, dict):
            threshold = threshold.get("value", 0)
        filters_desc.append(f"{context.slots['amount_filter']} {format_currency(float(threshold))}")

    filter_str = " ".join(filters_desc) if filters_desc else ""
    summary = context.slots.get("txn_summary", {})

    lines = []
    if filter_str:
        lines.append(f"Here are your purchases {filter_str} from {format_date_for_display(summary.get('earliest_date', ''))} to {format_date_for_display(summary.get('latest_date', ''))}:\n")
    else:
        lines.append("Here are your transactions:\n")

    # Display up to 15 transactions
    display_txns = transactions[:15]
    for txn in display_txns:
        lines.append(
            f"  {txn['date']} | {txn['merchant']:20} | {format_currency(txn['amount']):>10} | {txn['account_name']}"
        )

    if len(transactions) > 15:
        lines.append(f"\n(Showing first 15 of {len(transactions)} transactions)")

    lines.append("\nWhat else can I help you with?")

    return "\n".join(lines)


def ask_transfer_info(context):
    """Ask for missing transfer information."""
    has_amount = bool(context.slots.get("transfer_amount"))
    has_dest = bool(context.slots.get("destination_account"))
    has_source = bool(context.slots.get("source_account"))

    if not has_amount and not has_dest:
        return "How much would you like to transfer, and to which account?"
    if not has_amount:
        return "How much would you like to transfer?"
    if not has_dest:
        return "Which account would you like to transfer to?"
    if not has_source:
        return "Which account would you like to transfer from? (I'll use your spending account if you don't specify.)"

    # All required info present
    return "Let me prepare that transfer for you."


def confirm_transfer_details(context):
    """Confirm transfer details before execution."""
    amount = context.slots.get("transfer_amount")
    if isinstance(amount, dict):
        amount = amount.get("value", 0)

    dest = context.slots.get("destination_account", "unknown")
    source = context.slots.get("source_account", "spending")
    date = context.slots.get("transfer_date", "today")

    # Format date nicely if it's a dict from Duckling
    if isinstance(date, dict):
        date_val = date.get("value", "today")
        if date_val != "today":
            date = format_date_for_display(date_val[:10])
        else:
            date = "today"

    # Look up friendly names
    dest_account = find_account_by_name(dest)
    source_account = find_account_by_name(source)

    dest_name = dest_account["name"] if dest_account else dest
    source_name = source_account["name"] if source_account else source

    return (
        f"I have the amount to be {format_currency(float(amount))}, "
        f"the destination account to be {dest_name}, "
        f"the source account to be {source_name}, "
        f"and the date to be {date}. "
        f"Can you confirm this is correct?"
    )


def display_transfer_result(context):
    """Display transfer result (success or error)."""
    conf = context.slots.get("transfer_confirmation")

    if conf:
        # Success
        return (
            f"Your payment request is complete. {format_currency(conf.get('amount', 0))} has been transferred "
            f"from {conf.get('source', 'your account')} to {conf.get('destination', 'destination')}. "
            f"Here is the confirmation number for your reference: {conf.get('confirmation_number', 'N/A')}. "
            f"What else can I help you with?"
        )
    else:
        # Error
        error_msg = context.slots.get("transfer_error", "Unknown error")
        return f"I'm sorry, the transfer could not be completed. {error_msg}. Would you like to try again?"


def process_credit_card_query(context):
    """Process credit card query - extract card name and return info.

    This response function runs the credit card action and returns results.
    """
    result = get_credit_card_info(context)

    if result == "not_found":
        card_name = context.slots.get("card_name", "unknown")
        return f"I couldn't find a credit card matching '{card_name}'. Please try a different card name."
    elif result == "error":
        return "I encountered an error while fetching your credit card info. Please try again."

    return display_credit_card(context)


def display_credit_card(context):
    """Display credit card information."""
    card_type = context.slots.get("card_type", "single")

    if card_type == "single":
        card = context.slots.get("card_data", {})
        due_date = format_date_for_display(card.get("due_date", ""))

        return (
            f"Your {card.get('name', 'card')} has a minimum payment of "
            f"{format_currency(card.get('minimum_payment', 0))} due on {due_date}. "
            f"Your account balance is {format_currency(card.get('current_balance', 0))}."
        )
    else:
        # All cards
        cards = context.slots.get("all_cards", [])

        lines = ["Here's the information for all your credit cards:\n"]

        for card in cards:
            due_date = format_date_for_display(card.get("due_date", ""))
            lines.append(f"{card['name']}:")
            lines.append(f"  Balance: {format_currency(card['current_balance'])}")
            lines.append(f"  Available Credit: {format_currency(card['available_credit'])}")
            lines.append(f"  Minimum Payment: {format_currency(card['minimum_payment'])} due {due_date}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config", "banking_flow.json")
    client = GlinerClient()
    engine = DialogEngine(config_path, client)

    # Register Actions
    engine.actions.register("get_balance", get_balance)
    engine.actions.register("query_transactions", query_transactions)
    engine.actions.register("execute_transfer", execute_transfer)
    engine.actions.register("get_credit_card_info", get_credit_card_info)

    # Register Validators
    engine.validators.register_validator("validate_positive", validate_positive)

    # Register Enrichers
    duckling = DucklingEnricher()
    engine.validators.register_enricher("enrich_amount_of_money", duckling.enrich_amount_of_money)
    engine.validators.register_enricher("enrich_time", duckling.enrich_time)
    engine.validators.register_enricher("normalize_account_name", normalize_account_name)
    engine.validators.register_enricher("normalize_card_name", normalize_card_name)

    # Register Conditions
    engine.conditions.register("check_transfer_ready", check_transfer_ready)
    engine.conditions.register("has_txn_results", has_txn_results)

    # Register Response Functions
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

    context = engine.start_session("session_123")

    print("--- Personal Finance Assistant (Type 'exit' to quit) ---")

    # Initial Greeting
    initial_state = engine.states[context.current_state]
    print(f"Bot: {initial_state.get('response_template', 'Hello!')}")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        response = engine.process_turn(user_input, context)
        print(f"Bot: {response}")


if __name__ == "__main__":
    main()
