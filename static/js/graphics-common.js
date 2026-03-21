let currentVersion = -1;
const TEMPLATE = window.GRAPHIC_TEMPLATE || "";

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

function singlePlayerCard(player, mode, season, position) {
  const shellClass = mode === "Bottom Bar"
    ? "graphic bottom-bar-shell"
    : "graphic full-screen-shell";

  const teamColor = colorValue(player.team_color);

  if (mode === "Bottom Bar") {
    return `
      <div class="${shellClass}">
        <div class="single-layout bottom-layout image-plate-layout" style="--team-color:${teamColor};">
          <img class="plate-base" src="/static/img/bottom_bar_plate.png" alt="">
          <div class="plate-tint"></div>
          <div class="plate-shade"></div>

          <div class="brand-col">
            ${logoBadge(player)}
            ${player.headshot_url ? `<img class="headshot" src="${player.headshot_url}" alt="">` : ""}
          </div>

          <div class="content-col">
            <div class="title-row">
              <div>
                <div class="player-name">${player.player_name || ""}</div>
                <div class="team-name">${player.team || ""}</div>
              </div>
              ${player.team_logo_url ? `<img class="team-logo corner-logo" src="${player.team_logo_url}" alt="">` : ""}
            </div>
            <div class="stats-row">${statCards(player.stats)}</div>
          </div>
        </div>

        <div class="meta-pill">${season} • ${position}</div>
      </div>
    `;
  }

  return `
    <div class="${shellClass}">
      <div class="single-layout full-layout" style="--team-color:${teamColor};">
        <div class="team-accent"></div>

        <div class="brand-col">
          ${logoBadge(player)}
          ${player.headshot_url ? `<img class="headshot" src="${player.headshot_url}" alt="">` : ""}
        </div>

        <div class="content-col">
          <div class="title-row">
            <div>
              <div class="player-name">${player.player_name || ""}</div>
              <div class="team-name">${player.team || ""}</div>
            </div>
            ${player.team_logo_url ? `<img class="team-logo corner-logo" src="${player.team_logo_url}" alt="">` : ""}
          </div>
          <div class="stats-row">${statCards(player.stats)}</div>
        </div>
      </div>

      <div class="meta-pill">${season} • ${position}</div>
    </div>
  `;
}

function headToHead(players, season, position) {
  const leftColor = colorValue(players?.[0]?.team_color);
  const rightColor = colorValue(players?.[1]?.team_color);

  return `
    <div class="graphic h2h-shell">
      <div class="meta-pill center-pill">${season} • ${position} • HEAD TO HEAD</div>

      <div class="h2h-layout">
        ${players.map((player, idx) => `
          <div class="h2h-side" style="--team-color:${idx === 0 ? leftColor : rightColor};">
            <div class="team-accent"></div>
            ${logoBadge(player)}
            ${player.headshot_url ? `<img class="headshot large" src="${player.headshot_url}" alt="">` : ""}
            <div class="player-name center">${player.player_name || ""}</div>
            <div class="team-name center">${player.team || ""}</div>
            <div class="stats-grid">${statCards(player.stats)}</div>
          </div>
        `).join("")}
      </div>

      <div class="versus-badge">VS</div>
    </div>
  `;
}

function emptyState() {
  return `<div class="empty-state"></div>`;
}

function shouldRender(data) {
  return data.visible && data.graphic_style === TEMPLATE && (data.players || []).length > 0;
}

function renderGraphic(data) {
  const root = document.getElementById("graphicsRoot");

  if (!shouldRender(data)) {
    root.innerHTML = emptyState();
    return;
  }

  if (data.graphic_style === "Head to Head") {
    root.innerHTML = headToHead(data.players, data.season_type, data.position_type);
    return;
  }

  root.innerHTML = singlePlayerCard(
    data.players[0],
    data.graphic_style,
    data.season_type,
    data.position_type
  );
}

async function pollLive() {
  try {
    const res = await fetch("/api/live", { cache: "no-store" });
    const data = await res.json();

    if (data.version !== currentVersion) {
      currentVersion = data.version;
      renderGraphic(data);
    }
  } catch (err) {
    console.error(err);
  }
}

pollLive();
setInterval(pollLive, 500);
