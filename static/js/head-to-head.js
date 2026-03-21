function renderHeadToHead(data) {
  if (!data.visible || data.graphic_style !== "Head to Head" || !(data.players || []).length) {
    mountGraphic(emptyState());
    return;
  }

  const players = data.players;
  const leftColor = colorValue(players?.[0]?.team_color);
  const rightColor = colorValue(players?.[1]?.team_color);

  mountGraphic(`
    <div class="graphic h2h-shell">
      <div class="meta-pill center-pill">${data.season_type} • ${data.position_type} • HEAD TO HEAD</div>

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
  `);
}

pollLive(renderHeadToHead);
setInterval(() => pollLive(renderHeadToHead), 500);
