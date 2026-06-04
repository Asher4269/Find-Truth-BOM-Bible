import sqlite3
from pathlib import Path

# ==========================================
# DATABASE PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

BIBLE_DB = BASE_DIR / "scriptures" / "bible.db"
BOM_DB = BASE_DIR / "scriptures" / "book_of_mormon.db"

# ==========================================
# CONNECTIONS
# ==========================================

bible_conn = sqlite3.connect(BIBLE_DB)
bom_conn = sqlite3.connect(BOM_DB)

bible_conn.row_factory = sqlite3.Row
bom_conn.row_factory = sqlite3.Row


# ==========================================
# SEARCH BIBLE
# ==========================================

def search_bible(term, limit=25):
    query = """
    SELECT
        b.name AS book,
        v.chapter,
        v.verse,
        v.text
    FROM AKJV_verses v
    JOIN AKJV_books b
        ON b.id = v.book_id
    WHERE LOWER(v.text) LIKE LOWER(?)
    LIMIT ?
    """

    rows = bible_conn.execute(
        query,
        (f"%{term}%", limit)
    ).fetchall()

    results = []

    for row in rows:
        results.append({
            "source": "Bible",
            "book": row["book"],
            "chapter": row["chapter"],
            "verse": row["verse"],
            "text": row["text"]
        })

    return results


# ==========================================
# SEARCH BOOK OF MORMON
# ==========================================

def search_bom(term, limit=25):
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
    LIMIT ?
    """

    rows = bom_conn.execute(
        query,
        (f"%{term}%", limit)
    ).fetchall()

    results = []

    for row in rows:
        results.append({
            "source": "Book of Mormon",
            "book": row["book_name"],
            "chapter": row["verse_chapter"],
            "verse": row["verse_number"],
            "text": row["content_body"]
        })

    return results


# ==========================================
# SEARCH BOTH
# ==========================================

def search_all(term):
    return {
        "bible": search_bible(term),
        "bom": search_bom(term)
    }


# ==========================================
# DISPLAY RESULTS
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
# FUTURE CROSS REFERENCES
# ==========================================

def get_cross_references(verse_id):
    """
    Placeholder for future work using
    the refs table.

    Eventually this will return:
    Alma 32:21
        -> Hebrews 11:1
        -> James 2:17
    """

    query = """
    SELECT *
    FROM refs
    WHERE verse_id = ?
    """

    return bom_conn.execute(
        query,
        (verse_id,)
    ).fetchall()


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nScripture Search")
    print("-" * 40)

    while True:

        term = input(
            "\nEnter search term (or q to quit): "
        ).strip()

        if term.lower() in ("q", "quit", "exit"):
            break

        results = search_all(term)

        print_results(results)

        print(
            f"\nFound "
            f"{len(results['bible'])} Bible verses and "
            f"{len(results['bom'])} Book of Mormon verses."
        )


if __name__ == "__main__":
    main()