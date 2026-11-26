import sqlite3
import requests

DB_PATH = "books.db"

SUBJECTS = {
    "history": "History",
    "science_fiction": "Science Fiction",
    "philosophy": "Philosophy",
    "biography": "Biography",
    "mystery": "Mystery",
}


def fetch_and_insert(subject_slug, genre_label, limit=15):
    url = f"https://openlibrary.org/subjects/{subject_slug}.json"
    response = requests.get(url, params={"limit": limit}, timeout=15)
    response.raise_for_status()
    works = response.json().get("works", [])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    existing_titles = {
        row[0] for row in cursor.execute("SELECT title FROM books").fetchall()
    }

    added = 0
    for work in works:
        title = (work.get("title") or "").strip()
        authors = work.get("authors") or []
        author = authors[0].get("name", "Unknown Author").strip() if authors else "Unknown Author"
        first_year = work.get("first_publish_year")
        summary = (
            f"First published in {first_year}. Cataloged under {genre_label}."
            if first_year
            else f"Cataloged under {genre_label} from Open Library."
        )

        if title and title not in existing_titles:
            cursor.execute(
                "INSERT INTO books (title, author, genre, summary) VALUES (?, ?, ?, ?)",
                (title, author, genre_label, summary),
            )
            existing_titles.add(title)
            added += 1

    conn.commit()
    conn.close()
    print(f"{genre_label}: added {added} books")


if __name__ == "__main__":
    for slug, label in SUBJECTS.items():
        fetch_and_insert(slug, label, limit=15)
