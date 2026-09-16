import streamlit as st
import pandas as pd
from espn_api.football import League
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal

# 1. Page Configuration
st.set_page_config(page_title="Fantasy AI Scout", layout="wide")
st.title("🏈 ESPN Fantasy Football AI Scout")

# 2. ESPN & Gemini Credentials (Loaded from secrets)
LEAGUE_ID = int(st.secrets["LEAGUE_ID"])
YEAR = int(st.secrets["YEAR"])
SWID = st.secrets["SWID"]
ESPN_S2 = st.secrets["ESPN_S2"]
API_KEY = st.secrets["GEMINI_API_KEY"]

# 3. Cache and Load League Data
@st.cache_resource(ttl=600)
def load_espn_league():
    return League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

try:
    with st.spinner("Connecting to ESPN..."):
        league = load_espn_league()
        free_agents = league.free_agents(size=12)
except Exception as e:
    st.error(f"Failed to connect to ESPN: {e}")
    st.stop()

# 4. Sidebar Controls & Navigation
st.sidebar.header("⚙️ Team Settings")
team_options = {team.team_name: team for team in league.teams}
selected_team_name = st.sidebar.selectbox(
    "Select Your Team:",
    options=list(team_options.keys())
)
my_team = team_options[selected_team_name]
st.sidebar.success(f"Viewing: **{my_team.team_name}**")

st.sidebar.divider()
st.sidebar.header("🧭 Feature Navigation")
active_page = st.sidebar.radio(
    "Go to:",
    options=[
        "🤖 AI Waiver Scout",
        "⚔️ Start/Sit Debater",
        "🤝 Trade Evaluator",
        "📊 Positional Scarcity"
    ]
)

# --- 5. Persistent Header: Roster vs Free Agents (Mobile-Optimized) ---
roster_rows = [
    {"Player": p.name, "Pos": p.position, "Total Pts": p.total_points}
    for p in my_team.roster
]
fa_rows = [
    {"Player": p.name, "Pos": p.position, "Total Pts": p.total_points}
    for p in free_agents
]

with st.expander("📋 View Roster & Top Free Agents", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"**{my_team.team_name} Roster**")
        st.dataframe(pd.DataFrame(roster_rows), height=320, width="stretch", hide_index=True)

    with col2:
        st.caption("**Top Available Free Agents**")
        st.dataframe(pd.DataFrame(fa_rows), height=320, width="stretch", hide_index=True)

st.divider()

# --- SCHEMAS & STYLES ---
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

PILL_STYLES = {
    "Seems Fair": {"bg": "#143a1e", "text": "#6ee7b7", "border": "#059669", "icon": "⚖️"},
    "Everybody Wins": {"bg": "#0e3150", "text": "#93c5fd", "border": "#2563eb", "icon": "🤝"},
    "Slightly Off": {"bg": "#3e2704", "text": "#fcd34d", "border": "#d97706", "icon": "⚠️"},
    "Getting Fleeced": {"bg": "#38133b", "text": "#f0abfc", "border": "#c026d3", "icon": "💸"},
    "Collusion Warning": {"bg": "#450a0a", "text": "#fca5a5", "border": "#dc2626", "icon": "🚨"},
}

# =========================================================
# PAGE 1: AI WAIVER SCOUT
# =========================================================
if active_page == "🤖 AI Waiver Scout":
    st.subheader("🤖 AI Roster Evaluation & Waiver Targets")

    if st.button("Generate AI Scout Report", type="primary"):
        with st.spinner("Gemini is analyzing your squad and available waiver targets..."):
            client = genai.Client(api_key=API_KEY)
            prompt = f"""
            Analyze this Fantasy Football squad and suggest moves based on the available waiver wire pool.
            
            Team: {my_team.team_name}
            Roster: {roster_rows}
            
            Available Free Agents:
            {fa_rows}
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

        st.info(f"**Team Overview:** {report.team_summary}")
        st.warning(f"**Identified Weak Spot:** {report.weakest_position}")

        st.markdown("### 💡 Recommended Moves")
        for rec in report.recommendations:
            with st.container(border=True):
                st.markdown(f"**Drop:** `{rec.drop_player}` ➔ **Add:** `{rec.add_free_agent}`")
                st.progress(rec.upgrade_confidence / 100, text=f"Confidence: {rec.upgrade_confidence}%")
                st.write(rec.reasoning)

# =========================================================
# PAGE 2: HEAD-TO-HEAD DEBATER
# =========================================================
elif active_page == "⚔️ Start/Sit Debater":
    st.subheader("⚔️ Head-to-Head Debate (Live Grounded Search)")

    col_a, col_b = st.columns(2)
    roster_names = [p.name for p in my_team.roster]
    fa_names = [p.name for p in free_agents]

    with col_a:
        player_a_name = st.selectbox("Player A (From Your Roster):", roster_names)
    with col_b:
        player_b_name = st.selectbox("Player B (Free Agent Target):", fa_names)

    player_a_obj = next(p for p in my_team.roster if p.name == player_a_name)
    player_b_obj = next(p for p in free_agents if p.name == player_b_name)

    if st.button(f"Debate: {player_a_name} vs. {player_b_name}", type="secondary"):
        with st.spinner(f"Searching live news and analyzing {player_a_name} vs. {player_b_name}..."):
            client = genai.Client(api_key=API_KEY)

            prompt = f"""
            Conduct a live head-to-head fantasy football debate between:
            1. {player_a_name} ({player_a_obj.position}, {player_a_obj.total_points} total pts)
            2. {player_b_name} ({player_b_obj.position}, {player_b_obj.total_points} total pts)

            Instructions:
            - Search for the latest 2026 injury reports, practice participation status, and recent news for both players.
            - Compare their roles, target/touch share trends, and upcoming matchup favorability.
            - Conclude with a definitive **WINNER VERDICT** and confidence score (1-100%).
            - Format your response with clear markdown headings, bullet points, and bold text.
            """

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )

        st.markdown(response.text)

        grounding_metadata = response.candidates[0].grounding_metadata
        if grounding_metadata and grounding_metadata.grounding_chunks:
            with st.expander("🔍 Live News & Grounding Sources"):
                for chunk in grounding_metadata.grounding_chunks:
                    if chunk.web:
                        st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")

# =========================================================
# PAGE 3: TRADE EVALUATOR
# =========================================================
elif active_page == "🤝 Trade Evaluator":
    st.subheader("🤝 Multi-Team Trade Evaluator")

    opponent_options = [team.team_name for team in league.teams if team.team_name != my_team.team_name]
    opponent_team_name = st.selectbox("Select Opponent to Trade With:", opponent_options)
    opponent_team = team_options[opponent_team_name]

    col_trade_a, col_trade_b = st.columns(2)

    with col_trade_a:
        st.markdown(f"**Players You Send ({my_team.team_name}):**")
        your_trade_pieces = st.multiselect(
            "Choose players from your roster:",
            options=[p.name for p in my_team.roster],
            key="trade_send"
        )

    with col_trade_b:
        st.markdown(f"**Players You Receive ({opponent_team.team_name}):**")
        opp_trade_pieces = st.multiselect(
            "Choose players from opponent roster:",
            options=[p.name for p in opponent_team.roster],
            key="trade_recv"
        )

    @st.cache_data(show_spinner=False)
    def evaluate_trade(my_team_name, opp_team_name, send_names, recv_names, my_roster_summary, opp_roster_summary):
        client = genai.Client(api_key=API_KEY)

        prompt = f"""
        You are an expert Fantasy Football trade consultant. Evaluate this proposed trade:

        TEAM A (Giving): {my_team_name}
        Players Sent: {send_names}
        Full Roster Context: {my_roster_summary}

        TEAM B (Giving): {opp_team_name}
        Players Sent: {recv_names}
        Full Roster Context: {opp_roster_summary}

        Verdict Guidelines:
        - Seems Fair: Both sides swap balanced future/current value.
        - Everybody Wins: Addresses positional needs for both teams cleanly.
        - Getting Fleeced: One team drastically overpays for an elite asset.
        - Slightly Off: One team gets a slight edge, but still reasonable.
        - Collusion Warning: Severely lopsided trade damaging league integrity.

        Evaluate:
        1. Overall Fairness Score (1 to 100).
        2. How it helps or hurts Team A's positional depth.
        3. How it helps or hurts Team B's positional depth.
        4. Notable risk factors (injury history, schedule, target share).
        5. A concise bottom-line verdict.
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

    if st.button("Evaluate Trade Proposal", type="primary"):
        if not your_trade_pieces or not opp_trade_pieces:
            st.warning("Please select at least one player on each side of the trade.")
        else:
            with st.spinner("Analyzing roster depth, positional surplus, and trade balance..."):
                my_roster_summary = [{"name": p.name, "pos": p.position, "pts": p.total_points} for p in my_team.roster]
                opp_roster_summary = [{"name": p.name, "pos": p.position, "pts": p.total_points} for p in opponent_team.roster]

                trade_json = evaluate_trade(
                    my_team.team_name,
                    opponent_team.team_name,
                    your_trade_pieces,
                    opp_trade_pieces,
                    my_roster_summary,
                    opp_roster_summary
                )
                trade_res = TradeEvaluation.model_validate_json(trade_json)

            cfg = PILL_STYLES.get(
                trade_res.verdict, 
                {"bg": "#262626", "text": "#ffffff", "border": "#525252", "icon": "ℹ️"}
            )

            st.markdown(
                f"""
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 6px 16px;
                    border-radius: 9999px;
                    background-color: {cfg['bg']};
                    color: {cfg['text']};
                    border: 1.5px solid {cfg['border']};
                    font-weight: 700;
                    font-size: 1.05rem;
                    letter-spacing: 0.3px;
                    margin-top: 8px;
                    margin-bottom: 14px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
                ">
                    <span>{cfg['icon']}</span>
                    <span>{trade_res.verdict}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(trade_res.fairness_score / 100, text=f"Fairness Index: {trade_res.fairness_score}/100")
            st.info(f"**The Bottom Line:** {trade_res.bottom_line}")

            eval_col1, eval_col2 = st.columns(2)
            with eval_col1:
                with st.container(border=True):
                    st.markdown(f"**Impact on {my_team.team_name} (Your Team):**")
                    st.write(trade_res.your_team_impact)

            with eval_col2:
                with st.container(border=True):
                    st.markdown(f"**Impact on {opponent_team.team_name}:**")
                    st.write(trade_res.opponent_team_impact)

            if trade_res.risk_factors:
                st.markdown("#### ⚠️ Key Risk Factors to Consider")
                for risk in trade_res.risk_factors:
                    st.write(f"- {risk}")

# =========================================================
# PAGE 4: POSITIONAL SCARCITY
# =========================================================
elif active_page == "📊 Positional Scarcity":
    st.subheader("📊 League Positional Scarcity & Points Visualizer")

    all_player_data = []

    for team in league.teams:
        is_user_team = (team.team_name == my_team.team_name)
        for p in team.roster:
            all_player_data.append({
                "Player": p.name,
                "Position": p.position,
                "Total Points": p.total_points,
                "Team": team.team_name,
                "Category": "Your Team" if is_user_team else "Rival Rosters"
            })

    for p in free_agents:
        all_player_data.append({
            "Player": p.name,
            "Position": p.position,
            "Total Points": p.total_points,
            "Team": "Free Agency",
            "Category": "Waiver Pool"
        })

    df_all = pd.DataFrame(all_player_data)
    core_positions = ["QB", "RB", "WR", "TE", "K", "D/ST"]
    df_core = df_all[df_all["Position"].isin(core_positions)]

    tab_charts, tab_ai = st.tabs(["📈 Market Charts", "🧠 AI Scarcity Audit"])

    with tab_charts:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### 📌 Total Points Generated by Position")
            pts_by_pos = df_core.groupby(["Position", "Category"])["Total Points"].sum().unstack(fill_value=0)
            st.bar_chart(pts_by_pos, use_container_width=True)

        with col_chart2:
            st.markdown("##### 🎯 Average Point Production per Player")
            avg_by_pos = df_core.groupby(["Position", "Category"])["Total Points"].mean().unstack(fill_value=0).round(1)
            st.area_chart(avg_by_pos, use_container_width=True)

        st.markdown("##### 📋 Positional Point Distribution Breakdown")
        pos_summary = df_core.pivot_table(
            index="Position",
            columns="Category",
            values="Total Points",
            aggfunc=["count", "mean", "max"]
        ).round(1)
        st.dataframe(pos_summary, use_container_width=True)

    with tab_ai:
        st.markdown("##### Automated Roster Economy Diagnostic")
        st.caption("Let Gemini audit league-wide depth and highlight positional pinch points.")

        @st.cache_data(show_spinner=False)
        def run_scarcity_audit(summary_data, user_team_name):
            client = genai.Client(api_key=API_KEY)

            prompt = f"""
            You are a macro-level Fantasy Football quantitative analyst.
            Analyze this league positional data:
            
            {summary_data}
            
            Focus specifically on {user_team_name}'s competitive standing.
            Diagnose:
            1. Which positions have severe league droughts vs. deep waiver surplus.
            2. Actionable market inefficiencies {user_team_name} can exploit.
            """

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ScarcityReport,
                )
            )
            return response.text

        if st.button("Run Market Scarcity Audit", type="primary"):
            with st.spinner("Auditing league-wide points and waiver pool liquidity..."):
                summary_dict = df_core.groupby(["Position", "Category"])["Total Points"].describe().round(1).to_dict()
                report_json = run_scarcity_audit(str(summary_dict), my_team.team_name)
                report = ScarcityReport.model_validate_json(report_json)

            st.info(f"**Executive Takeaway:** {report.executive_summary}")
            st.warning(f"**Tightest Market Squeeze:** `{report.hardest_position_to_acquire}`")

            STATUS_BADGES = {
                "CRITICAL_DROUGHT": ":red-badge[🚨 CRITICAL DROUGHT]",
                "BALANCED": ":blue-badge[⚖️ BALANCED]",
                "SURPLUS_AVAILABLE": ":green-badge[🟢 SURPLUS AVAILABLE]"
            }

            for insight in report.insights:
                with st.container(border=True):
                    badge_tag = STATUS_BADGES.get(insight.status, f":gray-badge[{insight.status}]")
                    st.markdown(f"**{insight.position}** — {badge_tag}")
                    st.write(insight.advice)
