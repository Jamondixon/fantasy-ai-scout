# 🏈 Fantasy AI Scout

A high-performance, institutional-grade fantasy football analytics and decision-support dashboard powered by Streamlit, `espn-api`, Plotly, and Google Gemini. 

Fantasy AI Scout translates raw league data into actionable market intelligence—combining real-time roster tracking, AI-driven roster audits, predictive start/sit debates, and quantitative market economics.

---

## ⚡ Key Features

* **AI Roster Audit & Waiver Scout**: Automated roster analysis identifying positional bottlenecks and high-upside waiver wire pickups powered by Google Gemini.
* **Persistent League Modules**:
  * **Active Squad & Wire Depth Charts**: Collapsible, scrollable tables tracking current roster construction alongside top available free agents.
  * **Weekly Matchup Scoreboard**: Live and historic head-to-head weekly box scores with dynamic point margins across the entire league.
  * **Championship Standings**: Real-time division rankings, records, points for/against (PF/PA), and streak tracking with custom-styled, sticky headers.
* **Market Economics & Capital Allocation Dashboard**:
  * **Asset Allocation Index**: Interactive stacked visuals evaluating roster capital distribution and positional hoarding across all franchises.
  * **Capital Productivity**: Starter efficiency vs. stranded bench points scatter plot identifying under-optimized lineups.
  * **Waiver Liquidity & Velocity**: Transaction volume and market aggression mapped against total scoring output.
  * **VORP Scarcity Curves**: Value Over Replacement Level point decay cliffs (top 24 players by position).
* **High-Contrast Sleeper Aesthetic**: Deep teal (`#0F766E`) and slate design architecture featuring responsive Plotly visualizers and scrollable HTML tables.

---

## 🛠️ Tech Stack

* **Frontend/Framework**: [Streamlit](https://streamlit.io/)
* **Fantasy Data Engine**: [`espn-api`](https://github.com/cwendt94/espn-api)
* **Data Visualizations**: [Plotly Express](https://plotly.com/python/plotly-express/) & Pandas
* **AI & LLM Reasoning**: [Google GenAI SDK](https://github.com/googleapis/python-genai) (`gemini-2.5-flash`)
* **Styling**: Custom CSS (Responsive Flexbox, Glassmorphism card elevation, sticky table headers)

---

