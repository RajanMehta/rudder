"""Mock data for personal finance chatbot.

This module contains realistic mock data for bank accounts, credit cards,
and transactions. The data is designed to support the sample conversation
and be extensible for future UI development.
"""

from datetime import datetime, timedelta
from typing import Any
import random

# Seed for reproducible data
random.seed(42)

# =============================================================================
# ACCOUNTS
# =============================================================================

ACCOUNTS: dict[str, dict[str, Any]] = {
    "spending": {
        "id": "acct_001",
        "name": "Spending Account",
        "aliases": ["spending", "checking", "main", "primary", "debit"],
        "type": "CHECKING",
        "balance": 11556.00,
        "available_balance": 11556.00,
        "account_number_last4": "4521",
    },
    "savings": {
        "id": "acct_002",
        "name": "High-Yield Savings",
        "aliases": ["savings", "emergency", "rainy day", "high yield"],
        "type": "SAVINGS",
        "balance": 45230.00,
        "available_balance": 45230.00,
        "account_number_last4": "7832",
    },
    "vacation": {
        "id": "acct_003",
        "name": "Vacation Fund",
        "aliases": ["vacation", "travel fund", "trip", "holiday"],
        "type": "SAVINGS",
        "balance": 3200.00,
        "available_balance": 3200.00,
        "account_number_last4": "9104",
    },
    "joint": {
        "id": "acct_004",
        "name": "Joint Checking",
        "aliases": ["joint", "shared", "household", "family"],
        "type": "CHECKING",
        "balance": 8750.00,
        "available_balance": 8750.00,
        "account_number_last4": "2256",
    },
}

# =============================================================================
# CREDIT CARDS
# =============================================================================

CREDIT_CARDS: dict[str, dict[str, Any]] = {
    "travel_rewards": {
        "id": "cc_001",
        "name": "Travel Rewards Card",
        "aliases": ["travel", "travel card", "travel rewards", "rewards", "travel credit"],
        "type": "CREDIT_CARD",
        "current_balance": 158.00,  # Matches sample conversation
        "credit_limit": 15000.00,
        "available_credit": 14842.00,
        "minimum_payment": 40.00,
        "due_date": "2024-12-02",
        "apr": 18.99,
        "card_number_last4": "4892",
    },
    "cash_back": {
        "id": "cc_002",
        "name": "Cash Back Card",
        "aliases": ["cash back", "cashback", "everyday", "daily"],
        "type": "CREDIT_CARD",
        "current_balance": 567.23,
        "credit_limit": 8000.00,
        "available_credit": 7432.77,
        "minimum_payment": 25.00,
        "due_date": "2024-12-15",
        "apr": 21.99,
        "card_number_last4": "7621",
    },
    "business": {
        "id": "cc_003",
        "name": "Business Platinum",
        "aliases": ["business", "platinum", "work", "corporate"],
        "type": "CREDIT_CARD",
        "current_balance": 3421.89,
        "credit_limit": 25000.00,
        "available_credit": 21578.11,
        "minimum_payment": 85.00,
        "due_date": "2024-12-20",
        "apr": 16.99,
        "card_number_last4": "3345",
    },
}

# =============================================================================
# TRANSACTION GENERATION
# =============================================================================

CATEGORIES = [
    "Shopping",
    "Groceries",
    "Dining",
    "Entertainment",
    "Transportation",
    "Utilities",
    "Healthcare",
    "Travel",
]

MERCHANTS: dict[str, list[str]] = {
    "Shopping": ["Amazon", "Target", "Walmart", "Best Buy", "Apple Store", "Nike", "Costco", "Nordstrom", "Home Depot"],
    "Groceries": ["Whole Foods", "Trader Joe's", "Kroger", "Safeway", "Costco", "Sprouts"],
    "Dining": ["Starbucks", "Chipotle", "McDonald's", "Olive Garden", "Local Restaurant", "Panera Bread"],
    "Entertainment": ["Netflix", "Spotify", "AMC Theatres", "Steam", "Disney+", "Apple Music"],
    "Transportation": ["Uber", "Lyft", "Shell Gas", "Chevron", "BART", "Parking"],
    "Utilities": ["PG&E", "Comcast", "AT&T", "Water Company", "Verizon"],
    "Healthcare": ["CVS Pharmacy", "Kaiser", "Walgreens", "Doctor Visit"],
    "Travel": ["United Airlines", "Marriott", "Airbnb", "Delta Airlines", "Hilton", "Expedia"],
}

LOCATIONS = [
    "San Francisco, CA",
    "New York, NY",
    "Online",
    "Chicago, IL",
    "Seattle, WA",
    "Los Angeles, CA",
    "Austin, TX",
]


def _generate_amount_for_category(category: str) -> float:
    """Generate a realistic amount based on category."""
    ranges = {
        "Shopping": (15.00, 500.00),
        "Groceries": (25.00, 200.00),
        "Dining": (8.00, 100.00),
        "Entertainment": (10.00, 80.00),
        "Transportation": (5.00, 75.00),
        "Utilities": (50.00, 300.00),
        "Healthcare": (15.00, 200.00),
        "Travel": (100.00, 1500.00),
    }
    min_amt, max_amt = ranges.get(category, (10.00, 100.00))
    return round(random.uniform(min_amt, max_amt), 2)


def _generate_transactions(num_transactions: int = 500) -> list[dict[str, Any]]:
    """Generate random transactions for the last 24 months."""
    transactions = []
    end_date = datetime(2024, 11, 25)  # Fixed date for reproducibility
    start_date = end_date - timedelta(days=730)  # ~24 months

    all_account_ids = list(ACCOUNTS.keys()) + list(CREDIT_CARDS.keys())

    for i in range(num_transactions):
        category = random.choice(CATEGORIES)
        merchant = random.choice(MERCHANTS[category])
        amount = _generate_amount_for_category(category)

        # Random date within range
        days_ago = random.randint(0, 730)
        txn_date = end_date - timedelta(days=days_ago)

        # Random account
        account_key = random.choice(all_account_ids)
        if account_key in ACCOUNTS:
            account = ACCOUNTS[account_key]
        else:
            account = CREDIT_CARDS[account_key]

        # Location - online merchants are always "Online"
        if merchant in ["Amazon", "Netflix", "Spotify", "Disney+", "Steam", "Apple Music", "Expedia"]:
            location = "Online"
        else:
            location = random.choice(LOCATIONS)

        transactions.append({
            "id": f"txn_{i:05d}",
            "date": txn_date.strftime("%Y-%m-%d"),
            "datetime": txn_date.isoformat(),
            "merchant": merchant,
            "category": category,
            "amount": amount,
            "account_id": account["id"],
            "account_name": account["name"],
            "location": location,
            "status": "completed",
        })

    return transactions


def _generate_amazon_transactions() -> list[dict[str, Any]]:
    """Generate specific Amazon transactions for the sample conversation.

    The sample conversation mentions ~$5,074.77 spent on Amazon over 18 months.
    We'll create transactions that sum to approximately this amount.
    """
    amazon_txns = [
        {"date": "2024-11-15", "amount": 299.99, "account_key": "travel_rewards"},
        {"date": "2024-10-28", "amount": 156.45, "account_key": "spending"},
        {"date": "2024-10-05", "amount": 89.99, "account_key": "cash_back"},
        {"date": "2024-09-12", "amount": 432.15, "account_key": "travel_rewards"},
        {"date": "2024-08-20", "amount": 567.89, "account_key": "spending"},
        {"date": "2024-07-03", "amount": 234.56, "account_key": "travel_rewards"},
        {"date": "2024-06-15", "amount": 78.99, "account_key": "joint"},
        {"date": "2024-05-22", "amount": 345.00, "account_key": "business"},
        {"date": "2024-04-10", "amount": 189.99, "account_key": "spending"},
        {"date": "2024-03-05", "amount": 245.67, "account_key": "travel_rewards"},
        {"date": "2024-02-14", "amount": 99.00, "account_key": "spending"},
        {"date": "2024-01-08", "amount": 378.90, "account_key": "cash_back"},
        {"date": "2023-12-20", "amount": 456.19, "account_key": "travel_rewards"},
        {"date": "2023-11-24", "amount": 289.00, "account_key": "spending"},
        {"date": "2023-10-15", "amount": 167.50, "account_key": "joint"},
        {"date": "2023-09-08", "amount": 423.00, "account_key": "travel_rewards"},
        {"date": "2023-08-22", "amount": 134.99, "account_key": "spending"},
        {"date": "2023-07-11", "amount": 267.50, "account_key": "cash_back"},
        {"date": "2023-06-30", "amount": 189.00, "account_key": "spending"},
        {"date": "2023-05-25", "amount": 529.01, "account_key": "business"},
    ]

    transactions = []
    for i, txn in enumerate(amazon_txns):
        account_key = txn["account_key"]
        if account_key in ACCOUNTS:
            account = ACCOUNTS[account_key]
        else:
            account = CREDIT_CARDS[account_key]

        transactions.append({
            "id": f"txn_amz_{i:03d}",
            "date": txn["date"],
            "datetime": f"{txn['date']}T12:00:00",
            "merchant": "Amazon",
            "category": "Shopping",
            "amount": txn["amount"],
            "account_id": account["id"],
            "account_name": account["name"],
            "location": "Online",
            "status": "completed",
        })

    return transactions


# Generate all transactions
_base_transactions = _generate_transactions(480)
_amazon_transactions = _generate_amazon_transactions()

# Remove any randomly generated Amazon transactions to avoid duplicates
_base_transactions = [t for t in _base_transactions if t["merchant"] != "Amazon"]

# Combine and sort by date descending
TRANSACTIONS: list[dict[str, Any]] = _base_transactions + _amazon_transactions
TRANSACTIONS.sort(key=lambda x: x["date"], reverse=True)
