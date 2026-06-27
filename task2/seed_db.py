import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "quotes_db"
DATA_DIR = Path(__file__).parent


def load_json(filepath: Path) -> list[dict]:
    if not filepath.exists():
        raise FileNotFoundError(
            f"Required file not found: {filepath}\n"
            "Run task2/scraper.py first to generate the JSON files."
        )
    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{filepath} must contain a JSON array.")
    return data


def seed_collection(db, collection_name: str, data: list[dict]) -> None:
    try:
        col = db[collection_name]
        col.drop()
        result = col.insert_many(data)
        print(
            f"Collection '{collection_name}': inserted {len(result.inserted_ids)} document(s)."
        )
    except PyMongoError as e:
        print(f"[Error] Failed to seed '{collection_name}': {e}")


def main() -> None:
    if not MONGO_URI:
        print(
            "[Error] MONGO_URI is not set.\n"
            "Create a .env file with MONGO_URI=<your Atlas connection string>."
        )
        return

    try:
        quotes = load_json(DATA_DIR / "quotes.json")
        authors = load_json(DATA_DIR / "authors.json")
    except (FileNotFoundError, ValueError) as e:
        print(f"[Error] {e}")
        return

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Connected to MongoDB Atlas successfully.")
    except PyMongoError as e:
        print(f"[Error] Could not connect to MongoDB: {e}")
        return

    db = client[DB_NAME]
    seed_collection(db, "quotes", quotes)
    seed_collection(db, "authors", authors)

    client.close()
    print("Seeding complete.")


if __name__ == "__main__":
    main()
