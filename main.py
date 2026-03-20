from fastapi import FastAPI, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import json
from functools import lru_cache
from typing import List, Dict, Any

import gspread
from google.oauth2.service_account import Credentials

app = FastAPI(title="Broadcast Graphics V2.1")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DEFAULT_WORKSHEET_NAME = "Skater Regular Season"

LIVE_GRAPHIC_STATE = {
    "graphic_style": None,
    "position_type": None,
    "season_type": None,
    "worksheet_name": DEFAULT_WORKSHEET_NAME,
    "players": [],
    "visible": False,
    "version": 0
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def get_gsheet_client():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

    creds_dict = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(credentials)


@lru_cache(maxsize=8)
def get_worksheet(worksheet_name: str):
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        raise RuntimeError("GOOGLE_SHEETS_ID not set")

    client = get_gsheet_client()
    workbook = client.open_by_key(spreadsheet_id)
    return workbook.worksheet(worksheet_name)


def refresh_sheet_cache():
    get_worksheet.cache_clear()


def get_worksheet_name(position_type: str, season_type: str) -> str:
    mapping = {
        ("Skater", "Regular"): "Skater Regular Season",
        ("Skater", "Playoffs"): "Skater Playoffs",
        ("Goalie", "Regular"): "Goalie Regular Season",
        ("Goalie", "Playoffs"): "Goalie Playoffs",
    }
    return mapping.get((position_type, season_type), DEFAULT_WORKSHEET_NAME)


def get_all_players(worksheet_name: str) -> List[Dict[str, Any]]:
    sheet = get_worksheet(worksheet_name)
    return sheet.get_all_records()


def search_players(query_text: str = "", position_type: str | None = None, season_type: str | None = None, limit: int = 10):
    worksheet_name = get_worksheet_name(position_type or "Skater", season_type or "Regular")
    records = get_all_players(worksheet_name)
    q = normalize(query_text)

    matches = []
    for row in records:
        name = row.get("Player Name", "")
        team = row.get("Team", "")
        if not q or q in normalize(name):
            matches.append({
                "player_name": name,
                "team": team,
                "worksheet_name": worksheet_name
            })

    matches.sort(key=lambda x: x["player_name"])
    return matches[:limit]


def find_player(player_name: str, worksheet_name: str):
    records = get_all_players(worksheet_name)
    for row in records:
        if normalize(row.get("Player Name")) == normalize(player_name):
            return row
    return None


def build_stats(row: dict):
    return [
        {"label": "GP", "value": row.get("Games Played", "")},
        {"label": "G", "value": row.get("Goals", "")},
        {"label": "A", "value": row.get("Assist", "")},
        {"label": "PTS", "value": row.get("PTS", "")}
    ]


def build_player_payload(player_name: str, worksheet_name: str):
    row = find_player(player_name, worksheet_name)
    if not row:
        raise HTTPException(status_code=404, detail=f"Player not found in '{worksheet_name}': {player_name}")

    return {
        "player_name": row.get("Player Name"),
        "team": row.get("Team"),
        "headshot_url": row.get("Player Image"),
        "team_logo_url": row.get("Team Image"),
        "stats": build_stats(row)
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("control_v2_1.html", {"request": request})


@app.get("/control", response_class=HTMLResponse)
async def control_page(request: Request):
    return templates.TemplateResponse("control_v2_1.html", {"request": request})


@app.get("/graphics/live", response_class=HTMLResponse)
async def graphics_page(request: Request):
    return templates.TemplateResponse("graphics_live_v2_1.html", {"request": request})


@app.get("/api/live")
async def get_live():
    return JSONResponse(LIVE_GRAPHIC_STATE)


@app.get("/api/players")
async def api_players(
    q: str = Query(default=""),
    position_type: str = Query(default="Skater"),
    season_type: str = Query(default="Regular"),
    limit: int = Query(default=10)
):
    return {
        "results": search_players(q, position_type, season_type, limit)
    }


@app.post("/api/set-live")
async def set_live(
    graphic_style: str = Form(...),
    position_type: str = Form(...),
    season_type: str = Form(...),
    player_name_1: str = Form(...),
    player_name_2: str = Form("")
):
    worksheet_name = get_worksheet_name(position_type, season_type)

    players = [build_player_payload(player_name_1, worksheet_name)]

    if graphic_style == "Head to Head":
        if not player_name_2.strip():
            raise HTTPException(status_code=400, detail="Second player is required for Head to Head")
        players.append(build_player_payload(player_name_2, worksheet_name))

    LIVE_GRAPHIC_STATE["graphic_style"] = graphic_style
    LIVE_GRAPHIC_STATE["position_type"] = position_type
    LIVE_GRAPHIC_STATE["season_type"] = season_type
    LIVE_GRAPHIC_STATE["worksheet_name"] = worksheet_name
    LIVE_GRAPHIC_STATE["players"] = players
    LIVE_GRAPHIC_STATE["visible"] = True
    LIVE_GRAPHIC_STATE["version"] += 1

    return {"ok": True, "live_state": LIVE_GRAPHIC_STATE}


@app.post("/api/clear")
async def clear_live():
    LIVE_GRAPHIC_STATE["graphic_style"] = None
    LIVE_GRAPHIC_STATE["position_type"] = None
    LIVE_GRAPHIC_STATE["season_type"] = None
    LIVE_GRAPHIC_STATE["worksheet_name"] = DEFAULT_WORKSHEET_NAME
    LIVE_GRAPHIC_STATE["players"] = []
    LIVE_GRAPHIC_STATE["visible"] = False
    LIVE_GRAPHIC_STATE["version"] += 1
    return {"ok": True}


@app.post("/api/refresh-sheet")
async def refresh_sheet():
    refresh_sheet_cache()
    return {"ok": True}
