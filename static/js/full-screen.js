function renderFullScreen(data) {
  if (!data.visible || data.graphic_style !== "Full Screen" || !(data.players || []).length) {
    mountGraphic(emptyState());
    return;
  }

  const player = data.players[0];
  const teamColor = colorValue(player.team_color);

  mountGraphic(`
    <div class="graphic full-screen-shell">
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

      <div class="meta-pill">${data.season_type} • ${data.position_type}</div>
    </div>
  `);
}

pollLive(renderFullScreen);
setInterval(() => pollLive(renderFullScreen), 500);
