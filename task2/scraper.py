"""
Task 2 — Scrape all quotes and author details from quotes.toscrape.com.
Outputs:
  task2/quotes.json  — list of quote objects
  task2/authors.json — list of unique author objects
"""

import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com"
OUTPUT_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Author scraper
# ---------------------------------------------------------------------------

def scrape_author(author_path: str) -> dict | None:
    """
    Fetch and parse the author detail page.

    Args:
        author_path: Relative URL path to the author page (e.g. '/author/einstein/').

    Returns:
        Dictionary with fullname, born_date, born_location, description,
        or None if the request fails.
    """
    url = BASE_URL + author_path
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Warning] Could not fetch author page {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    fullname = soup.find("h3", class_="author-title")
    born_date = soup.find("span", class_="author-born-date")
    born_location = soup.find("span", class_="author-born-location")
    description = soup.find("div", class_="author-description")

    if not all([fullname, born_date, born_location, description]):
        print(f"[Warning] Incomplete author data at {url}")
        return None

    return {
        "fullname": fullname.get_text(strip=True),
        "born_date": born_date.get_text(strip=True),
        "born_location": born_location.get_text(strip=True),
        "description": description.get_text(strip=True),
    }


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

def scrape_all() -> tuple[list[dict], list[dict]]:
    """
    Iterate over all paginated pages and collect quotes and authors.

    Returns:
        Tuple (quotes, authors) where each is a list of dicts.
    """
    quotes: list[dict] = []
    authors: dict[str, dict] = {}  # keyed by author name to avoid duplicates

    page = 1
    while True:
        url = f"{BASE_URL}/page/{page}/"
        print(f"Scraping page {page}: {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[Error] Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quote_divs = soup.find_all("div", class_="quote")

        if not quote_divs:
            print("No more quotes found — scraping complete.")
            break

        for quote_div in quote_divs:
            text_tag = quote_div.find("span", class_="text")
            author_tag = quote_div.find("small", class_="author")
            tag_links = quote_div.find_all("a", class_="tag")
            author_link_tag = quote_div.find("a", href=True)

            if not (text_tag and author_tag and author_link_tag):
                continue

            author_name = author_tag.get_text(strip=True)
            tags = [t.get_text(strip=True) for t in tag_links]

            quotes.append(
                {
                    "tags": tags,
                    "author": author_name,
                    "quote": text_tag.get_text(strip=True),
                }
            )

            # Fetch author details only once per unique author
            if author_name not in authors:
                author_data = scrape_author(author_link_tag["href"])
                if author_data:
                    authors[author_name] = author_data

        # Follow pagination
        next_li = soup.find("li", class_="next")
        if not next_li:
            break
        page += 1

    return quotes, list(authors.values())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    quotes, authors = scrape_all()

    quotes_path = OUTPUT_DIR / "quotes.json"
    authors_path = OUTPUT_DIR / "authors.json"

    with open(quotes_path, "w", encoding="utf-8") as fh:
        json.dump(quotes, fh, ensure_ascii=False, indent=2)
    print(f"Saved {len(quotes)} quotes to {quotes_path}")

    with open(authors_path, "w", encoding="utf-8") as fh:
        json.dump(authors, fh, ensure_ascii=False, indent=2)
    print(f"Saved {len(authors)} authors to {authors_path}")


if __name__ == "__main__":
    main()
