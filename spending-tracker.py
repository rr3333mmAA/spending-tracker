import argparse
import json
import os
import datetime
import uuid

"""
Example usage:
python spending-tracker.py add "Coffee" 3.50
"""

STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spendings.json")

class Spending:
    def __init__(self, item, amount, category="Other", id=None, date=None):
        self.id = id or str(uuid.uuid4())
        self.item = item
        self.amount = amount
        self.category = category
        self.date = date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "item": self.item,
            "amount": self.amount,
            "category": self.category,
            "date": self.date
        }

class SpendingTracker:
    def __init__(self):
        self.spendings: list[Spending] = []

    def load_spendings(self):
        """Load spendings from the storage file."""
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                data = json.load(f)
                self.spendings = [Spending(**item) for item in data]
        else:
            self.spendings = []
    
    def save_spendings(self):
        """Save spendings to the storage file."""
        with open(STORAGE_FILE, 'w') as f:
            json.dump([spending.to_dict() for spending in self.spendings], f, indent=4)

    def append_spending(self, item, amount, category="Other", date=None):
        """Append a new spending item."""
        spending = Spending(item, amount, category=category, date=date)
        self.spendings.append(spending)
        self.save_spendings()

    def get_total_spendings(self):
        """Calculate the total amount of spendings."""
        return sum(spending.amount for spending in self.spendings)

    def overview(self, currency_rate=1.0):
        conversion_note = f" (converted at rate {currency_rate})" if currency_rate != 1.0 else ""
        overview = f"\nCurrent spendings{conversion_note}:\n"
        for spending in self.spendings:
            converted_amount = spending.amount * currency_rate
            overview += f"{spending.item}: {converted_amount:.2f} (on {spending.date})\n"
        total = self.get_total_spendings() * currency_rate
        overview += f"\nTotal spendings: {total:.2f}\n"
        return overview

    def delete_spending(self, spending_id):
        """Delete a spending item by its ID."""
        self.spendings = [spending for spending in self.spendings if spending.id != spending_id]
        self.save_spendings()
        print(f"Spending with ID {spending_id} has been deleted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple command-line tool for tracking spendings.")
    subparsers = parser.add_subparsers(dest="command")

    # ---- Add command ----
    add_parser = subparsers.add_parser("add", help="Add a spending entry.")
    add_parser.add_argument("item", help="Item description, e.g. 'Coffee'")
    add_parser.add_argument("amount", type=float, help="Amount spent (numeric).")
    add_parser.add_argument("--category", default="Other",
                            help="Category (default: Other).")
    add_parser.add_argument("--date", help="Date (YYYY-MM-DD). Defaults to today.")

    # ---- List command ----
    list_parser = subparsers.add_parser("list", help="List spending entries.")
    list_parser.add_argument("--currency-rate", type=float, default=1.0,
                            help="Currency conversion rate (default: 1.0).")
    # list_parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    # list_parser.add_argument("--to", dest="date_to", help="End date YYYY-MM-DD")
    # list_parser.add_argument("--category", help="Filter by category")
    # list_parser.add_argument("--all", action="store_true", help="Show all entries (ignore date).")

    # ---- Delete command ----
    del_parser = subparsers.add_parser("delete", help="Delete an entry by ID.")
    del_parser.add_argument("id", type=int, help="ID of the entry to delete.")

    args = parser.parse_args()
    
    tracker = SpendingTracker()
    tracker.load_spendings()

    if args.command == "add":
        # Convert date to datetime object if provided
        date = None
        if args.date:
            try:
                date = datetime.datetime.strptime(args.date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                exit(1)
        tracker.append_spending(args.item, args.amount, category=args.category, date=date)

    elif args.command == "list":
        if tracker.spendings:
            print(tracker.overview(currency_rate=args.currency_rate))
        else:
            print("No spendings recorded yet.")

    elif args.command == "delete":
        if tracker.spendings:
            tracker.delete_spending(args.id)
        else:
            print("No spendings recorded yet.")

    else:
        parser.print_help()
        exit(1)