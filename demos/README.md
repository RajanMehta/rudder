# Demo Scripts

Interactive demos for the Personal Finance Assistant.

## Running Demos

All demos should be run from the project root with Docker:

```bash
# Start containers
docker compose up -d

# Run a specific demo
docker compose exec app python demos/demo_balance.py
docker compose exec app python demos/demo_transactions.py
docker compose exec app python demos/demo_transfer.py
docker compose exec app python demos/demo_full_conversation.py
docker compose exec app python demos/demo_interactive.py
```

Or use Make targets:

```bash
make demo-balance
make demo-transactions
make demo-transfer
make demo-full
make demo-interactive
```

## Available Demos

### demo_balance.py
Tests balance inquiries for single accounts and all accounts.

### demo_transactions.py
Tests transaction filtering by merchant, date range, and amount.

### demo_transfer.py
Tests the complete transfer flow with confirmation and cancellation.

### demo_full_conversation.py
Demonstrates the sample conversation from requirements, switching between:
1. Transaction queries (Amazon purchases)
2. Credit card inquiry (travel card due)
3. Balance inquiry (spending account)
4. Transfer (pay credit card)
5. Farewell

### demo_interactive.py
Interactive chat session. Type your own messages and explore the assistant.
Commands:
- `help` - Show example commands
- `state` - Show current state and slots
- `quit` - Exit

## Sample Inputs to Try

**Balance:**
- "What's my balance?"
- "How much in my spending account?"
- "Show me my savings balance"

**Transactions:**
- "Show me Amazon purchases"
- "What did I spend at Starbucks?"
- "Groceries last month"
- "Transactions over $50"

**Credit Cards:**
- "How much is due on my travel card?"
- "Show my credit cards"

**Transfers:**
- "Transfer $100 from savings to spending"
- "Pay $158 to my travel card from spending"
