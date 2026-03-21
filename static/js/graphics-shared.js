let currentVersion = -1;

function colorValue(hex) {
  const raw = (hex || "3170DE").replace("#", "").trim();
  return /^[0-9A-Fa-f]{6}$/.test(raw) ? `#${raw}` : "#3170DE";
}

function statCards(stats) {
  return (stats || []).map(stat => `
    <div class="stat-card">
      <div class="stat-label">${stat.label}</div>
      <div class="stat-value">${stat.value ?? ""}</div>
    </div>
  `).join("");
}

function logoBadge(player) {
  return player.team_logo_url ? `
    <div class="logo-badge">
      <img class="team-logo" src="${player.team_logo_url}" alt="">
    </div>
  ` : "";
}

function emptyState() {
  return `<div class="empty-state"></div>`;
}

function mountGraphic(html) {
  const root = document.getElementById("graphicsRoot");
  root.innerHTML = html;
}

async function pollLive(renderer) {
  try {
    const res = await fetch("/api/live", { cache: "no-store" });
    const data = await res.json();

    if (data.version !== currentVersion) {
      currentVersion = data.version;
      renderer(data);
    }
  } catch (err) {
    console.error(err);
  }
}
