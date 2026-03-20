from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LIVE_GRAPHIC_STATE = {
    "graphic_style": None,
    "position_type": None,
    "season_type": None,
    "players": []
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_gsheet_client():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

    creds_dict = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(credentials)


def get_players_sheet():
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        raise RuntimeError("GOOGLE_SHEETS_ID not set")

    client = get_gsheet_client()
    workbook = client.open_by_key(spreadsheet_id)
    return workbook.worksheet("players")


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def find_player(player_name: str):
    sheet = get_players_sheet()
    records = sheet.get_all_records()

    for row in records:
        if normalize(row.get("player_name")) == normalize(player_name):
            return row
    return None


def build_stats(row: dict, position_type: str, season_type: str):
    season_prefix = "regular" if season_type == "Regular" else "playoffs"

    if position_type == "Skater":
        return {
            "GP": row.get(f"{season_prefix}_skater_gp", ""),
            "G": row.get(f"{season_prefix}_skater_g", ""),
            "A": row.get(f"{season_prefix}_skater_a", ""),
            "PTS": row.get(f"{season_prefix}_skater_pts", ""),
            "PIM": row.get(f"{season_prefix}_skater_pim", "")
        }

    if position_type == "Goalie":
        return {
            "GP": row.get(f"{season_prefix}_goalie_gp", ""),
            "W": row.get(f"{season_prefix}_goalie_w", ""),
            "GAA": row.get(f"{season_prefix}_goalie_gaa", ""),
            "SV%": row.get(f"{season_prefix}_goalie_sv_pct", ""),
            "SO": row.get(f"{season_prefix}_goalie_so", "")
        }

    raise HTTPException(status_code=400, detail="Invalid position type")


def build_player_payload(player_name: str, position_type: str, season_type: str):
    row = find_player(player_name)
    if not row:
        raise HTTPException(status_code=404, detail=f"Player not found: {player_name}")

    return {
        "player_name": row.get("player_name"),
        "team": row.get("team"),
        "position_type": row.get("position_type"),
        "headshot_url": row.get("headshot_url"),
        "team_logo_url": row.get("team_logo_url"),
        "stats": build_stats(row, position_type, season_type)
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})


@app.get("/control", response_class=HTMLResponse)
async def control_page(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})


@app.post("/api/set-live")
async def set_live(
    graphic_style: str = Form(...),
    position_type: str = Form(...),
    season_type: str = Form(...),
    player_name_1: str = Form(...),
    player_name_2: str = Form("")
):
    players = [build_player_payload(player_name_1, position_type, season_type)]

    if graphic_style == "Head to Head":
        if not player_name_2.strip():
            raise HTTPException(status_code=400, detail="Second player is required for Head to Head")
        players.append(build_player_payload(player_name_2, position_type, season_type))

    LIVE_GRAPHIC_STATE["graphic_style"] = graphic_style
    LIVE_GRAPHIC_STATE["position_type"] = position_type
    LIVE_GRAPHIC_STATE["season_type"] = season_type
    LIVE_GRAPHIC_STATE["players"] = players

    return {"ok": True, "live_state": LIVE_GRAPHIC_STATE}


@app.get("/api/live")
async def get_live():
    return JSONResponse(LIVE_GRAPHIC_STATE)


@app.get("/api/clear")
async def clear_live():
    LIVE_GRAPHIC_STATE["graphic_style"] = None
    LIVE_GRAPHIC_STATE["position_type"] = None
    LIVE_GRAPHIC_STATE["season_type"] = None
    LIVE_GRAPHIC_STATE["players"] = []
    return {"ok": True}


@app.get("/graphics/live", response_class=HTMLResponse)
async def graphics_live(request: Request):
    return templates.TemplateResponse(
        "graphics_live.html",
        {
            "request": request,
            "live": LIVE_GRAPHIC_STATE
        }
    )
