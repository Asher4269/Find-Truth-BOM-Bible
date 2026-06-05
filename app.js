// =====================================================
// DATA
// =====================================================

let bibleVerses = [];
let bomVerses = [];

const MAX_RESULTS = 100;

// =====================================================
// ELEMENTS
// =====================================================

const searchButton = document.getElementById("searchButton");
const searchInput = document.getElementById("searchInput");

const bibleResults = document.getElementById("bibleResults");
const bomResults = document.getElementById("bomResults");

const loading = document.getElementById("loading");

// =====================================================
// LOAD DATA
// =====================================================

async function loadData() {
  loading.classList.remove("hidden");
  loading.innerText = "Loading scriptures...";

  try {
    const [bibleResponse, bomResponse] = await Promise.all([
      fetch("data/bible.json"),
      fetch("data/book_of_mormon.json"),
    ]);

    const bible = await bibleResponse.json();
    const bom = await bomResponse.json();

    // ------------------------------
    // Flatten Bible
    // ------------------------------

    bibleVerses = bible.verses.map((v) => ({
      source: "Bible",
      book: v.book_name,
      chapter: v.chapter,
      verse: v.verse,
      reference: `${v.book_name} ${v.chapter}:${v.verse}`,
      text: v.text,
    }));

    // ------------------------------
    // Flatten BOM
    // ------------------------------

    bomVerses = [];

    bom.books.forEach((book) => {
      book.chapters.forEach((chapter) => {
        chapter.verses.forEach((verse) => {
          bomVerses.push({
            source: "Book of Mormon",
            book: book.book,
            chapter: chapter.chapter,
            verse: verse.verse,
            reference: verse.reference,
            text: verse.text,
          });
        });
      });
    });

    console.log(`Loaded ${bibleVerses.length} Bible verses`);

    console.log(`Loaded ${bomVerses.length} BOM verses`);

    loading.innerText = `Loaded ${bibleVerses.length + bomVerses.length} verses`;

    setTimeout(() => {
      loading.classList.add("hidden");
    }, 1500);
  } catch (err) {
    console.error(err);

    loading.innerText = "Failed to load scripture files.";
  }
}

// =====================================================
// SEARCH
// =====================================================

function searchVerses(query) {
  const q = query.toLowerCase();

  return {
    bible: bibleVerses
      .filter((v) => v.text.toLowerCase().includes(q))
      .slice(0, MAX_RESULTS),

    bom: bomVerses
      .filter((v) => v.text.toLowerCase().includes(q))
      .slice(0, MAX_RESULTS),
  };
}

// =====================================================
// HIGHLIGHT MATCHES
// =====================================================

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlight(text, query) {
  if (!query) return text;

  const regex = new RegExp(`(${escapeRegex(query)})`, "gi");

  return text.replace(regex, "<mark>$1</mark>");
}

// =====================================================
// RENDER
// =====================================================

function renderVerses(verses, container, query) {
  container.innerHTML = "";

  if (!verses.length) {
    container.innerHTML = "<p>No matches found.</p>";

    return;
  }

  verses.forEach((v) => {
    const card = document.createElement("div");

    card.className = "verse";

    card.innerHTML = `
            <div class="reference">
                ${v.reference}
            </div>

            <div class="text">
                ${highlight(v.text, query)}
            </div>
        `;

    container.appendChild(card);
  });
}

// =====================================================
// SEARCH HANDLER
// =====================================================

function performSearch() {
  const query = searchInput.value.trim();

  if (!query) return;

  const results = searchVerses(query);

  renderVerses(results.bible, bibleResults, query);

  renderVerses(results.bom, bomResults, query);

  console.log(`Bible: ${results.bible.length}`);

  console.log(`BOM: ${results.bom.length}`);
}

// =====================================================
// EVENTS
// =====================================================

searchButton.addEventListener("click", performSearch);

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    performSearch();
  }
});

// =====================================================
// STARTUP
// =====================================================

loadData();
