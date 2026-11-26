import sqlite3

FEATURED_BOOKS = {
    "Military": [
        ("The Art of War", "Sun Tzu"),
        ("On War", "Carl von Clausewitz"),
        ("Band of Brothers", "Stephen E. Ambrose"),
        ("Black Hawk Down", "Mark Bowden"),
        ("We Were Soldiers Once… and Young", "Harold G. Moore and Joseph L. Galloway"),
        ("With the Old Breed", "Eugene B. Sledge"),
        ("Lone Survivor", "Marcus Luttrell"),
        ("Unbroken", "Laura Hillenbrand"),
        ("The Guns of August", "Barbara W. Tuchman"),
        ("The Forever War", "Dexter Filkins"),
    ],
    "Non Fiction": [
        ("Educated", "Tara Westover"),
        ("In Cold Blood", "Truman Capote"),
        ("The Devil in the White City", "Erik Larson"),
        ("A Brief History of Time", "Stephen Hawking"),
        ("Guns, Germs, and Steel", "Jared Diamond"),
        ("The Omnivore's Dilemma", "Michael Pollan"),
        ("I Know Why the Caged Bird Sings", "Maya Angelou"),
        ("The Wager", "David Grann"),
        ("On Writing", "Stephen King"),
        ("The Right Stuff", "Tom Wolfe"),
    ],
    "Poetry": [
        ("Leaves of Grass", "Walt Whitman"),
        ("The Complete Poems of Emily Dickinson", "Emily Dickinson"),
        ("Ariel", "Sylvia Plath"),
        ("The Waste Land and Other Poems", "T. S. Eliot"),
        ("The Raven and Other Poems", "Edgar Allan Poe"),
        ("Twenty Love Poems and a Song of Despair", "Pablo Neruda"),
        ("Howl and Other Poems", "Allen Ginsberg"),
        ("And Still I Rise", "Maya Angelou"),
        ("The Essential Rumi", "Rumi"),
        ("Songs of Innocence and of Experience", "William Blake"),
    ],
}


def seed_books_by_category(db_path="books.db"):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                genre TEXT NOT NULL DEFAULT ''
            )
            """
        )

        cur.execute("PRAGMA table_info(books)")
        columns = [row[1] for row in cur.fetchall()]
        if "category" not in columns:
            cur.execute("ALTER TABLE books ADD COLUMN category TEXT NOT NULL DEFAULT ''")
            columns.append("category")
        if "genre" not in columns:
            cur.execute("ALTER TABLE books ADD COLUMN genre TEXT NOT NULL DEFAULT ''")
            columns.append("genre")

        has_genre = "genre" in columns

        with conn:
            for category, books in FEATURED_BOOKS.items():
                cur.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    (category,),
                )
                for title, author in books:
                    cur.execute(
                        "SELECT 1 FROM books WHERE title = ? AND author = ? AND category = ?",
                        (title, author, category),
                    )
                    if cur.fetchone() is None:
                        if has_genre:
                            cur.execute(
                                "INSERT INTO books (title, author, category, genre) VALUES (?, ?, ?, ?)",
                                (title, author, category, category),
                            )
                        else:
                            cur.execute(
                                "INSERT INTO books (title, author, category) VALUES (?, ?, ?)",
                                (title, author, category),
                            )
    finally:
        conn.close()


if __name__ == "__main__":
    seed_books_by_category("books.db")
    print("Seeded Military, Non Fiction, and Poetry (10 books each).")
