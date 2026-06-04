import sqlite3
from pathlib import Path

# ==========================================
# DATABASE PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

BIBLE_DB = BASE_DIR / "scriptures" / "bible.db"
BOM_DB = BASE_DIR / "scriptures" / "book_of_mormon.db"

# ==========================================
# DATABASE HELPERS
# ==========================================

def get_bible_connection():
    conn = sqlite3.connect(BIBLE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_bom_connection():
    conn = sqlite3.connect(BOM_DB)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# SEARCH BIBLE
# ==========================================

def search_bible(term, limit=50):

    conn = get_bible_connection()

    query = """
    SELECT
        b.name AS book,
        v.chapter,
        v.verse,
        v.text
    FROM AKJV_verses v
    JOIN AKJV_books b
        ON v.book_id = b.id
    WHERE LOWER(v.text) LIKE LOWER(?)
    ORDER BY b.name, v.chapter, v.verse
    LIMIT ?
    """

    rows = conn.execute(
        query,
        (f"%{term}%", limit)
    ).fetchall()

    conn.close()

    return [
        {
            "source": "Bible",
            "book": row["book"],
            "chapter": row["chapter"],
            "verse": row["verse"],
            "text": row["text"]
        }
        for row in rows
    ]


# ==========================================
# SEARCH BOOK OF MORMON
# ==========================================

def search_bom(term, limit=50):

    conn = get_bom_connection()

    query = """
    SELECT
        b.book_name,
        v.verse_chapter,
        v.verse_number,
        c.content_body
    FROM contents c
    JOIN verses v
        ON c.verse_id = v.verse_id
    JOIN books b
        ON v.book_id = b.book_id
    WHERE c.edition_id = 31
      AND LOWER(c.content_body) LIKE LOWER(?)
    ORDER BY b.book_name,
             v.verse_chapter,
             v.verse_number
    LIMIT ?
    """

    rows = conn.execute(
        query,
        (f"%{term}%", limit)
    ).fetchall()

    conn.close()

    return [
        {
            "source": "Book of Mormon",
            "book": row["book_name"],
            "chapter": row["verse_chapter"],
            "verse": row["verse_number"],
            "text": row["content_body"]
        }
        for row in rows
    ]


# ==========================================
# SEARCH BOTH
# ==========================================

def search_all(term, limit=50):

    return {
        "bible": search_bible(term, limit),
        "bom": search_bom(term, limit)
    }


# ==========================================
# FUTURE CROSS REFERENCES
# ==========================================

def get_cross_references(verse_id):

    conn = get_bom_connection()

    query = """
    SELECT *
    FROM refs
    WHERE verse_id = ?
    """

    rows = conn.execute(
        query,
        (verse_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================
# TERMINAL TESTING
# ==========================================

def print_results(results):

    print("\n" + "=" * 80)
    print("BIBLE RESULTS")
    print("=" * 80)

    if not results["bible"]:
        print("No results found.")

    for verse in results["bible"]:

        print(
            f"{verse['book']} "
            f"{verse['chapter']}:{verse['verse']}"
        )

        print(verse["text"])
        print()

    print("\n" + "=" * 80)
    print("BOOK OF MORMON RESULTS")
    print("=" * 80)

    if not results["bom"]:
        print("No results found.")

    for verse in results["bom"]:

        print(
            f"{verse['book']} "
            f"{verse['chapter']}:{verse['verse']}"
        )

        print(verse["text"])
        print()


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nScripture Search")
    print("-" * 50)

    while True:

        term = input(
            "\nEnter search term (q to quit): "
        ).strip()

        if term.lower() in (
            "q",
            "quit",
            "exit"
        ):
            break

        results = search_all(term)

        print_results(results)

        print(
            f"\nBible Results: "
            f"{len(results['bible'])}"
        )

        print(
            f"Book of Mormon Results: "
            f"{len(results['bom'])}"
        )


if __name__ == "__main__":
    main()