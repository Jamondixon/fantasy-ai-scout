import streamlit as st
import pandas as pd
import plotly.express as px
from espn_api.football import League
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal

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

    /* Subdued divider lines */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
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
# 4. SIDEBAR NAVIGATION
# =========================================================
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

# --- Module A: Squad & Wire Grids (Scrollable with Sticky Styled Headers) ---
roster_rows = [
    {"Slot": getattr(p, "lineupSlot", "BE"), "Player": p.name, "Pos": p.position, "Total Pts": round(p.total_points, 1)}
    for p in my_team.roster
]
fa_rows = [
    {"Player": p.name, "Pos": p.position, "Total Pts": round(p.total_points, 1)}
    for p in free_agents
]

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
            {"SLOT": getattr(p, "lineupSlot", "BE"), "PLAYER": p.name, "POS": p.position, "TOTAL PTS": f"{p.total_points:.1f}"}
            for p in my_team.roster
        ])
        st.markdown(
            f'<div class="table-scroll-container">{df_roster.to_html(classes="sleeper-table", index=False)}</div>',
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
            {"PLAYER": p.name, "POS": p.position, "TOTAL PTS": f"{p.total_points:.1f}"}
            for p in free_agents
        ])
        st.markdown(
            f'<div class="table-scroll-container">{df_fa.to_html(classes="sleeper-table", index=False)}</div>',
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
    standings_rows = []
    sorted_teams = sorted(league.teams, key=lambda t: (getattr(t, 'standing', 99), -t.wins, -t.points_for))

    for rank, t in enumerate(sorted_teams, start=1):
        standings_rows.append({
            "RANK": rank,
            "TEAM": t.team_name,
            "MANAGER": getattr(t, "owner", "Unknown"),
            "W-L": f"{t.wins}-{t.losses}" + (f"-{t.ties}" if getattr(t, 'ties', 0) > 0 else ""),
            "PF": f"{t.points_for:.1f}",
            "PA": f"{t.points_against:.1f}",
            "STREAK": f"{getattr(t, 'streak_type', '')} {getattr(t, 'streak_length', '')}"
        })

    df_standings = pd.DataFrame(standings_rows)
    st.markdown(
        f'<div class="table-scroll-container">{df_standings.to_html(classes="sleeper-table", index=False)}</div>',
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
# PAGE 2: START / SIT DEBATER
# =========================================================
elif active_page == "Start/Sit Debater":
    st.markdown("<div class='section-title'>Head-to-Head Decision Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='meta-caption'>Live Practice & Injury Grounded Analysis</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    roster_names = [p.name for p in my_team.roster]
    fa_names = [p.name for p in free_agents]

    with col_a:
        player_a_name = st.selectbox("Club Option", roster_names)
    with col_b:
        player_b_name = st.selectbox("Wire Alternative", fa_names)

    player_a_obj = next(p for p in my_team.roster if p.name == player_a_name)
    player_b_obj = next(p for p in free_agents if p.name == player_b_name)

    if st.button(f"Analyze Matchup: {player_a_name} vs. {player_b_name}"):
        with st.spinner("Scraping practice reports and injury feeds..."):
            client = genai.Client(api_key=API_KEY)

            prompt = f"""
            Head-to-head fantasy football debate between:
            1. {player_a_name} ({player_a_obj.position}, {player_a_obj.total_points} total pts)
            2. {player_b_name} ({player_b_obj.position}, {player_b_obj.total_points} total pts)

            Instructions:
            - Search for latest 2026 practice participation, injury alerts, and news.
            - Compare touch volume, red-zone share, and defensive matchup.
            - Provide a decisive final call with confidence rating.
            - Tone: High-density, professional sports journalism. Zero robotic filler.
            """

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )

        st.markdown(f"""
        <div class='sleeper-card' style='margin-top: 16px; color: #0F172A; font-size: 14.5px;'>
            {response.text}
        </div>
        """, unsafe_allow_html=True)

        grounding_metadata = response.candidates[0].grounding_metadata
        if grounding_metadata and grounding_metadata.grounding_chunks:
            with st.expander("Verified Beat Sources & Wire Reports"):
                for chunk in grounding_metadata.grounding_chunks:
                    if chunk.web:
                        st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")

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
