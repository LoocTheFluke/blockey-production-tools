# Broadcast Graphics V2.1

This version reads from four worksheet tabs based on the Production Control choices:

- Skater + Regular -> `Skater Regular Season`
- Skater + Playoffs -> `Skater Playoffs`
- Goalie + Regular -> `Goalie Regular Season`
- Goalie + Playoffs -> `Goalie Playoffs`

## Required headers for EVERY tab
Use these exact row-1 headers:

- Player Image
- Team Image
- Player Name
- Team
- Games Played
- Goals
- Assist
- PTS

## What you need to put in the code
Nothing if your tab names and headers match exactly.

## What must exist in Google Sheets
Create these tabs:
- Skater Regular Season
- Skater Playoffs
- Goalie Regular Season
- Goalie Playoffs

If you only have `Skater Regular Season` right now, that mode will work immediately.
The other three modes will work once those tabs exist.

## Render
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn main:app --host 0.0.0.0 --port $PORT

## Environment Variables
- GOOGLE_SHEETS_ID
- GOOGLE_SERVICE_ACCOUNT_JSON

## Main URLs
- Control: `/control`
- OBS Browser Source: `/graphics/live`
