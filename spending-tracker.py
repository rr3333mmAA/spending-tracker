import argparse
import json
import os

"""
Example: python3 spending-tracker.py --add "Coffee" 3.50 --add "Lunch" 12.00 --view 
"""

STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spendings.json")

def load_spendings():
    """Load spendings from the storage file."""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_spendings(spendings):
    """Save spendings to the storage file."""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(spendings, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple command-line tool for tracking spendings.")
    parser.add_argument("--add", nargs=2, action='append', metavar=("item", "amount"), 
                      help="Add a spending item with its amount. Can be used multiple times.")
    parser.add_argument("--view", action="store_true", help="View all spending items.")
    args = parser.parse_args()
    
    spendings = load_spendings()
    
    if args.add:
        for item_amount in args.add:
            item, amount = item_amount
            try:
                amount = float(amount)
                if item in spendings:
                    spendings[item] += amount
                else:
                    spendings[item] = amount
                print(f"Added {item} with amount {amount:.2f}.")
            except ValueError:
                print(f"Invalid amount for {item}. Please enter a numeric value.")
        
        save_spendings(spendings)
    
    if args.view:
        if spendings:
            total = sum(spendings.values())
            print("Current spendings:")
            for item, amount in spendings.items():
                print(f"{item}: ${amount:.2f}")
            print(f"Total: ${total:.2f}")
        else:
            print("No spendings recorded.")
    
    if not args.add and not args.view:
        parser.print_help()