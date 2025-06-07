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
    def __init__(self, item, amount, currency="usd", category="Other", id=None, date=None):
        self.id = id or str(uuid.uuid4())
        self.item = item
        self.amount = amount
        self.currency = currency
        self.category = category
        self.date = date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "item": self.item,
            "amount": self.amount,
            "currency": self.currency,
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

    def append_spending(self, item, amount, currency="usd", category="Other", date=None):
        """Append a new spending item."""
        spending = Spending(item, amount, currency=currency, category=category, date=date)
        self.spendings.append(spending)
        self.save_spendings()

    def get_total_spendings(self):
        """Calculate the total amount of spendings."""
        total_spendings = dict()
        for spending in self.spendings:
            if spending.currency not in total_spendings:
                total_spendings[spending.currency] = 0
            total_spendings[spending.currency] += spending.amount
        return total_spendings

    def overview(self, from_date=None, to_date=None, category=None):
        overview = f"\nCurrent spendings:\n"
        for spending in self.spendings:
            spending.date = datetime.datetime.strptime(spending.date, "%Y-%m-%d %H:%M:%S")
            if category and spending.category != category:
                continue
            if from_date and spending.date < from_date:
                continue
            if to_date and spending.date > to_date:
                continue
            overview += f"{spending.item}: {spending.amount:.2f} {spending.currency} ({spending.category}, on {spending.date})\n"
        total = self.get_total_spendings()
        overview += "\nTotal spendings: "
        for currency, amount in total.items():
            overview += f"{amount:.2f} {currency}, "
        overview = overview[:-2] + "\n"
        return overview

    def delete_spending(self, spending_id):
        """Delete a spending item by its ID."""
        self.spendings = [spending for spending in self.spendings if spending.id != spending_id]
        self.save_spendings()
        print(f"Spending with ID {spending_id} has been deleted.")

    def edit_spending(self, spending_id, item=None, amount=None, currency=None, category=None):
        """Edit a spending item by its ID."""
        for spending in self.spendings:
            if spending.id == spending_id:
                if item is not None:
                    spending.item = item
                if amount is not None:
                    spending.amount = amount
                if currency is not None:
                    spending.currency = currency
                if category is not None:
                    spending.category = category
                self.save_spendings()
                print(f"Spending with ID {spending_id} has been updated.")
                return
        print(f"No spending found with ID {spending_id}.")

def parser():
    parser_ = argparse.ArgumentParser(description="A simple command-line tool for tracking spendings.")
    subparsers = parser_.add_subparsers(dest="command")

    # ---- Add command ----
    add_parser = subparsers.add_parser("add", help="Add a spending entry.")
    add_parser.add_argument("item", help="Item description, e.g. 'Coffee'")
    add_parser.add_argument("amount", type=float, help="Amount spent (numeric).")
    add_parser.add_argument("--currency", default="usd",
                            help="Currency (default: usd).")
    add_parser.add_argument("--category", default="Other",
                            help="Category (default: Other).")
    add_parser.add_argument("--date", help="Date (YYYY-MM-DD). Defaults to today.")

    # ---- List command ----
    list_parser = subparsers.add_parser("list", help="List spending entries.")
    list_parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    list_parser.add_argument("--to", dest="date_to", help="End date YYYY-MM-DD")
    list_parser.add_argument("--category", help="Filter by category")

    # ---- Delete command ----
    del_parser = subparsers.add_parser("delete", help="Delete an entry by ID.")
    del_parser.add_argument("id", help="ID of the entry to delete.")

    # ---- Edit command ----
    edit_parser = subparsers.add_parser("edit", help="Edit an entry by ID.")
    edit_parser.add_argument("id", help="ID of the entry to edit.")
    edit_parser.add_argument("--item", help="New item description")
    edit_parser.add_argument("--amount", type=float, help="New amount spent")
    edit_parser.add_argument("--currency", help="New currency")
    edit_parser.add_argument("--category", help="New category")

    return parser_

if __name__ == "__main__":
    parser_ = parser()
    args = parser_.parse_args()

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
        tracker.append_spending(args.item, args.amount, currency=args.currency, category=args.category, date=date)

    elif args.command == "list":
        if tracker.spendings:
            from_date = datetime.datetime.strptime(args.date_from, "%Y-%m-%d") if args.date_from else None
            to_date = datetime.datetime.strptime(args.date_to, "%Y-%m-%d") if args.date_to else None
            print(tracker.overview(from_date=from_date, to_date=to_date, category=args.category))
        else:
            print("No spendings recorded yet.")

    elif args.command == "delete":
        if tracker.spendings:
            tracker.delete_spending(args.id)
        else:
            print("No spendings recorded yet.")

    elif args.command == "edit":
        if tracker.spendings:
            tracker.edit_spending(args.id, item=args.item, amount=args.amount, currency=args.currency, category=args.category)
        else:
            print("No spendings recorded yet.")

    else:
        parser_.print_help()
        exit(1)