# Broadcast Graphics MVP (FastAPI + Render + Google Sheets)

## What this does
- Production opens `/control`
- Selects:
  - Graphics Style (Bottom Bar | Full Screen | Head to Head)
  - Position Type (Skater | Goalie)
  - Season Type (Regular | Playoffs)
  - Player Name (1 or 2 for Head to Head)
- App reads player stats from Google Sheets
- OBS uses `/graphics/live` as Browser Source

## Render setup
Build command:
pip install -r requirements.txt

Start command:
uvicorn main:app --host 0.0.0.0 --port $PORT

## Environment Variables
- GOOGLE_SHEETS_ID
- GOOGLE_SERVICE_ACCOUNT_JSON

## Required Google Sheet tab
Worksheet name must be: players

## Suggested columns
player_name
team
position_type
headshot_url
team_logo_url
regular_skater_gp
regular_skater_g
regular_skater_a
regular_skater_pts
regular_skater_pim
playoffs_skater_gp
playoffs_skater_g
playoffs_skater_a
playoffs_skater_pts
playoffs_skater_pim
regular_goalie_gp
regular_goalie_w
regular_goalie_gaa
regular_goalie_sv_pct
regular_goalie_so
playoffs_goalie_gp
playoffs_goalie_w
playoffs_goalie_gaa
playoffs_goalie_sv_pct
playoffs_goalie_so
