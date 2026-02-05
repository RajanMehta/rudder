"""Data access layer for personal finance chatbot.

This module provides functions to query and filter mock data for accounts,
credit cards, and transactions.
"""

from typing import Any, Optional
from datetime import datetime

from .mock_data import ACCOUNTS, CREDIT_CARDS, TRANSACTIONS


def find_account_by_name(name: str) -> Optional[dict[str, Any]]:
    """Find an account (bank account or credit card) by name or alias.

    Args:
        name: Account name or alias (case-insensitive)

    Returns:
        Account dict if found, None otherwise
    """
    if not name:
        return None

    name_lower = name.lower().strip()

    # Check bank accounts first
    for key, account in ACCOUNTS.items():
        if name_lower == key:
            return account
        if name_lower in [a.lower() for a in account.get("aliases", [])]:
            return account
        if name_lower in account["name"].lower():
            return account

    # Then check credit cards
    for key, card in CREDIT_CARDS.items():
        if name_lower == key:
            return card
        if name_lower in [a.lower() for a in card.get("aliases", [])]:
            return card
        if name_lower in card["name"].lower():
            return card

    return None


def find_credit_card_by_name(name: str) -> Optional[dict[str, Any]]:
    """Find a credit card by name or alias.

    Args:
        name: Card name or alias (case-insensitive)

    Returns:
        Credit card dict if found, None otherwise
    """
    if not name:
        return None

    name_lower = name.lower().strip()

    for key, card in CREDIT_CARDS.items():
        if name_lower == key:
            return card
        if name_lower in [a.lower() for a in card.get("aliases", [])]:
            return card
        if name_lower in card["name"].lower():
            return card

    return None


def get_all_accounts() -> list[dict[str, Any]]:
    """Get all bank accounts (checking and savings).

    Returns:
        List of account dicts
    """
    return list(ACCOUNTS.values())


def get_all_credit_cards() -> list[dict[str, Any]]:
    """Get all credit cards.

    Returns:
        List of credit card dicts
    """
    return list(CREDIT_CARDS.values())


def filter_transactions(
    merchant: Optional[str] = None,
    category: Optional[str] = None,
    amount_filter: Optional[str] = None,
    amount_threshold: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    account_id: Optional[str] = None,
    account_name: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Filter transactions based on various criteria.

    Args:
        merchant: Filter by merchant name (partial match, case-insensitive)
        category: Filter by category (partial match, case-insensitive)
        amount_filter: "over" or "under" to filter by amount threshold
        amount_threshold: Amount to compare against (requires amount_filter)
        start_date: Filter transactions on or after this date (YYYY-MM-DD)
        end_date: Filter transactions on or before this date (YYYY-MM-DD)
        location: Filter by location (partial match, case-insensitive)
        account_id: Filter by specific account ID
        account_name: Filter by account name (will lookup account_id)

    Returns:
        List of matching transaction dicts
    """
    results = TRANSACTIONS.copy()

    # Filter by merchant
    if merchant:
        merchant_lower = merchant.lower()
        results = [t for t in results if merchant_lower in t["merchant"].lower()]

    # Filter by category
    if category:
        category_lower = category.lower()
        results = [t for t in results if category_lower in t["category"].lower()]

    # Filter by amount
    if amount_filter and amount_threshold is not None:
        if amount_filter.lower() == "over":
            results = [t for t in results if t["amount"] > amount_threshold]
        elif amount_filter.lower() == "under":
            results = [t for t in results if t["amount"] < amount_threshold]

    # Filter by date range
    if start_date:
        results = [t for t in results if t["date"] >= start_date]

    if end_date:
        results = [t for t in results if t["date"] <= end_date]

    # Filter by location
    if location:
        location_lower = location.lower()
        results = [t for t in results if location_lower in t["location"].lower()]

    # Filter by account
    if account_id:
        results = [t for t in results if t["account_id"] == account_id]
    elif account_name:
        account = find_account_by_name(account_name)
        if account:
            results = [t for t in results if t["account_id"] == account["id"]]

    return results


def calculate_txn_summary(transactions: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate summary statistics for a list of transactions.

    Args:
        transactions: List of transaction dicts

    Returns:
        Summary dict with total, count, avg, accounts, date range
    """
    if not transactions:
        return {
            "total": 0,
            "count": 0,
            "avg": 0,
            "accounts": 0,
            "earliest_date": None,
            "latest_date": None,
        }

    total = sum(t["amount"] for t in transactions)
    count = len(transactions)
    unique_accounts = len(set(t["account_id"] for t in transactions))
    dates = [t["date"] for t in transactions]

    return {
        "total": round(total, 2),
        "count": count,
        "avg": round(total / count, 2),
        "accounts": unique_accounts,
        "earliest_date": min(dates),
        "latest_date": max(dates),
    }


def format_date_for_display(date_str: str) -> str:
    """Format a date string for human-readable display.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Formatted date like "November 25th, 2024"
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return dt.strftime(f"%B {day}{suffix}, %Y")
    except ValueError:
        return date_str


def format_currency(amount: float) -> str:
    """Format an amount as currency.

    Args:
        amount: Amount to format

    Returns:
        Formatted string like "$1,234.56"
    """
    return f"${amount:,.2f}"
