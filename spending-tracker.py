import argparse
import json
import os
import datetime
import uuid

"""
Example: python3 spending-tracker.py --add "Coffee" 3.50 --add "Lunch" 12.00 --view 
"""

STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spendings.json")

class Spending:
    def __init__(self, item, amount, id=None, date=None):
        self.id = id or str(uuid.uuid4())
        self.item = item
        self.amount = amount
        self.date = date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "id": self.id,
            "item": self.item,
            "amount": self.amount,
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
    
    def append_spending(self, item, amount):
        """Append a new spending item."""
        spending = Spending(item, amount)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple command-line tool for tracking spendings.")
    parser.add_argument("--add", nargs=2, action='append', metavar=("item", "amount"), 
                      help="Add a spending item with its amount. Can be used multiple times.")
    parser.add_argument("--view", action="store_true", help="View all spending items.")
    parser.add_argument("--currency-rate", type=float, help="Currency conversion rate for viewing amounts (e.g., 0.85 for USD to EUR).", default=1.0)
    args = parser.parse_args()
    
    tracker = SpendingTracker()
    tracker.load_spendings()
    
    if args.add:
        for item_amount in args.add:
            item, amount = item_amount
            try:
                amount = float(amount)
                tracker.append_spending(item, amount)
                print(f"Added spending: {item} - {amount:.2f}")
            except ValueError:
                print(f"Invalid amount '{amount}' for item '{item}'. Please provide a valid number.")

    if args.view:
        print(tracker.overview(args.currency_rate))
        
    if not args.add and not args.view:
        parser.print_help()