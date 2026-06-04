const searchButton = document.getElementById("searchButton");
const searchInput = document.getElementById("searchInput");

const bibleResults = document.getElementById("bibleResults");
const bomResults = document.getElementById("bomResults");

const loading = document.getElementById("loading");

searchButton.addEventListener("click", performSearch);

searchInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    performSearch();
  }
});

async function performSearch() {
  const query = searchInput.value.trim();

  if (!query) return;

  loading.classList.remove("hidden");

  bibleResults.innerHTML = "";
  bomResults.innerHTML = "";

  try {
    const response = await fetch(
      `http://localhost:8000/search?q=${encodeURIComponent(query)}`,
    );

    const data = await response.json();

    renderVerses(data.bible, bibleResults);
    renderVerses(data.bom, bomResults);
  } catch (error) {
    console.error(error);

    bibleResults.innerHTML = "<p>Unable to reach server.</p>";

    bomResults.innerHTML = "<p>Unable to reach server.</p>";
  }

  loading.classList.add("hidden");
}

function renderVerses(verses, container) {
  if (!verses.length) {
    container.innerHTML = "<p>No matching verses found.</p>";

    return;
  }

  verses.forEach((v) => {
    const card = document.createElement("div");
    card.className = "verse";

    card.innerHTML = `
            <div class="reference">
                ${v.book} ${v.chapter}:${v.verse}
            </div>

            <div class="text">
                ${v.text}
            </div>
        `;

    container.appendChild(card);
  });
}
