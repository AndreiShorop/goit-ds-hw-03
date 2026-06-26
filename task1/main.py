"""
Task 1 — MongoDB CRUD operations using PyMongo.
Manages a collection of cats with fields: name, age, features.
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "cats_db"
COLLECTION_NAME = "cats"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def seed_data() -> None:
    """Insert sample cat documents if the collection is empty."""
    if collection.count_documents({}) == 0:
        sample_cats = [
            {
                "name": "barsik",
                "age": 3,
                "features": ["ходить в капці", "дає себе гладити", "рудий"],
            },
            {
                "name": "murzik",
                "age": 5,
                "features": ["любить рибу", "грає з м'ячем", "сірий"],
            },
            {
                "name": "pushok",
                "age": 2,
                "features": ["білий", "ласкавий", "тихий"],
            },
        ]
        collection.insert_many(sample_cats)
        print("Sample data inserted into the collection.")


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_all_cats() -> None:
    """Print every document in the cats collection."""
    try:
        cats = list(collection.find())
        if not cats:
            print("The collection is empty.")
            return
        for cat in cats:
            print(cat)
    except PyMongoError as e:
        print(f"[Error] Could not read cats: {e}")


def get_cat_by_name(name: str) -> None:
    """Print the document for a cat with the given name."""
    try:
        cat = collection.find_one({"name": name})
        if cat:
            print(cat)
        else:
            print(f"Cat '{name}' was not found.")
    except PyMongoError as e:
        print(f"[Error] Could not find cat: {e}")


# ---------------------------------------------------------------------------
# Update operations
# ---------------------------------------------------------------------------

def update_cat_age(name: str, new_age: int) -> None:
    """Update the age field of a cat identified by name."""
    try:
        result = collection.update_one({"name": name}, {"$set": {"age": new_age}})
        if result.matched_count:
            print(f"Cat '{name}' age updated to {new_age}.")
        else:
            print(f"Cat '{name}' was not found.")
    except PyMongoError as e:
        print(f"[Error] Could not update cat age: {e}")


def add_cat_feature(name: str, feature: str) -> None:
    """Append a new feature to the features list of a cat identified by name."""
    try:
        result = collection.update_one(
            {"name": name}, {"$push": {"features": feature}}
        )
        if result.matched_count:
            print(f"Feature '{feature}' added to cat '{name}'.")
        else:
            print(f"Cat '{name}' was not found.")
    except PyMongoError as e:
        print(f"[Error] Could not add feature: {e}")


# ---------------------------------------------------------------------------
# Delete operations
# ---------------------------------------------------------------------------

def delete_cat_by_name(name: str) -> None:
    """Remove a single cat document identified by name."""
    try:
        result = collection.delete_one({"name": name})
        if result.deleted_count:
            print(f"Cat '{name}' deleted successfully.")
        else:
            print(f"Cat '{name}' was not found.")
    except PyMongoError as e:
        print(f"[Error] Could not delete cat: {e}")


def delete_all_cats() -> None:
    """Remove all documents from the cats collection."""
    try:
        result = collection.delete_many({})
        print(f"Deleted {result.deleted_count} document(s) from the collection.")
    except PyMongoError as e:
        print(f"[Error] Could not delete all cats: {e}")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point — interactive CLI menu for CRUD operations."""
    seed_data()

    menu = (
        "\n--- Cats CRUD Menu ---\n"
        "1. Show all cats\n"
        "2. Find cat by name\n"
        "3. Update cat age\n"
        "4. Add feature to cat\n"
        "5. Delete cat by name\n"
        "6. Delete all cats\n"
        "0. Exit\n"
    )

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            get_all_cats()

        elif choice == "2":
            name = input("Enter cat name: ").strip()
            get_cat_by_name(name)

        elif choice == "3":
            name = input("Enter cat name: ").strip()
            raw_age = input("Enter new age: ").strip()
            try:
                update_cat_age(name, int(raw_age))
            except ValueError:
                print("Age must be a whole number.")

        elif choice == "4":
            name = input("Enter cat name: ").strip()
            feature = input("Enter new feature: ").strip()
            add_cat_feature(name, feature)

        elif choice == "5":
            name = input("Enter cat name: ").strip()
            delete_cat_by_name(name)

        elif choice == "6":
            confirm = input("Delete ALL cats? Type 'yes' to confirm: ").strip().lower()
            if confirm == "yes":
                delete_all_cats()
            else:
                print("Operation cancelled.")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose a number from the menu.")


if __name__ == "__main__":
    main()
