function renderBottomBar(data) {
  if (!data.visible || data.graphic_style !== "Bottom Bar" || !(data.players || []).length) {
    mountGraphic(emptyState());
    return;
  }

  const player = data.players[0];
  const teamColor = colorValue(player.team_color);

  mountGraphic(`
    <div class="graphic bottom-bar-shell">
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

      <div class="meta-pill">${data.season_type} • ${data.position_type}</div>
    </div>
  `);
}

pollLive(renderBottomBar);
setInterval(() => pollLive(renderBottomBar), 500);
