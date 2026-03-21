# Broadcast Graphics Split Version

This version works the same as your previous setup, but the frontend assets are split up.

## Structure

- `templates/control.html`
- `templates/graphics_bottom_bar.html`
- `templates/graphics_full_screen.html`
- `templates/graphics_head_to_head.html`

- `static/css/control.css`
- `static/css/graphics-base.css`
- `static/css/bottom-bar.css`
- `static/css/full-screen.css`
- `static/css/head-to-head.css`

- `static/js/control.js`
- `static/js/graphics-common.js`

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

## Worksheet mapping

- Skater + Regular -> `Skater Regular Season`
- Skater + Playoffs -> `Skater Playoffs`
- Goalie + Regular -> `Goalie Regular Season`
- Goalie + Playoffs -> `Goalie Playoffs`

## OBS Sources

- `/graphics/bottom-bar`
- `/graphics/full-screen`
- `/graphics/head-to-head`

## Bottom bar plate image

Put your bottom bar plate PNG here:

`static/img/bottom_bar_plate.png`

## Render

Build Command:
`pip install -r requirements.txt`

Start Command:
`uvicorn main:app --host 0.0.0.0 --port $PORT`

## Environment Variables

- `GOOGLE_SHEETS_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
