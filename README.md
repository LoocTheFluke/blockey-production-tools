# Broadcast Graphics V3.0

This version uses 3 separate OBS browser sources:

- Bottom Bar -> `/graphics/bottom-bar`
- Full Screen -> `/graphics/full-screen`
- Head to Head -> `/graphics/head-to-head`

Only the matching template renders on each source. The others stay transparent.

## Google Sheet format
Headers must be in row 4.
Only columns A:H are read.

Required headers:
- Player Image
- Team Image
- Username
- Team
- GP
- G
- A
- PTS

Data starts on row 5.

## Worksheet mapping
- Skater + Regular -> `Skater Regular Season`
- Skater + Playoffs -> `Skater Playoffs`
- Goalie + Regular -> `Goalie Regular Season`
- Goalie + Playoffs -> `Goalie Playoffs`

## Team colors
Edit `team_colors.py`

Example:
TEAM_COLORS = {
    "BOS": "228B22",
    "NYR": "0038A8",
}

DEFAULT_TEAM_COLOR = "3170DE"

If a team is not found, the default color is used.

## Render
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn main:app --host 0.0.0.0 --port $PORT

## Environment Variables
- GOOGLE_SHEETS_ID
- GOOGLE_SERVICE_ACCOUNT_JSON

## OBS suggestions
- Bottom Bar source size: 1920 x 320
- Full Screen source size: 1920 x 1080
- Head to Head source size: 1920 x 1080
