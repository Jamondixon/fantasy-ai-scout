import streamlit as st
import pandas as pd
import requests
import textwrap
import plotly.express as px
from espn_api.football import League
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================================================
# 1. PAGE SETUP & THEME ENGINE
# =========================================================
st.set_page_config(
    page_title="Scout | Fantasy Football AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

   /* Hero Top Bar matching Run Waiver Analysis Button */
    .hero-banner {
        background: #0F766E;
        border: 1.5px solid #115E59;
        border-radius: 10px;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 22px;
        box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25);
    }
    .hero-icon {
        font-size: 28px;
        line-height: 1;
    }
    .hero-title {
        font-size: 1.55rem;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: 0.2px;
        text-transform: uppercase;
        margin: 0;
    }
    .hero-tag {
        font-size: 0.8rem;
        font-weight: 700;
        background: #115E59;
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        padding: 4px 10px;
        margin-left: auto;
        letter-spacing: 0.5px;
    }

    /* Expander Section Headers (Active Squad & Available Wire, Standings, etc.) */
    div[data-testid="stExpander"] details summary p {
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: 0.3px !important;
        text-transform: uppercase !important;
    }

    /* Grid Frame Sub-titles inside Cards */
    .grid-frame div {
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        color: #334155 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Bold Data Grid Framing & Shadows */
    .grid-frame {
        background: #FFFFFF;
        border: 2px solid #94A3B8;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
        margin-bottom: 8px;
    }

    /* Scrollable Container Wrapper */
    .table-scroll-container {
        max-height: 320px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1.5px solid #CBD5E1;
        border-radius: 8px;
        background: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Sleeper Table with Sticky, Centered Headers and Values */
    .sleeper-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center !important;
    }
    .sleeper-table th {
        position: sticky;
        top: 0;
        z-index: 2;
        background: #F8FAFC !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 10px 14px;
        border-bottom: 2px solid #CBD5E1;
        text-align: center !important;
    }
    .sleeper-table td {
        font-size: 0.9rem;
        color: #0F172A;
        padding: 8px 14px;
        border-bottom: 1px solid #E2E8F0;
        text-align: center !important;
    }
    .sleeper-table tr:hover {
        background-color: #F1F5F9;
    }
    /* Sleeper Base Card */
    .sleeper-card {
        background: #F8FAFC;
        border: 1.5px solid #CBD5E1;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

   /* Match Expander Modules (A, B, C) to .grid-frame */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 2px solid #94A3B8 !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.08) !important;
        margin-bottom: 18px !important;
        overflow: visible !important;
    }

    div[data-testid="stExpander"] details {
        border: none !important;
        background: transparent !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] details summary {
        border-bottom: 2px solid #E2E8F0 !important;
        padding: 14px 18px !important;
        border-top-left-radius: 8px !important;
        border-top-right-radius: 8px !important;
    }

    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 18px !important;
    }

    /* Sub-headers and Meta Labels */
    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.2px;
        margin-bottom: 4px;
    }
    .meta-caption {
        font-size: 0.85rem;
        font-weight: 700;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    /* Custom Button Overrides */
    div.stButton > button {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 20px !important;
        letter-spacing: 0.3px !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #115E59 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3) !important;
    }

    /* High-Contrast Callout Box */
    .callout-box {
        background: #F0FDFA;
        border: 1px solid #99F6E4;
        border-left: 5px solid #0F766E;
        border-radius: 4px 6px 6px 4px;
        padding: 14px 18px;
        margin-bottom: 14px;
        color: #0F172A;
        font-size: 14.5px;
        line-height: 1.55;
    }

    /* Force high-specificity color for white cards in sidebar */
    section[data-testid="stSidebar"] .nfl-game-card,
    section[data-testid="stSidebar"] .nfl-game-card * {
        color: #0F172A !important;
    }

    section[data-testid="stSidebar"] .nfl-game-header span {
        color: #64748B !important;
    }

    section[data-testid="stSidebar"] .nfl-team-row.winner span {
        color: #0F766E !important;
        font-weight: 800 !important;
    }

    /* Sidebar matching Run Waiver Analysis Button */
    section[data-testid="stSidebar"] {
        background-color: #0F766E !important;
    }

    /* Crisp white text & headers on the deep teal background */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .meta-caption {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Clean white inputs with dark text for legibility */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #115E59 !important;
        border-radius: 6px !important;
    }

    /* Streak Status Badges */
    .badge-win {
        background-color: rgba(16, 185, 129, 0.15);
        color: #059669;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #10B981;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
    .badge-loss {
        background-color: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #EF4444;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }

    /* Subdued divider lines */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* High Specificity Force: White Background & Teal Text for Sidebar Cards */
    section[data-testid="stSidebar"] div.nfl-game-card {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
    }

    section[data-testid="stSidebar"] div.nfl-game-card * {
        background-color: transparent !important;
        color: #0F766E !important;
        -webkit-text-fill-color: #0F766E !important;
    }

    section[data-testid="stSidebar"] div.nfl-game-card .nfl-game-header {
        display: flex !important;
        justify-content: space-between !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        border-bottom: 1.5px solid #E2E8F0 !important;
        padding-bottom: 4px !important;
        margin-bottom: 6px !important;
    }

    section[data-testid="stSidebar"] div.nfl-game-card .nfl-team-row {
        display: flex !important;
        justify-content: space-between !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin-bottom: 3px !important;
    }

    section[data-testid="stSidebar"] div.nfl-game-card .nfl-team-row.winner * {
        font-weight: 900 !important;
        color: #115E59 !important;
        -webkit-text-fill-color: #115E59 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. CREDENTIALS & SECRETS
# =========================================================
LEAGUE_ID = int(st.secrets["LEAGUE_ID"])
YEAR = int(st.secrets["YEAR"])
SWID = st.secrets["SWID"]
ESPN_S2 = st.secrets["ESPN_S2"]
API_KEY = st.secrets["GEMINI_API_KEY"]

# Google GenAI Client
client = genai.Client(api_key=API_KEY)
# =========================================================
# 3. DATA LOADING & CACHING
# =========================================================
@st.cache_resource(ttl=600)
def load_espn_league():
    return League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

try:
    with st.spinner("Syncing league environment..."):
        league = load_espn_league()
        free_agents = league.free_agents(size=15)
except Exception as e:
    st.error(f"League connection failed: {e}")
    st.stop()


# =========================================================
# 4. SIDEBAR NAVIGATION & MATCHUPS
# =========================================================

def format_game_status_cst(event, status_obj):
    """
    Formats the game status/time to Central Time (CST/CDT) for scheduled games.
    Preserves in-progress (e.g., 'Q2 08:31') and completed (e.g., 'Final') statuses.
    """
    state = status_obj.get("state", "").lower()
    raw_status = (
        status_obj.get("shortDetail")
        or status_obj.get("detail")
        or status_obj.get("description")
        or "Scheduled"
    )

    # If the game is already live or finished, keep the clock/final status intact
    if state in ["in", "post"] or any(k in raw_status.lower() for k in ["final", "end", "half", "delayed"]):
        return raw_status

    # For pre-game / scheduled matchups, parse the ISO date string to Central Time
    date_str = event.get("date")
    if date_str:
        try:
            # Normalize ISO string ending in Z to +00:00
            if date_str.endswith("Z"):
                date_str = date_str[:-1] + "+00:00"
            
            utc_dt = datetime.fromisoformat(date_str)
            central_tz = ZoneInfo("America/Chicago")
            central_dt = utc_dt.astimezone(central_tz)

            # Formats as "Sun 12:00 PM CDT" or "Mon 7:15 PM CST"
            # Remove leading zero on hour for macOS/Linux (-I)
            time_part = central_dt.strftime("%-I:%M %p %Z")
            day_part = central_dt.strftime("%a")
            return f"{day_part} {time_part}"
        except Exception:
            pass

    return raw_status

@st.cache_data(ttl=1800)
def get_nfl_weather_map():
    """
    Builds an accurate weather badge mapping for all 32 NFL teams.
    Checks ESPN live game feeds first, falls back to Open-Meteo for outdoor venues,
    and automatically identifies domes.
    """
    weather_map = {}
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    headers = {"User-Agent": "Mozilla/5.0"}

    # Track which teams got resolved from ESPN
    resolved_teams = set()

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for event in data.get("events", []):
                comps = event.get("competitions", [{}])[0]
                competitors = comps.get("competitors", [])

                home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})
                home_team = (
                    home_comp.get("team", {}).get("abbreviation") 
                    or home_comp.get("team", {}).get("shortDisplayName") 
                    or ""
                ).upper()

                # Venue dome status
                venue = comps.get("venue", {})
                is_indoor = venue.get("indoor", False) or STADIUM_COORDS.get(home_team, (0, 0, False))[2]

                # Weather parsing
                weather_info = comps.get("weather") or event.get("weather") or {}
                display_text = str(weather_info.get("displayValue", "")).lower()
                temp = weather_info.get("temperature")
                temp_str = f" {temp}°F" if temp is not None else ""

                if is_indoor:
                    badge = '<span title="Indoor / Retractable Dome">🏟️ Dome</span>'
                elif any(w in display_text for w in ["rain", "shower", "drizzle", "t-storm", "storm", "precip"]):
                    badge = f'<span title="Rain">🌧️ Rain{temp_str}</span>'
                elif any(w in display_text for w in ["snow", "blizzard", "flurries", "sleet", "ice"]):
                    badge = f'<span title="Snow">❄️ Snow{temp_str}</span>'
                elif any(w in display_text for w in ["cloud", "overcast", "fog", "haze"]):
                    badge = f'<span title="Cloudy">☁️ Cloud{temp_str}</span>'
                elif any(w in display_text for w in ["wind", "breezy"]):
                    badge = f'<span title="Windy">💨 Wind{temp_str}</span>'
                elif any(w in display_text for w in ["clear", "sunny", "fair"]):
                    badge = f'<span title="Clear/Sunny">☀️ Sun{temp_str}</span>'
                elif temp is not None:
                    badge = f'<span title="Temperature">🌡️ {temp}°F</span>'
                else:
                    # Fallback to stadium weather API
                    badge = f'<span title="Live Venue">{get_live_venue_weather(home_team)}</span>'

                # Map to both competitors in this game
                for comp in competitors:
                    abbr = comp.get("team", {}).get("abbreviation", "").upper()
                    if abbr:
                        weather_map[abbr] = badge
                        resolved_teams.add(abbr)
    except Exception as e:
        print(f"Weather map fetch error: {e}")

    # Safety Fallback: Populate any teams on Bye or not yet scheduled
    for team_abbr in STADIUM_COORDS.keys():
        if team_abbr not in resolved_teams:
            lat, lon, is_dome = STADIUM_COORDS[team_abbr]
            if is_dome:
                weather_map[team_abbr] = '<span title="Indoor Dome">🏟️ Dome</span>'
            else:
                weather_map[team_abbr] = f'<span title="Live Venue">{get_live_venue_weather(team_abbr)}</span>'

    # Fallback for free agents with FA or empty team
    weather_map["FA"] = '<span title="Free Agent / Bye">-</span>'
    weather_map[""] = '<span title="Free Agent / Bye">-</span>'

    return weather_map

# NFL Stadium coordinates for bulletproof live weather fallback
STADIUM_COORDS = {
    "ARI": (33.5276, -112.2626, True),   # State Farm Stadium (Dome)
    "ATL": (33.7554, -84.4010, True),    # Mercedes-Benz Stadium (Dome)
    "BAL": (39.2780, -76.6227, False),   # M&T Bank Stadium
    "BUF": (42.7738, -78.7870, False),   # Highmark Stadium
    "CAR": (35.2258, -80.8528, False),   # Bank of America Stadium
    "CHI": (41.8623, -87.6167, False),   # Soldier Field
    "CIN": (39.0955, -84.5161, False),   # Paycor Stadium
    "CLE": (41.5061, -81.6995, False),   # Huntington Bank Field
    "DAL": (32.7473, -97.0945, True),    # AT&T Stadium (Dome)
    "DEN": (39.7439, -105.0201, False),  # Empower Field at Mile High
    "DET": (42.3400, -83.0456, True),    # Ford Field (Dome)
    "GB":  (44.5013, -88.0622, False),   # Lambeau Field
    "HOU": (29.6847, -95.4107, True),    # NRG Stadium (Dome)
    "IND": (39.7601, -86.1639, True),    # Lucas Oil Stadium (Dome)
    "JAX": (30.3240, -81.6373, False),   # EverBank Stadium
    "KC":  (39.0489, -94.4839, False),   # Arrowhead Stadium
    "LV":  (36.0909, -115.1833, True),   # Allegiant Stadium (Dome)
    "LAC": (33.9535, -118.3392, True),   # SoFi Stadium (Dome)
    "LAR": (33.9535, -118.3392, True),   # SoFi Stadium (Dome)
    "MIA": (25.9580, -80.2389, False),   # Hard Rock Stadium
    "MIN": (44.9735, -93.2575, True),    # U.S. Bank Stadium (Dome)
    "NE":  (42.0909, -71.2643, False),   # Gillette Stadium
    "NO":  (29.9511, -90.0812, True),    # Caesars Superdome (Dome)
    "NYG": (40.8128, -74.0742, False),   # MetLife Stadium
    "NYJ": (40.8128, -74.0742, False),   # MetLife Stadium
    "PHI": (39.9008, -75.1675, False),   # Lincoln Financial Field
    "PIT": (40.4468, -80.0158, False),   # Acrisure Stadium
    "SF":  (37.4033, -121.9694, False),  # Levi's Stadium
    "SEA": (47.5952, -122.3316, False),  # Lumen Field
    "TB":  (27.9759, -82.5033, False),   # Raymond James Stadium
    "TEN": (36.1665, -86.7713, False),   # Nissan Stadium
    "WAS": (38.9076, -76.8645, False),   # Northwest Stadium
}

def get_live_venue_weather(home_team_abbr):
    """Fallback: Queries Open-Meteo for real-time temperature and condition code."""
    venue_info = STADIUM_COORDS.get(home_team_abbr.upper())
    if not venue_info:
        return "☀️ 72°F"
    lat, lon, is_dome = venue_info
    if is_dome:
        return "🏟️ Dome"

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
        r = requests.get(url, timeout=3).json().get("current", {})
        temp = round(r.get("temperature_2m", 70))
        code = r.get("weather_code", 0)

        # WMO Weather interpretation codes
        if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return f"🌧️ {temp}°F"
        elif code in [71, 73, 75, 77, 85, 86]:
            return f"❄️ {temp}°F"
        elif code in [95, 96, 99]:
            return f"⛈️ {temp}°F"
        elif code in [1, 2, 3]:
            return f"☁️ {temp}°F"
        elif code in [45, 48]:
            return f"🌫️ {temp}°F"
        return f"☀️ {temp}°F"
    except Exception:
        return "☀️ 70°F"


@st.cache_data(ttl=300)
def get_nfl_matchups_data():
    """Fetches the current week's NFL games and displays times in Central Time."""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    headers = {"User-Agent": "Mozilla/5.0"}
    games = []

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for event in data.get("events", []):
                comps = event.get("competitions", [{}])[0]
                status_obj = event.get("status", {}).get("type", {})

                # --- Convert Game Time to Central Time ---
                game_status = format_game_status_cst(event, status_obj)

                competitors = comps.get("competitors", [])
                away_comp = next((c for c in competitors if c.get("homeAway") == "away"), {})
                home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})

                away_team = (
                    away_comp.get("team", {}).get("abbreviation")
                    or away_comp.get("team", {}).get("shortDisplayName")
                    or "AWAY"
                )
                home_team = (
                    home_comp.get("team", {}).get("abbreviation")
                    or home_comp.get("team", {}).get("shortDisplayName")
                    or "HOME"
                )

                a_score = away_comp.get("score")
                h_score = home_comp.get("score")
                away_score = str(a_score) if a_score is not None and str(a_score).strip() != "" else "-"
                home_score = str(h_score) if h_score is not None and str(h_score).strip() != "" else "-"

                away_winner = bool(away_comp.get("winner", False))
                home_winner = bool(home_comp.get("winner", False))

                # Dome & Venue Weather Check
                venue = comps.get("venue", {})
                is_indoor = venue.get("indoor", False) or STADIUM_COORDS.get(home_team.upper(), (0, 0, False))[2]

                weather_info = comps.get("weather") or event.get("weather") or {}
                display_text = str(weather_info.get("displayValue", "")).lower()
                temp = weather_info.get("temperature")
                temp_display = f" {temp}°F" if temp is not None else ""

                if is_indoor:
                    wx_icon = "🏟️ Dome"
                elif any(w in display_text for w in ["rain", "shower", "drizzle", "t-storm", "storm", "precip"]):
                    wx_icon = f"🌧️{temp_display}".strip()
                elif any(w in display_text for w in ["snow", "blizzard", "flurries", "sleet", "ice"]):
                    wx_icon = f"❄️{temp_display}".strip()
                elif any(w in display_text for w in ["cloud", "overcast", "fog", "haze"]):
                    wx_icon = f"☁️{temp_display}".strip()
                elif any(w in display_text for w in ["wind", "breezy"]):
                    wx_icon = f"💨{temp_display}".strip()
                elif any(w in display_text for w in ["clear", "sunny", "fair"]):
                    wx_icon = f"☀️{temp_display}".strip()
                elif temp is not None:
                    wx_icon = f"🌡️ {temp}°F"
                else:
                    wx_icon = get_live_venue_weather(home_team)

                games.append({
                    "status": game_status,
                    "away_team": away_team,
                    "home_team": home_team,
                    "away_score": away_score,
                    "home_score": home_score,
                    "away_winner": away_winner,
                    "home_winner": home_winner,
                    "weather": wx_icon
                })
    except Exception as e:
        print(f"ESPN Matchups fetch error: {e}")

    return games

with st.sidebar:
    st.markdown(f"### {league.settings.name}")
    st.caption(f"ESPN Season {YEAR} • {len(league.teams)} Clubs")

    team_options = {team.team_name: team for team in league.teams}
    selected_team_name = st.selectbox("Active Roster", options=list(team_options.keys()))
    my_team = team_options[selected_team_name]

    st.divider()

    st.markdown("<div class='meta-caption'>Workspace</div>", unsafe_allow_html=True)

    active_page = st.radio(
        "Navigation",
        options=[
            "Waiver Wire Scout",
            "Start/Sit Debater",
            "Trade Evaluator",
            "Positional Economy"
        ],
        label_visibility="collapsed"
    )

    # --- Weekly NFL Matchups & Weather Cards ---
    st.divider()
    st.markdown("<div class='meta-caption' style='margin-bottom: 8px;'>Weekly NFL Matchups</div>", unsafe_allow_html=True)

    nfl_games = get_nfl_matchups_data()

    if nfl_games:
        cards_list = []
        for g in nfl_games:
            away_win_class = "winner" if g["away_winner"] else ""
            home_win_class = "winner" if g["home_winner"] else ""

            card_html = f"""
<div class="nfl-game-card">
    <div class="nfl-game-header">
        <span>{g['status']}</span>
        <span>{g['weather']}</span>
    </div>
    <div class="nfl-team-row {away_win_class}">
        <span>{g['away_team']}</span>
        <span>{g['away_score']}</span>
    </div>
    <div class="nfl-team-row {home_win_class}">
        <span>{g['home_team']}</span>
        <span>{g['home_score']}</span>
    </div>
</div>
"""
            cards_list.append(textwrap.dedent(card_html).strip())

        full_html = f'<div style="max-height: 480px; overflow-y: auto; padding-right: 4px;">{"".join(cards_list)}</div>'
        st.markdown(full_html, unsafe_allow_html=True)
    else:
        st.caption("No NFL matchup data available right now.")
# =========================================================
# 5. DYNAMIC HERO TOP BAR
# =========================================================
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">{active_page}</div>
    <div class="hero-tag">{my_team.team_name}</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 6. PERSISTENT LEAGUE MODULES (COLLAPSIBLE)
# =========================================================

# --- Module A: Squad & Wire Grids (Scrollable with Weather Icons) ---
weather_map = get_nfl_weather_map()

def resolve_player_wx(player):
    """Safely retrieves weather badge by player proTeam abbreviation."""
    raw_team = getattr(player, "proTeam", "")
    team_str = str(raw_team).strip().upper()
    return weather_map.get(team_str, "☀️ 70°F")

with st.expander("Active Squad & Available Wire", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="grid-frame">
            <div style="font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; margin-bottom: 8px;">
                {my_team.team_name} Depth Chart
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        df_roster = pd.DataFrame([
            {
                "SLOT": getattr(p, "lineupSlot", "BE"),
                "PLAYER": p.name,
                "POS": p.position,
                "TEAM": getattr(p, "proTeam", "-").upper(),
                "WX": resolve_player_wx(p),
                "TOTAL PTS": f"{p.total_points:.1f}"
            }
            for p in my_team.roster
        ])
        st.markdown(
            f'<div class="table-scroll-container">{df_roster.to_html(classes="sleeper-table", index=False, escape=False)}</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown("""
        <div class="grid-frame">
            <div style="font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; margin-bottom: 8px;">
                Top Available Waivers
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        df_fa = pd.DataFrame([
            {
                "PLAYER": p.name,
                "POS": p.position,
                "TEAM": getattr(p, "proTeam", "-").upper(),
                "WX": resolve_player_wx(p),
                "TOTAL PTS": f"{p.total_points:.1f}"
            }
            for p in free_agents
        ])
        st.markdown(
            f'<div class="table-scroll-container">{df_fa.to_html(classes="sleeper-table", index=False, escape=False)}</div>',
            unsafe_allow_html=True
        )
# --- Module B: Matchup Scoreboard ---
with st.expander(f"Weekly Matchup Scoreboard (Week {league.current_week})", expanded=False):
    selected_week = st.slider("Select Matchup Week", min_value=1, max_value=18, value=int(league.current_week))
    try:
        box_scores = league.box_scores(week=selected_week)
        col_m1, col_m2 = st.columns(2)
        for idx, match in enumerate(box_scores):
            target_col = col_m1 if idx % 2 == 0 else col_m2
            with target_col:
                st.markdown(f"""
                <div class='sleeper-card' style='margin-bottom: 12px;'>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #E2E8F0;">
                        <div>
                            <span style="font-weight: 800; font-size: 15px; color: #0F172A;">{match.home_team.team_name}</span>
                            <span style="font-size: 12px; color: #64748B; margin-left: 6px;">({match.home_team.wins}-{match.home_team.losses})</span>
                        </div>
                        <div style="font-size: 18px; font-weight: 800; color: #0F766E;">{match.home_score:.1f}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px;">
                        <div>
                            <span style="font-weight: 800; font-size: 15px; color: #0F172A;">{match.away_team.team_name}</span>
                            <span style="font-size: 12px; color: #64748B; margin-left: 6px;">({match.away_team.wins}-{match.away_team.losses})</span>
                        </div>
                        <div style="font-size: 18px; font-weight: 800; color: #0F766E;">{match.away_score:.1f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as err:
        st.warning(f"Could not load box scores for Week {selected_week}: {err}")


# --- Module C: League Standings (Scrollable with Sticky Styled Headers) ---
with st.expander("Championship Standings", expanded=False):
    def get_manager_name(team):
        """Extracts manager name reliably from ESPN API team object."""
        owners = getattr(team, "owners", None)
        if owners and isinstance(owners, list) and len(owners) > 0:
            first_owner = owners[0]
            if isinstance(first_owner, dict):
                first = first_owner.get("firstName", "")
                last = first_owner.get("lastName", "")
                display = first_owner.get("displayName", "")
                full = f"{first} {last}".strip()
                return full if full else (display if display else "Manager")
            elif isinstance(first_owner, str):
                return first_owner
        
        for attr in ["owner", "primary_owner", "manager"]:
            val = getattr(team, attr, None)
            if val and isinstance(val, str):
                return val
                
        return "Manager"

    def format_streak(streak_type, streak_length):
        """Returns colored badge HTML based on Win/Loss streak."""
        st_type = str(streak_type).strip().upper()
        length = str(streak_length).strip()
        label = f"{st_type} {length}".strip()

        if not label:
            return "-"
        
        if "WIN" in st_type or st_type == "W":
            return f'<span class="badge-win">{label}</span>'
        elif "LOSS" in st_type or st_type == "L":
            return f'<span class="badge-loss">{label}</span>'
        return label

    standings_rows = []
    sorted_teams = sorted(league.teams, key=lambda t: (getattr(t, 'standing', 99), -t.wins, -t.points_for))

    for rank, t in enumerate(sorted_teams, start=1):
        st_type = getattr(t, 'streak_type', '')
        st_len = getattr(t, 'streak_length', '')

        standings_rows.append({
            "RANK": rank,
            "TEAM": t.team_name,
            "MANAGER": get_manager_name(t),
            "W-L": f"{t.wins}-{t.losses}" + (f"-{t.ties}" if getattr(t, 'ties', 0) > 0 else ""),
            "PF": f"{t.points_for:.1f}",
            "PA": f"{t.points_against:.1f}",
            "STREAK": format_streak(st_type, st_len)
        })

    df_standings = pd.DataFrame(standings_rows)
    st.markdown(
        f'<div class="table-scroll-container">{df_standings.to_html(classes="sleeper-table", index=False, escape=False)}</div>',
        unsafe_allow_html=True
    )

st.divider()

# =========================================================
# 7. PYDANTIC SCHEMAS & VERDICT PALETTES
# =========================================================
class WaiverRecommendation(BaseModel):
    drop_player: str
    add_free_agent: str
    reasoning: str
    upgrade_confidence: int

class ScoutReport(BaseModel):
    team_summary: str
    weakest_position: str
    recommendations: list[WaiverRecommendation]

class TradeEvaluation(BaseModel):
    verdict: Literal[
        "Seems Fair",
        "Getting Fleeced",
        "Everybody Wins",
        "Collusion Warning",
        "Slightly Off"
    ]
    fairness_score: int
    your_team_impact: str
    opponent_team_impact: str
    risk_factors: list[str]
    bottom_line: str

class PositionInsight(BaseModel):
    position: str
    status: Literal["CRITICAL_DROUGHT", "BALANCED", "SURPLUS_AVAILABLE"]
    advice: str

class ScarcityReport(BaseModel):
    executive_summary: str
    hardest_position_to_acquire: str
    insights: list[PositionInsight]

SLEEPER_VERDICTS = {
    "Seems Fair": {"bg": "#ECFDF5", "text": "#065F46", "border": "#10B981"},
    "Everybody Wins": {"bg": "#EFF6FF", "text": "#1E40AF", "border": "#3B82F6"},
    "Slightly Off": {"bg": "#FFFBEB", "text": "#92400E", "border": "#F59E0B"},
    "Getting Fleeced": {"bg": "#FDF2F8", "text": "#9D174D", "border": "#EC4899"},
    "Collusion Warning": {"bg": "#FEF2F2", "text": "#991B1B", "border": "#EF4444"},
}

STATUS_TAGS = {
    "CRITICAL_DROUGHT": {"bg": "#FEF2F2", "text": "#991B1B", "border": "#EF4444", "label": "Critical Drought"},
    "BALANCED": {"bg": "#EFF6FF", "text": "#1E40AF", "border": "#3B82F6", "label": "Balanced"},
    "SURPLUS_AVAILABLE": {"bg": "#ECFDF5", "text": "#065F46", "border": "#10B981", "label": "Surplus Wire"}
}

# ESPN official Pro Team ID mapping (overrides outdated package defaults)
ESPN_PRO_TEAMS = {
    0: "FA", 1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL",
    7: "DEN", 8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV",
    14: "LAR", 15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ",
    21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC", 25: "SF", 26: "SEA", 27: "TB",
    28: "WAS", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU"
}

def get_player_team_abbr(player):
    """Accurately resolves a player's real NFL team abbreviation."""
    raw_team = getattr(player, "proTeam", "")
    if isinstance(raw_team, int):
        return ESPN_PRO_TEAMS.get(raw_team, "FA")
    if str(raw_team).isdigit():
        return ESPN_PRO_TEAMS.get(int(raw_team), "FA")
    team_str = str(raw_team).strip().upper()
    return team_str if team_str else "FA"

# =========================================================
# PAGE 1: WAIVER WIRE SCOUT
# =========================================================
if active_page == "Waiver Wire Scout":
    st.markdown("<div class='section-title'>Waiver Wire Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='meta-caption'>AI Roster Audit & Free Agent Targets</div>", unsafe_allow_html=True)

    if st.button("Run Waiver Analysis"):
        with st.spinner("Scouting wire candidates..."):
            client = genai.Client(api_key=API_KEY)
            prompt = f"""
            Analyze this Fantasy Football squad and suggest moves based on the available waiver wire pool.
            Team: {my_team.team_name}
            Roster: {roster_rows}
            Available Free Agents: {fa_rows}
            Tone: Sharp, quantitative, no introductory fluff.
            """

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ScoutReport,
                )
            )
            report = ScoutReport.model_validate_json(response.text)

        st.markdown(f"""
        <div class='callout-box'>
            <div style="font-weight: 800; color: #0F766E; margin-bottom: 2px;">ROSTER AUDIT</div>
            <div style="color: #1E293B;">{report.team_summary}</div>
            <div style="margin-top: 8px; font-weight: 700; color: #B45309;">Primary Vulnerability: {report.weakest_position}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 18px;'>Recommended Transactions</div>", unsafe_allow_html=True)
        for rec in report.recommendations:
            st.markdown(f"""
            <div class='sleeper-card'>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="color: #DC2626; font-weight: 800; font-size: 13px;">DROP</span> 
                        <span style="font-weight: 700; font-size: 15px; color: #0F172A; margin-right: 12px;">{rec.drop_player}</span>
                        <span style="color: #64748B; font-weight: bold;">➔</span> 
                        <span style="color: #0F766E; font-weight: 800; font-size: 13px; margin-left: 12px;">ADD</span> 
                        <span style="font-weight: 700; font-size: 15px; color: #0F172A;">{rec.add_free_agent}</span>
                    </div>
                    <div style="color: #334155; font-size: 13px; font-weight: 700;">{rec.upgrade_confidence}% Confidence</div>
                </div>
                <div style="font-size: 14px; color: #334155; line-height: 1.55;">{rec.reasoning}</div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# PAGE 2: START/SIT DEBATER
# =========================================================

elif active_page == "Start/Sit Debater":
    st.markdown('<div class="hero-title">Start / Sit Debater</div>', unsafe_allow_html=True)

    # Pre-build lookup dictionaries and labels
    roster_players = my_team.roster
    roster_options = {
        f"{p.name} ({p.position} - {get_player_team_abbr(p)})": p 
        for p in roster_players
    }
    roster_names = list(roster_options.keys())

    wire_options = {
        f"{p.name} ({p.position} - {get_player_team_abbr(p)})": p 
        for p in free_agents
    }
    wire_names = list(wire_options.keys())

    # --- 2-Column Dilemma Interface ---
    col_roster, col_wire = st.columns(2, gap="large")

    chosen_p1, chosen_p2 = None, None
    debate_trigger = False
    debate_mode = ""


    # -------------------------------------------------------------
    # Column 1: Roster vs Roster
    # -------------------------------------------------------------
    with col_roster:
        st.markdown("""
        <div style="background: #FFFFFF; border: 2px solid #CBD5E1; border-radius: 8px; padding: 18px; margin-bottom: 14px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);">
            <div style="font-size: 16px; font-weight: 900; color: #0F172A; text-transform: uppercase; letter-spacing: 0.025em; margin-bottom: 6px;">
                ⚔️ Roster vs Roster
            </div>
            <div style="font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">
                Compare two starters or bench options on your active squad.
            </div>
        </div>
        """, unsafe_allow_html=True)

        idx_p2 = 1 if len(roster_names) > 1 else 0

        p1_r_name = st.selectbox(
            "Primary Roster Option",
            options=roster_names,
            index=0,
            key="r_vs_r_p1"
        )
        p2_r_name = st.selectbox(
            "Alternative Roster Option",
            options=roster_names,
            index=idx_p2,
            key="r_vs_r_p2"
        )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("⚖️ Debate Internal Roster", use_container_width=True, key="btn_debate_roster"):
            if p1_r_name == p2_r_name:
                st.warning("Please choose two different players to debate.")
            else:
                chosen_p1 = roster_options[p1_r_name]
                chosen_p2 = roster_options[p2_r_name]
                debate_trigger = True
                debate_mode = "Roster vs Roster"

    # -------------------------------------------------------------
    # Column 2: Roster vs Waiver Wire
    # -------------------------------------------------------------
    with col_wire:
        st.markdown("""
        <div style="background: #FFFFFF; border: 2px solid #CBD5E1; border-radius: 8px; padding: 18px; margin-bottom: 14px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);">
            <div style="font-size: 16px; font-weight: 900; color: #0F172A; text-transform: uppercase; letter-spacing: 0.025em; margin-bottom: 6px;">
                🔄 Roster vs Waiver Wire
            </div>
            <div style="font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">
                Determine if a top free agent warrants starting over your current asset.
            </div>
        </div>
        """, unsafe_allow_html=True)

        p1_w_name = st.selectbox(
            "Current Roster Player",
            options=roster_names,
            index=0,
            key="r_vs_w_p1"
        )
        p2_w_name = st.selectbox(
            "Available Wire Prospect",
            options=wire_names,
            index=0,
            key="r_vs_w_p2"
        )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Debate Wire Pivot", use_container_width=True, key="btn_debate_wire"):
            chosen_p1 = roster_options[p1_w_name]
            chosen_p2 = wire_options[p2_w_name]
            debate_trigger = True
            debate_mode = "Roster vs Waiver Wire"

    # -------------------------------------------------------------
    # Render AI Evaluation & Metrics on Trigger
    # -------------------------------------------------------------
    if debate_trigger and chosen_p1 and chosen_p2:
        st.divider()
        st.markdown(f"<div class='meta-caption'>Evaluation Matrix: {debate_mode}</div>", unsafe_allow_html=True)

        # 1. Metric Cards Side-by-Side
        m1, m2 = st.columns(2)
        wx_map = get_nfl_weather_map()

        p1_team = get_player_team_abbr(chosen_p1)
        p2_team = get_player_team_abbr(chosen_p2)

        with m1:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #0F766E; border-radius: 8px; padding: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 11px; font-weight: 800; color: #0F766E; text-transform: uppercase;">Option 1</div>
                <div style="font-size: 18px; font-weight: 900; color: #0F172A; margin: 2px 0;">{chosen_p1.name}</div>
                <div style="font-size: 13px; color: #64748B;">{chosen_p1.position} • {p1_team} | {wx_map.get(p1_team, '☀️ 70°F')}</div>
                <div style="margin-top: 8px; font-size: 14px; font-weight: 700; color: #0F172A;">
                    Season Pts: <span style="color: #0F766E;">{chosen_p1.total_points:.1f}</span> 
                    &nbsp;|&nbsp; Proj: <span style="color: #0F766E;">{getattr(chosen_p1, 'projected_total_points', 0.0):.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #0F766E; border-radius: 8px; padding: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 11px; font-weight: 800; color: #0F766E; text-transform: uppercase;">Option 2</div>
                <div style="font-size: 18px; font-weight: 900; color: #0F172A; margin: 2px 0;">{chosen_p2.name}</div>
                <div style="font-size: 13px; color: #64748B;">{chosen_p2.position} • {p2_team} | {wx_map.get(p2_team, '☀️ 70°F')}</div>
                <div style="margin-top: 8px; font-size: 14px; font-weight: 700; color: #0F172A;">
                    Season Pts: <span style="color: #0F766E;">{chosen_p2.total_points:.1f}</span> 
                    &nbsp;|&nbsp; Proj: <span style="color: #0F766E;">{getattr(chosen_p2, 'projected_total_points', 0.0):.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

        # 2. AI Recommendation Generation
        with st.spinner(f"Analyzing match-up dynamics and weather conditions for {chosen_p1.name} vs {chosen_p2.name}..."):
            try:
                p1_wx = wx_map.get(p1_team, "Outdoor / Fair")
                p2_wx = wx_map.get(p2_team, "Outdoor / Fair")

                # Full team lookup for unmistakable AI grounding
                team_names = {
                    "PIT": "Pittsburgh Steelers", "SEA": "Seattle Seahawks",
                    "CHI": "Chicago Bears", "GB": "Green Bay Packers",
                    "KC": "Kansas City Chiefs", "BUF": "Buffalo Bills",
                    "PHI": "Philadelphia Eagles", "DAL": "Dallas Cowboys",
                    "SF": "San Francisco 49ers", "DET": "Detroit Lions",
                    "MIA": "Miami Dolphins", "NYJ": "New York Jets",
                    "BAL": "Baltimore Ravens", "CIN": "Cincinnati Bengals",
                    "HOU": "Houston Texans", "IND": "Indianapolis Colts",
                    "JAX": "Jacksonville Jaguars", "TEN": "Tennessee Titans",
                    "DEN": "Denver Broncos", "LAC": "Los Angeles Chargers",
                    "LV": "Las Vegas Raiders", "WAS": "Washington Commanders",
                    "NYG": "New York Giants", "MIN": "Minnesota Vikings",
                    "ATL": "Atlanta Falcons", "CAR": "Carolina Panthers",
                    "NO": "New Orleans Saints", "TB": "Tampa Bay Buccaneers",
                    "ARI": "Arizona Cardinals", "LAR": "Los Angeles Rams",
                    "NE": "New England Patriots", "CLE": "Cleveland Browns"
                }

                p1_full_team = team_names.get(p1_team, p1_team)
                p2_full_team = team_names.get(p2_team, p2_team)

                prompt = f"""
                You are an institutional fantasy football analyst for the active NFL season.
                
                CRITICAL ROSTER CONSTRAINTS:
                - Treat player team assignments strictly as provided below. Do NOT use former teams or outdated prior-season affiliations.
                - Candidate 1 plays for the {p1_full_team} ({p1_team}).
                - Candidate 2 plays for the {p2_full_team} ({p2_team}).
                
                MATCHUP CONTEXT:
                Dilemma Type: {debate_mode}
                
                Candidate 1: {chosen_p1.name}
                - Position: {chosen_p1.position}
                - Current NFL Franchise: {p1_full_team} ({p1_team})
                - Total Season Fantasy Points: {chosen_p1.total_points}
                - Projected Points: {getattr(chosen_p1, 'projected_total_points', 0.0):.1f}
                - Venue & Weather: {p1_wx}
                
                Candidate 2: {chosen_p2.name}
                - Position: {chosen_p2.position}
                - Current NFL Franchise: {p2_full_team} ({p2_team})
                - Total Season Fantasy Points: {chosen_p2.total_points}
                - Projected Points: {getattr(chosen_p2, 'projected_total_points', 0.0):.1f}
                - Venue & Weather: {p2_wx}
                
                Provide a structured, sharp evaluation:
                1. **Definitive Start Recommendation**: Name the winner clearly.
                2. **Ceiling vs. Floor Analysis**: Contrast their risk profiles within their respective current offensive systems.
                3. **Weather & Environmental Factor**: How the venue/weather affects the game script.
                Keep it punchy, quantitative, and formatted with clean markdown bullet points.
                """
                
                # Model generation call
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=prompt
                )
                
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1.5px solid #E2E8F0; border-left: 4px solid #0F766E; border-radius: 6px; padding: 16px; margin-top: 12px; color: #0F172A;">
                    {response.text}
                </div>
                """, unsafe_allow_html=True)

            except Exception as ex:
                st.error(f"AI Debater Service Unavailable: {ex}")
# =========================================================
# PAGE 3: TRADE EVALUATOR
# =========================================================
elif active_page == "Trade Evaluator":
    st.markdown("<div class='section-title'>Trade Desk Evaluator</div>", unsafe_allow_html=True)
    st.markdown("<div class='meta-caption'>Multi-Player Equity & Depth Chart Impact</div>", unsafe_allow_html=True)

    opponent_options = [team.team_name for team in league.teams if team.team_name != my_team.team_name]
    opponent_team_name = st.selectbox("Trading Partner", opponent_options)
    opponent_team = team_options[opponent_team_name]

    col_trade_a, col_trade_b = st.columns(2)
    with col_trade_a:
        your_trade_pieces = st.multiselect(
            f"{my_team.team_name} Sends",
            options=[p.name for p in my_team.roster]
        )
    with col_trade_b:
        opp_trade_pieces = st.multiselect(
            f"{opponent_team.team_name} Sends",
            options=[p.name for p in opponent_team.roster]
        )

    @st.cache_data(show_spinner=False)
    def evaluate_trade(my_team_name, opp_team_name, send_names, recv_names, my_roster_summary, opp_roster_summary):
        client = genai.Client(api_key=API_KEY)
        prompt = f"""
        Evaluate this proposed fantasy football trade:
        TEAM A (Sending): {my_team_name} | Pieces: {send_names} | Squad: {my_roster_summary}
        TEAM B (Sending): {opp_team_name} | Pieces: {recv_names} | Squad: {opp_roster_summary}

        Verdict Rules:
        - Seems Fair: Balanced value swap.
        - Everybody Wins: Fixes positional drought cleanly on both sides.
        - Getting Fleeced: Unbalanced overpay.
        - Slightly Off: Minor edge to one side.
        - Collusion Warning: Destructive imbalance.
        """

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TradeEvaluation,
            )
        )
        return response.text

    if st.button("Evaluate Trade Equity"):
        if not your_trade_pieces or not opp_trade_pieces:
            st.warning("Select at least one player from each roster to proceed.")
        else:
            with st.spinner("Calculating depth chart impact and equity index..."):
                my_roster_summary = [{"name": p.name, "pos": p.position, "pts": p.total_points} for p in my_team.roster]
                opp_roster_summary = [{"name": p.name, "pos": p.position, "pts": p.total_points} for p in opponent_team.roster]

                trade_json = evaluate_trade(
                    my_team.team_name, opponent_team.team_name,
                    your_trade_pieces, opp_trade_pieces,
                    my_roster_summary, opp_roster_summary
                )
                trade_res = TradeEvaluation.model_validate_json(trade_json)

            verdict_style = SLEEPER_VERDICTS.get(
                trade_res.verdict, 
                {"bg": "#F1F5F9", "text": "#0F172A", "border": "#94A3B8"}
            )

            st.markdown(f"""
            <div style="display: flex; gap: 12px; align-items: center; margin: 14px 0;">
                <div style="
                    background: {verdict_style['bg']};
                    color: {verdict_style['text']};
                    border: 1.5px solid {verdict_style['border']};
                    padding: 6px 14px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 800;
                    letter-spacing: 0.4px;
                    text-transform: uppercase;
                ">
                    {trade_res.verdict}
                </div>
                <div style="font-size: 14px; color: #1E293B; font-weight: 700;">
                    Fairness Index: {trade_res.fairness_score}/100
                </div>
            </div>
            <div class='callout-box' style='color: #0F172A;'><b>Bottom Line:</b> {trade_res.bottom_line}</div>
            """, unsafe_allow_html=True)

            eval_col1, eval_col2 = st.columns(2)
            with eval_col1:
                st.markdown(f"""
                <div class='sleeper-card'>
                    <div style="font-size: 12px; font-weight: 800; color: #1E40AF; text-transform: uppercase; margin-bottom: 6px;">{my_team.team_name} Impact</div>
                    <div style="font-size: 14px; color: #1E293B; line-height: 1.55;">{trade_res.your_team_impact}</div>
                </div>
                """, unsafe_allow_html=True)

            with eval_col2:
                st.markdown(f"""
                <div class='sleeper-card'>
                    <div style="font-size: 12px; font-weight: 800; color: #1E40AF; text-transform: uppercase; margin-bottom: 6px;">{opponent_team.team_name} Impact</div>
                    <div style="font-size: 14px; color: #1E293B; line-height: 1.55;">{trade_res.opponent_team_impact}</div>
                </div>
                """, unsafe_allow_html=True)

            if trade_res.risk_factors:
                st.markdown("<div class='section-title' style='margin-top: 14px;'>Identified Variables</div>", unsafe_allow_html=True)
                for risk in trade_res.risk_factors:
                    st.markdown(f"<div style='font-size: 14px; color: #334155; margin-bottom: 6px;'>• {risk}</div>", unsafe_allow_html=True)

# =========================================================
# PAGE 4: POSITIONAL ECONOMY & LEAGUE MARKET
# =========================================================
elif active_page == "Positional Economy":
    st.markdown("<div class='section-title'>League Market Economics</div>", unsafe_allow_html=True)
    st.markdown("<div class='meta-caption'>Asset Allocation, Efficiency, Market Velocity & Scarcity</div>", unsafe_allow_html=True)

    # 4 Dedicated Tabs
    tab_alloc, tab_efficiency, tab_liquidity, tab_scarcity = st.tabs([
        "Asset Allocation", 
        "Capital Productivity", 
        "Waiver Liquidity",
        "VORP Scarcity Curves"
    ])

    # ---------------------------------------------------------
    # TAB 1: ASSET ALLOCATION (POSITION HOARDING)
    # ---------------------------------------------------------
    with tab_alloc:
        st.markdown("<div class='meta-caption'>Positional Roster Share Per Franchise</div>", unsafe_allow_html=True)
        
        alloc_data = []
        for t in league.teams:
            pos_counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "K": 0, "D/ST": 0}
            for p in t.roster:
                pos = p.position if p.position in pos_counts else "WR"
                pos_counts[pos] += 1
            
            for pos, count in pos_counts.items():
                alloc_data.append({
                    "Team": t.team_name,
                    "Position": pos,
                    "Count": count
                })

        df_alloc = pd.DataFrame(alloc_data)

        import plotly.express as px
        fig_alloc = px.bar(
            df_alloc,
            x="Count",
            y="Team",
            color="Position",
            orientation="h",
            color_discrete_map={
                "QB": "#E11D48",
                "RB": "#0F766E",
                "WR": "#2563EB",
                "TE": "#D97706",
                "K": "#64748B",
                "D/ST": "#475569"
            }
        )
        fig_alloc.update_layout(
            barmode="stack",
            height=450,
            margin=dict(l=10, r=10, t=25, b=10),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Total Rostered Players"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: CAPITAL PRODUCTIVITY (STARTERS VS BENCH)
    # ---------------------------------------------------------
    with tab_efficiency:
        st.markdown("<div class='meta-caption'>Points Extracted: Starters vs. Stranded Bench Capital</div>", unsafe_allow_html=True)

        eff_rows = []
        for t in league.teams:
            starter_pts = sum(getattr(p, "total_points", 0) for p in t.roster if getattr(p, "lineupSlot", "BE") != "BE")
            bench_pts = sum(getattr(p, "total_points", 0) for p in t.roster if getattr(p, "lineupSlot", "BE") == "BE")
            total_pts = starter_pts + bench_pts
            eff_rate = (starter_pts / total_pts * 100) if total_pts > 0 else 0

            eff_rows.append({
                "Team": t.team_name,
                "Starter Pts": round(starter_pts, 1),
                "Bench Pts": round(bench_pts, 1),
                "Efficiency %": round(eff_rate, 1),
                "Wins": t.wins
            })

        df_eff = pd.DataFrame(eff_rows)

        fig_eff = px.scatter(
            df_eff,
            x="Bench Pts",
            y="Starter Pts",
            size="Wins",
            color="Efficiency %",
            text="Team",
            color_continuous_scale=["#CBD5E1", "#0F766E"]
        )
        fig_eff.update_traces(textposition='top center')
        fig_eff.update_layout(
            height=450,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Stranded Bench Points"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Active Starting Points")
        )
        st.plotly_chart(fig_eff, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: WAIVER LIQUIDITY & ACQUISITION VELOCITY
    # ---------------------------------------------------------
    with tab_liquidity:
        st.markdown("<div class='meta-caption'>Market Aggression: Moves Made vs. Offensive Output</div>", unsafe_allow_html=True)

        liq_rows = []
        for t in league.teams:
            moves = getattr(t, "acquisitions", 0)
            trades = getattr(t, "trades", 0)
            faab_spent = getattr(t, "faab_spent", 0)
            liq_rows.append({
                "Team": t.team_name,
                "Acquisitions": moves,
                "Trades": trades,
                "Total Moves": moves + trades,
                "FAAB Spent": faab_spent,
                "Points For": round(t.points_for, 1),
                "Wins": t.wins
            })

        df_liq = pd.DataFrame(liq_rows)

        # Bubble size reflects Wins, color maps to Total Moves
        fig_liq = px.scatter(
            df_liq,
            x="Acquisitions",
            y="Points For",
            size="Wins",
            color="Total Moves",
            text="Team",
            color_continuous_scale=["#94A3B8", "#0F766E"],
            hover_data=["Trades", "FAAB Spent", "Wins"]
        )
        fig_liq.update_traces(textposition="top center")
        fig_liq.update_layout(
            height=450,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Waiver Claims / Roster Adds"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Total Points For (PF)")
        )
        st.plotly_chart(fig_liq, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 4: VORP SCARCITY CURVES
    # ---------------------------------------------------------
    with tab_scarcity:
        st.markdown("<div class='meta-caption'>Positional Output Cliffs (Ranked 1-24)</div>", unsafe_allow_html=True)

        all_players = []
        for t in league.teams:
            for p in t.roster:
                if p.position in ["QB", "RB", "WR", "TE"]:
                    all_players.append({"Player": p.name, "Pos": p.position, "Pts": p.total_points})

        df_players = pd.DataFrame(all_players)
        
        ranked_frames = []
        for pos in ["RB", "WR", "QB", "TE"]:
            sub = df_players[df_players["Pos"] == pos].sort_values("Pts", ascending=False).reset_index(drop=True)
            sub["Position Rank"] = sub.index + 1
            ranked_frames.append(sub.head(24))

        if ranked_frames:
            df_vorp = pd.concat(ranked_frames)

            fig_vorp = px.line(
                df_vorp,
                x="Position Rank",
                y="Pts",
                color="Pos",
                line_shape="spline",
                color_discrete_map={
                    "QB": "#E11D48",
                    "RB": "#0F766E",
                    "WR": "#2563EB",
                    "TE": "#D97706"
                }
            )
            fig_vorp.update_layout(
                height=420,
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Position Rank (Top 24)"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Total Points Scored")
            )
            st.plotly_chart(fig_vorp, use_container_width=True)
