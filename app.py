import os
import sqlite3
import requests
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")
NYT_API_KEY = os.environ.get("NYT_BOOKS_API_KEY", "")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

SAMPLE_BOOKS = [
    (
        "The Name of the Rose",
        "Umberto Eco",
        "Historical Mystery",
        "Monastic intrigue, ancient manuscripts, and quiet lantern-lit study.",
    ),
    (
        "Piranesi",
        "Susanna Clarke",
        "Fantasy",
        "Tidal halls, marble statues, and meticulous journals kept through shifting weather.",
    ),
    (
        "The Shadow of the Wind",
        "Carlos Ruiz Zafón",
        "Gothic Fiction",
        "A forgotten novel in Barcelona's Cemetery of Forgotten Books sparks a years-long mystery.",
    ),
    (
        "Circe",
        "Madeline Miller",
        "Mythological Fiction",
        "Solitude, craft, and quiet defiance on a distant island.",
    ),
    (
        "Split Second",
        "Janet Evanovich",
        "NYT Best Sellers",
        "Newly married Stephanie Plum hunts down a bond jumper and an invisible stalker.",
    ),
    (
        "All In",
        "David Baldacci",
        "NYT Best Sellers",
        "Travis Devine's investigation uncovers a cabal intent on shifting the global balance of power.",
    ),
    (
        "A Court of Splintered Harmony",
        "Sarah J. Maas",
        "NYT Best Sellers",
        "Former alliances must be restored to fight a rising threat in Prythian.",
    ),
    (
        "Theo of Golden",
        "Allen Levi",
        "NYT Best Sellers",
        "A traveler in a small Southern town buys pencil portraits of residents and exchanges them for their stories.",
    ),
    (
        "The Calamity Club",
        "Kathryn Stockett",
        "NYT Best Sellers",
        "During the Great Depression, women band together to reshape their futures.",
    ),
    (
        "The French Illusion",
        "John Grisham",
        "NYT Best Sellers",
        "A kidnapping during a honeymoon in France pulls a young lawyer into an international operation.",
    ),
    (
        "Threshing Day",
        "Rebecca Yarros",
        "NYT Best Sellers",
        "Thirteen stories from the Empyrean world following cadets competing for a dragon bond.",
    ),
    (
        "The Hollow",
        "Michael Connelly",
        "NYT Best Sellers",
        "Harry Bosch investigates a case tied to the facility where he spent part of his youth.",
    ),
]


def import_nyt_bestsellers(list_name="hardcover-fiction", genre_label="NYT Best Sellers"):
    if not NYT_API_KEY:
        return 0

    try:
        url = f"https://api.nytimes.com/svc/books/v3/lists/current/{list_name}.json"
        response = requests.get(url, params={"api-key": NYT_API_KEY}, timeout=10)
        response.raise_for_status()
        books_data = response.json().get("results", {}).get("books", [])
    except Exception as exc:
        print(f"NYT API sync skipped: {exc}")
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    existing_titles = {
        row[0] for row in cursor.execute("SELECT title FROM books").fetchall()
    }

    added = 0
    for item in books_data:
        title = (item.get("title") or "").strip().title()
        author = (item.get("author") or "Unknown Author").strip()
        summary = (
            item.get("description") or "Featured on the New York Times Best Seller list."
        ).strip()
        if title and title not in existing_titles:
            cursor.execute(
                "INSERT INTO books (title, author, genre, summary) VALUES (?, ?, ?, ?)",
                (title, author, genre_label, summary),
            )
            existing_titles.add(title)
            added += 1

    conn.commit()
    conn.close()
    return added


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            summary TEXT NOT NULL
        )
        """
    )
    existing_titles = {
        row[0] for row in cursor.execute("SELECT title FROM books").fetchall()
    }
    new_books = [book for book in SAMPLE_BOOKS if book[0] not in existing_titles]
    if new_books:
        cursor.executemany(
            "INSERT INTO books (title, author, genre, summary) VALUES (?, ?, ?, ?)",
            new_books,
        )
    conn.commit()
    conn.close()
    import_nyt_bestsellers()


def get_books(selected_genre=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if selected_genre and selected_genre != "All":
        rows = conn.execute(
            "SELECT id, title, author, genre, summary FROM books WHERE genre = ? ORDER BY id",
            (selected_genre,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, title, author, genre, summary FROM books ORDER BY id"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_genres():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT DISTINCT genre FROM books ORDER BY genre"
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


@app.route("/")
def index():
    selected_genre = request.args.get("genre", "All")
    books = get_books(selected_genre)
    genres = get_genres()
    logo_exists = os.path.exists(os.path.join(app.static_folder, "logo.png"))
    return render_template(
        "index.html",
        books=books,
        genres=genres,
        selected_genre=selected_genre,
        logo_exists=logo_exists,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
