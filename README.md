# Broadcast Graphics V2.2

This version uses these exact headers in row 4:

- Player Image
- Team Image
- Username
- Team
- GP
- G
- A
- PTS

## Important
- The app reads only columns A:H
- The app reads headers from row 4
- Data starts on row 5
- Rows 1-3 are ignored

## Worksheet mapping
- Skater + Regular -> `Skater Regular Season`
- Skater + Playoffs -> `Skater Playoffs`
- Goalie + Regular -> `Goalie Regular Season`
- Goalie + Playoffs -> `Goalie Playoffs`

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
