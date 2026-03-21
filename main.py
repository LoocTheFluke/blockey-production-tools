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

from team_colors import TEAM_COLORS, DEFAULT_TEAM_COLOR

app = FastAPI(title="Broadcast Graphics Split Version")

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
    "version": 0,
    "live_label": "EMPTY"
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def normalize(text: str) -> str:
    return " ".join((text or "").replace("\u00A0", " ").strip().upper().split())


def safe_hex(value: str | None) -> str:
    raw = (value or "").strip().lstrip("#").upper()
    if len(raw) == 6 and all(c in "0123456789ABCDEF" for c in raw):
        return raw
    return DEFAULT_TEAM_COLOR


def get_team_color(team_code: str | None) -> str:
    team = normalize(team_code)
    return safe_hex(TEAM_COLORS.get(team, DEFAULT_TEAM_COLOR))


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
    values = sheet.get("A4:H")

    if not values or len(values) < 2:
        return []

    headers = values[0]
    rows = values[1:]

    expected_headers = [
        "Player Image",
        "Team Image",
        "Username",
        "Team",
        "GP",
        "G",
        "A",
        "PTS",
    ]

    if headers != expected_headers:
        raise HTTPException(
            status_code=500,
            detail=f"Header row mismatch in '{worksheet_name}'. Found: {headers}"
        )

    records = []
    for row in rows:
        padded = row + [""] * (len(expected_headers) - len(row))
        trimmed = padded[:len(expected_headers)]
        if not any(str(cell).strip() for cell in trimmed):
            continue
        records.append(dict(zip(expected_headers, trimmed)))

    return records


def search_players(query_text: str = "", position_type: str | None = None, season_type: str | None = None, limit: int = 10):
    worksheet_name = get_worksheet_name(position_type or "Skater", season_type or "Regular")
    records = get_all_players(worksheet_name)
    q = normalize(query_text)

    matches = []
    for row in records:
        name = row.get("Username", "")
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
    target = normalize(player_name)

    for row in records:
        if normalize(row.get("Username")) == target:
            return row
    return None


def build_stats(row: dict):
    return [
        {"label": "GP", "value": row.get("GP", "")},
        {"label": "G", "value": row.get("G", "")},
        {"label": "A", "value": row.get("A", "")},
        {"label": "PTS", "value": row.get("PTS", "")}
    ]


def build_player_payload(player_name: str, worksheet_name: str):
    row = find_player(player_name, worksheet_name)
    if not row:
        raise HTTPException(status_code=404, detail=f"Player not found in '{worksheet_name}': {player_name}")

    team = row.get("Team", "")
    return {
        "player_name": row.get("Username"),
        "team": team,
        "headshot_url": row.get("Player Image"),
        "team_logo_url": row.get("Team Image"),
        "team_color": get_team_color(team),
        "stats": build_stats(row)
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("control.html", {"request": request, "default_color": DEFAULT_TEAM_COLOR, "team_colors": TEAM_COLORS})


@app.get("/control", response_class=HTMLResponse)
async def control_page(request: Request):
    return templates.TemplateResponse("control.html", {"request": request, "default_color": DEFAULT_TEAM_COLOR, "team_colors": TEAM_COLORS})


@app.get("/graphics/bottom-bar", response_class=HTMLResponse)
async def graphics_bottom_bar(request: Request):
    return templates.TemplateResponse("graphics_bottom_bar.html", {"request": request})


@app.get("/graphics/full-screen", response_class=HTMLResponse)
async def graphics_full_screen(request: Request):
    return templates.TemplateResponse("graphics_full_screen.html", {"request": request})


@app.get("/graphics/head-to-head", response_class=HTMLResponse)
async def graphics_head_to_head(request: Request):
    return templates.TemplateResponse("graphics_head_to_head.html", {"request": request})


@app.get("/api/live")
async def get_live():
    return JSONResponse(LIVE_GRAPHIC_STATE)


@app.get("/api/team-colors")
async def get_team_colors():
    return {"default_color": DEFAULT_TEAM_COLOR, "team_colors": TEAM_COLORS}


@app.get("/api/players")
async def api_players(
    q: str = Query(default=""),
    position_type: str = Query(default="Skater"),
    season_type: str = Query(default="Regular"),
    limit: int = Query(default=10)
):
    return {"results": search_players(q, position_type, season_type, limit)}


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
        live_label = f"{players[0]['player_name']} • {players[1]['player_name']} • FACE TO FACE"
    else:
        live_label = f"{players[0]['player_name']} • {graphic_style.upper()}"

    LIVE_GRAPHIC_STATE["graphic_style"] = graphic_style
    LIVE_GRAPHIC_STATE["position_type"] = position_type
    LIVE_GRAPHIC_STATE["season_type"] = season_type
    LIVE_GRAPHIC_STATE["worksheet_name"] = worksheet_name
    LIVE_GRAPHIC_STATE["players"] = players
    LIVE_GRAPHIC_STATE["visible"] = True
    LIVE_GRAPHIC_STATE["live_label"] = live_label
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
    LIVE_GRAPHIC_STATE["live_label"] = "EMPTY"
    LIVE_GRAPHIC_STATE["version"] += 1
    return {"ok": True}


@app.post("/api/refresh-sheet")
async def refresh_sheet():
    refresh_sheet_cache()
    return {"ok": True}
