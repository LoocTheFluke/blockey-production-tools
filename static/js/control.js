const form = document.getElementById("liveForm");
const statusBox = document.getElementById("status");
const graphicStyle = document.getElementById("graphic_style");
const positionType = document.getElementById("position_type");
const seasonType = document.getElementById("season_type");
const player2Wrap = document.getElementById("player2Wrap");
const liveVersion = document.getElementById("liveVersion");
const sheetPreview = document.getElementById("sheetPreview");

function getWorksheetName(position, season) {
  if (position === "Skater" && season === "Regular") return "Skater Regular Season";
  if (position === "Skater" && season === "Playoffs") return "Skater Playoffs";
  if (position === "Goalie" && season === "Regular") return "Goalie Regular Season";
  if (position === "Goalie" && season === "Playoffs") return "Goalie Playoffs";
  return "Skater Regular Season";
}

function syncUI() {
  player2Wrap.classList.toggle("hidden", graphicStyle.value !== "Head to Head");
  sheetPreview.textContent = getWorksheetName(positionType.value, seasonType.value);
}

graphicStyle.addEventListener("change", syncUI);
positionType.addEventListener("change", syncUI);
seasonType.addEventListener("change", syncUI);
syncUI();

async function getLiveVersion() {
  const res = await fetch("/api/live");
  const data = await res.json();
  liveVersion.textContent = data.live_label || "EMPTY";
}

async function setLive(e) {
  e.preventDefault();
  statusBox.textContent = "Updating live graphic...";
  const formData = new FormData(form);
  const res = await fetch("/api/set-live", { method: "POST", body: formData });
  const data = await res.json();

  if (res.ok) {
    statusBox.textContent = `Live graphic updated from ${data.live_state.worksheet_name}.`;
    liveVersion.textContent = data.live_state.live_label || "EMPTY";
  } else {
    statusBox.textContent = data.detail || "Error updating live graphic.";
  }
}

async function clearGraphic() {
  const res = await fetch("/api/clear", { method: "POST" });
  const data = await res.json();
  statusBox.textContent = res.ok ? "Graphic cleared." : (data.detail || "Error clearing graphic.");
  await getLiveVersion();
}

async function refreshSheet() {
  statusBox.textContent = "Refreshing Google Sheet cache...";
  const res = await fetch("/api/refresh-sheet", { method: "POST" });
  const data = await res.json();
  statusBox.textContent = res.ok ? "Google Sheet cache refreshed." : (data.detail || "Error refreshing sheet.");
}

form.addEventListener("submit", setLive);
document.getElementById("clearBtn").addEventListener("click", clearGraphic);
document.getElementById("refreshSheetBtn").addEventListener("click", refreshSheet);

function attachAutocomplete(inputId, suggestionsId) {
  const input = document.getElementById(inputId);
  const box = document.getElementById(suggestionsId);

  async function loadSuggestions() {
    const q = input.value.trim();
    const pos = positionType.value;
    const season = seasonType.value;

    if (!q) {
      box.innerHTML = "";
      box.style.display = "none";
      return;
    }

    const res = await fetch(`/api/players?q=${encodeURIComponent(q)}&position_type=${encodeURIComponent(pos)}&season_type=${encodeURIComponent(season)}&limit=8`);
    const data = await res.json();
    const results = data.results || [];

    if (!results.length) {
      box.innerHTML = "";
      box.style.display = "none";
      return;
    }

    box.innerHTML = results.map(item => `
      <button type="button" class="suggestion-item" data-name="${item.player_name}">
        <strong>${item.player_name}</strong>
        <span>${item.team} • ${item.worksheet_name}</span>
      </button>
    `).join("");

    box.style.display = "block";

    box.querySelectorAll(".suggestion-item").forEach(btn => {
      btn.addEventListener("click", () => {
        input.value = btn.dataset.name;
        box.innerHTML = "";
        box.style.display = "none";
      });
    });
  }

  input.addEventListener("input", loadSuggestions);
  input.addEventListener("blur", () => setTimeout(() => { box.style.display = "none"; }, 150));
  input.addEventListener("focus", loadSuggestions);
  positionType.addEventListener("change", () => { box.style.display = "none"; input.value = ""; });
  seasonType.addEventListener("change", () => { box.style.display = "none"; input.value = ""; });
}

attachAutocomplete("player_name_1", "suggestions_1");
attachAutocomplete("player_name_2", "suggestions_2");
getLiveVersion();
