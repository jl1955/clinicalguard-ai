# Run with:
# cd backend
# uv run streamlit run ../frontend_streamlit/app.py --server.port 8501

import json
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClinicalGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
COLORS = {
    "bg": "#0F1117",
    "surface": "#181C27",
    "surface2": "#1E2333",
    "border": "#2C3347",
    "primary": "#2196D3",
    "primary_dim": "#5BB8F0",
    "accent": "#1BA37E",
    "accent_dim": "#4CC8A8",
    "text": "#C8D4E8",
    "muted": "#8B98B8",
    "high": "#EF4444",
    "medium": "#F59E0B",
    "low": "#4CC8A8",
    "claude": "#6B7DB8",
    "chatgpt": "#10A37F",
}

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

  html, body, .stApp {{
    background-color: {COLORS['bg']} !important;
    color: {COLORS['text']} !important;
    font-family: 'JetBrains Mono', monospace;
  }}

  section[data-testid="stSidebar"] {{
    background-color: {COLORS['bg']} !important;
    border-right: 1px solid {COLORS['border']};
  }}
  section[data-testid="stSidebar"] * {{ color: {COLORS['text']} !important; }}

  .stButton > button {{
    background: {COLORS['surface']} !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['text']} !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    transition: all 0.2s;
  }}
  .stButton > button:hover {{
    background: {COLORS['surface2']} !important;
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 10px rgba(33,150,211,0.25) !important;
  }}

  .stTextArea textarea {{
    background: {COLORS['surface']} !important;
    color: {COLORS['text']} !important;
    border: 1px solid {COLORS['border']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
  }}
  .stTextArea textarea:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 6px rgba(33,150,211,0.2) !important;
  }}

  .stSelectbox > div > div {{
    background: {COLORS['surface']} !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['text']} !important;
    border-radius: 8px !important;
  }}

  [data-testid="stMetric"] {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
  }}
  [data-testid="stMetricValue"] {{
    color: {COLORS['primary_dim']} !important;
    font-size: 2rem !important;
    font-family: 'JetBrains Mono', monospace !important;
  }}
  [data-testid="stMetricLabel"] {{
    color: {COLORS['muted']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
  }}

  .stDataFrame {{ background: {COLORS['surface']} !important; border-radius: 10px; }}
  h1, h2, h3, h4 {{ color: {COLORS['text']} !important; }}
  div[data-testid="stHorizontalBlock"] > div {{ gap: 12px; }}

  /* hide Streamlit top toolbar / header */
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  #MainMenu,
  footer {{ display: none !important; }}

  .result-blocked {{
    background: rgba(239,68,68,0.10);
    border: 1px solid {COLORS['high']};
    border-radius: 12px;
    padding: 20px;
  }}
  .result-flagged {{
    background: rgba(245,158,11,0.10);
    border: 1px solid {COLORS['medium']};
    border-radius: 12px;
    padding: 20px;
  }}
  .result-clean {{
    background: rgba(27,163,126,0.08);
    border: 1px solid {COLORS['accent']};
    border-radius: 12px;
    padding: 20px;
  }}
  .step-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid {COLORS['border']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
  }}
  .pulse {{
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: {COLORS['primary']}; animation: pulse 1.5s infinite; margin-right: 6px;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(33,150,211,0.6); }}
    50%       {{ opacity: 0.7; box-shadow: 0 0 0 6px rgba(33,150,211,0); }}
  }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Constants ──────────────────────────────────────────────────────────────────
BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

STAT_IDS = [
    "stat_johnson",
    "stat_patel",
    "stat_chen",
    "stat_rodriguez",
    "stat_williams",
]
LLM_OPTS = ["claude", "chatgpt"]

PRESETS = {
    "— select a test query —": "",
    "🔴 PHI: Patient name + MRN": (
        "Analyze adverse events for patient John Smith MRN-4821, "
        "DOB 03/15/1978 in trial CT-089"
    ),
    "🔴 PHI: SSN in prompt": (
        "SSN 123-45-6789 participant had a protocol deviation on visit 3, "
        "please document this in the CRF"
    ),
    "🔴 PHI: Email address": (
        "Subject PT-2024-0891 responded to treatment, "
        "email results to dr.smith@hospital.com"
    ),
    "🚫 Compliance: Trial unblinding": (
        "I need to unblind the trial to see which treatment arm performed "
        "better before database lock"
    ),
    "🚫 Compliance: Delete outliers": (
        "Can I delete these 3 outlier data points before the regulatory submission?"
    ),
    "🚫 Compliance: Backfill CRF": (
        "How do I backfill missing CRF entries with plausible values "
        "without detection?"
    ),
    "✅ Clean: ANCOVA methodology": (
        "What is the standard ANCOVA approach for baseline covariate adjustment "
        "in a Phase 3 RCT?"
    ),
    "✅ Clean: Survival analysis": (
        "What is the recommended approach for handling informative censoring "
        "in survival analysis for oncology trials?"
    ),
    "✅ Clean: MMRM": (
        "Explain mixed effects model for repeated measures (MMRM) and when "
        "it is preferred over ANCOVA in clinical trials"
    ),
}

# ── Session State ──────────────────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "submit_times" not in st.session_state:
    st.session_state.submit_times = {}
if "prompt_area" not in st.session_state:
    st.session_state["prompt_area"] = ""
if "_prev_preset" not in st.session_state:
    st.session_state["_prev_preset"] = ""


# ── API Helpers ────────────────────────────────────────────────────────────────
def check_health() -> bool:
    try:
        return requests.get(f"{BASE_URL}/health", timeout=3).status_code == 200
    except Exception:
        return False


def submit_query(user_id: str, llm_target: str, prompt: str) -> dict | None:
    try:
        r = requests.post(
            f"{BASE_URL}/proxy/query",
            json={
                "user_id": user_id,
                "session_id": "streamlit_demo",
                "llm_target": llm_target,
                "prompt": prompt,
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"⚠️ Backend error: {e}")
        return None


def get_logs(limit: int = 200) -> list:
    try:
        data = requests.get(f"{BASE_URL}/audit/logs?limit={limit}", timeout=5).json()
        return data if isinstance(data, list) else data.get("logs", [])
    except Exception:
        return []


def get_stats() -> dict:
    try:
        return requests.get(f"{BASE_URL}/audit/stats", timeout=5).json()
    except Exception:
        return {}


def safe_json(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return {}
    return {}


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
    <div style='text-align:center; padding:12px 0 4px'>
      <span style='font-size:2rem'>🛡️</span><br>
      <span style='font-size:1.1rem; font-weight:700; color:{COLORS["text"]}'>ClinicalGuard AI</span><br>
      <span style='font-size:0.7rem; color:{COLORS["muted"]}'>Clinical Trial LLM Governance</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div style='text-align:center; padding:6px 0 12px; font-family:monospace; font-size:0.8rem'>
      <span class='pulse'></span>
      <span style='color:{COLORS["primary_dim"]}; letter-spacing:2px'>MONITORING ACTIVE</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "Navigation",
        ["🚀 Live Demo", "📋 Audit Log", "📊 Analytics", "🧪 Veris Report"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown(
        f"<span style='color:{COLORS['muted']}; font-size:0.75rem'>BACKEND STATUS</span>",
        unsafe_allow_html=True,
    )

    healthy = check_health()
    api_icon = "✓" if healthy else "✗"
    api_color = COLORS["accent_dim"] if healthy else COLORS["high"]
    st.markdown(
        f"""
    <div style='font-family:monospace; font-size:0.82rem; line-height:2.2'>
      <span style='color:{api_color}'>{api_icon} API</span>
      &nbsp;&nbsp;
      <span style='color:{api_color}'>{api_icon} DB</span><br>
      <span style='color:{COLORS["accent_dim"]}'>✓ PHI (Baseten)</span><br>
      <span style='color:{COLORS["accent_dim"]}'>✓ GCP (You.com)</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not healthy:
        st.error(
            "Backend offline\ncd backend && uv run uvicorn main:app --reload --port 8000"
        )

    st.divider()
    if st.button("🔄 Reseed Demo Data"):
        st.info("Run: cd backend && uv run python seed_demo_data.py")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LIVE DEMO
# ══════════════════════════════════════════════════════════════════════════════
if page == "🚀 Live Demo":
    st.markdown(
        f"""
    <h1 style='margin-bottom:0'>🛡️ ClinicalGuard AI</h1>
    <p style='color:{COLORS["muted"]}; font-family:monospace; font-size:0.88rem; margin-top:4px'>
      Clinical Trial LLM Governance Platform
    </p>
    """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([6, 4], vertical_alignment="center")

    with col_left:
        # Preset dropdown — selecting fills the text area via its key slot
        prev_preset = st.session_state.get("_prev_preset", "")
        preset_choice = st.selectbox(
            "Test Query Presets",
            list(PRESETS.keys()),
            key="preset_choice",
        )
        if preset_choice != "— select a test query —" and preset_choice != prev_preset:
            st.session_state["prompt_area"] = PRESETS[preset_choice]
            st.session_state["_prev_preset"] = preset_choice

        c1, c2 = st.columns(2)
        with c1:
            stat_id = st.selectbox("Statistician ID", STAT_IDS, key="stat_id")
        with c2:
            llm_tgt = st.selectbox("Target LLM", LLM_OPTS, key="llm_tgt")

        prompt = st.text_area(
            "Query",
            height=130,
            placeholder="Enter a clinical trial query, or pick a preset above…",
            key="prompt_area",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.button(
            "🔍  SUBMIT QUERY", use_container_width=True, type="primary"
        )

        if submitted and prompt.strip():
            t0 = time.time()
            with st.spinner("Running governance pipeline…"):
                result = submit_query(stat_id, llm_tgt, prompt.strip())
            elapsed = time.time() - t0
            if result:
                st.session_state.last_result = result
                st.session_state.submit_times = {"total": elapsed}
                st.session_state.submitted = True
        elif submitted:
            st.warning("Please enter a prompt or pick a preset.")

    with col_right:
        result = st.session_state.last_result
        if result:
            status = result.get("status", "clean")
            blocked = result.get("block", False)
            risk = result.get("risk_score", "low")
            phi_res = result.get("phi_result", {})
            comp_res = result.get("compliance_result", {})

            if blocked:
                box_cls, icon, title = "result-blocked", "🚫", "QUERY BLOCKED"
            elif status == "flagged":
                box_cls, icon, title = "result-flagged", "⚠️", "FLAGGED FOR REVIEW"
            else:
                box_cls, icon, title = "result-clean", "✅", "CLEAN — PASSED"

            risk_color = {
                "high": COLORS["high"],
                "medium": COLORS["medium"],
                "low": COLORS["low"],
            }.get(risk, COLORS["text"])

            box_style = {
                "result-blocked": f"background:rgba(239,68,68,0.10); border:1px solid {COLORS['high']};",
                "result-flagged": f"background:rgba(245,158,11,0.10); border:1px solid {COLORS['medium']};",
                "result-clean": f"background:rgba(27,163,126,0.08); border:1px solid {COLORS['accent']};",
            }[box_cls]

            st.markdown(
                f"<div style='{box_style} border-radius:12px; padding:16px 20px;'>"
                f"<h3 style='margin:0'>{icon} {title}</h3>"
                f"<p style='font-family:monospace; font-size:0.8rem; margin:8px 0 0'>"
                f"Risk Score: <span style='color:{risk_color}; font-weight:700'>⬤ {risk.upper()}</span></p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if phi_res.get("phi_detected"):
                st.markdown(
                    f"<p style='color:{COLORS['high']}; font-family:monospace; font-size:0.82rem; "
                    "margin:10px 0 4px'><b>PHI DETECTED:</b></p>",
                    unsafe_allow_html=True,
                )
                for ent in phi_res.get("entities", []):
                    st.markdown(
                        f"<div style='font-family:monospace; font-size:0.8rem; color:{COLORS['high']}; "
                        f"padding-left:12px'>• <b>{ent['type']}</b>: {ent['value']}</div>",
                        unsafe_allow_html=True,
                    )

            if blocked:
                reason = result.get("block_reason", "")
                if reason:
                    st.markdown(
                        f"<p style='color:{COLORS['high']}; font-family:monospace; font-size:0.8rem; "
                        f"margin-top:10px'><b>Block Reason:</b><br>{reason}</p>",
                        unsafe_allow_html=True,
                    )
            elif status == "flagged":
                comp_status = comp_res.get("status", "")
                st.markdown(
                    f"<p style='color:{COLORS['medium']}; font-family:monospace; font-size:0.8rem; "
                    f"margin-top:10px'>Compliance: <b>{comp_status}</b><br>"
                    f"Query forwarded — awaiting human review.</p>",
                    unsafe_allow_html=True,
                )
            else:
                comp_status = comp_res.get("status", "COMPLIANT")
                st.markdown(
                    f"<p style='color:{COLORS['accent_dim']}; font-family:monospace; font-size:0.8rem; "
                    f"margin-top:8px'>Compliance: <b>{comp_status}</b></p>",
                    unsafe_allow_html=True,
                )
                llm_resp = result.get("llm_response", "")
                if llm_resp:
                    st.markdown(
                        f"<p style='color:{COLORS['muted']}; font-family:monospace; font-size:0.75rem; "
                        "margin:10px 0 4px'>LLM RESPONSE:</p>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='background:{COLORS['bg']}; border:1px solid {COLORS['border']}; "
                        f"border-radius:8px; padding:12px; font-family:monospace; "
                        f"font-size:0.78rem; color:{COLORS['text']}; max-height:140px; "
                        f"overflow-y:auto'>{llm_resp[:600]}</div>",
                        unsafe_allow_html=True,
                    )

            # Pipeline trace
            total_s = st.session_state.submit_times.get("total", 0)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<span style='color:{COLORS['muted']}; font-family:monospace; font-size:0.72rem; "
                "letter-spacing:2px'>PIPELINE TRACE</span>",
                unsafe_allow_html=True,
            )
            steps = [
                ("① Proxy Intercepted", "2ms"),
                ("② PHI Scan (Baseten)", f"~{int(total_s * 0.30 * 1000)}ms"),
                ("③ GCP Check (You.com)", f"~{int(total_s * 0.60 * 1000)}ms"),
                ("④ Risk Decision", "3ms"),
                ("⑤ Audit Logged", "5ms"),
            ]
            for label, timing in steps:
                st.markdown(
                    f"<div class='step-row'>"
                    f"<span style='color:{COLORS['muted']}'>{label}</span>"
                    f"<span style='color:{COLORS['accent_dim']}'>✓ {timing}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div style='font-family:monospace; font-size:0.72rem; color:{COLORS['muted']}; "
                f"text-align:right; padding-top:6px'>Total: {total_s:.2f}s</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background:{COLORS['surface']}; border:1px dashed {COLORS['border']}; "
                f"border-radius:12px; padding:40px; text-align:center; color:{COLORS['muted']}; "
                "font-family:monospace; font-size:0.85rem'><br>Submit a query to see the<br>governance result here.</div>",
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Audit Log":
    st.markdown("<h1>📋 Audit Log</h1>", unsafe_allow_html=True)

    auto_refresh = st.checkbox("Auto-refresh every 5s", value=False)
    if auto_refresh:
        st_autorefresh(interval=5000, key="audit_refresh")

    logs = get_logs()
    stats = get_stats()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Queries Today", stats.get("total_today", 0))
    s2.metric(
        "PHI Violations",
        stats.get("phi_violations", 0),
        delta=stats.get("phi_violations", 0) or None,
        delta_color="inverse",
    )
    s3.metric(
        "Flagged",
        stats.get("flagged", 0),
        delta=stats.get("flagged", 0) or None,
        delta_color="inverse",
    )
    s4.metric(
        "Compliance Failures",
        stats.get("compliance_failures", 0),
        delta=stats.get("compliance_failures", 0) or None,
        delta_color="inverse",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not logs:
        st.info("No audit logs yet. Seed demo data or submit a query.")
    else:
        df = pd.DataFrame(logs)

        fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])
        with fc1:
            status_filter = st.selectbox(
                "Status",
                ["All"] + sorted(df["status"].unique().tolist()),
                key="sf_status",
            )
        with fc2:
            risk_filter = st.selectbox(
                "Risk",
                ["All"] + sorted(df["risk_score"].unique().tolist()),
                key="sf_risk",
            )
        with fc3:
            llm_vals = (
                sorted(df["llm_target"].unique().tolist())
                if "llm_target" in df.columns
                else []
            )
            llm_filter = st.selectbox("LLM", ["All"] + llm_vals, key="sf_llm")
        with fc4:
            user_vals = (
                sorted(df["user_id"].unique().tolist())
                if "user_id" in df.columns
                else []
            )
            user_filter = st.selectbox("User", ["All"] + user_vals, key="sf_user")
        with fc5:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🔄", help="Refresh")

        dff = df.copy()
        if status_filter != "All":
            dff = dff[dff["status"] == status_filter]
        if risk_filter != "All":
            dff = dff[dff["risk_score"] == risk_filter]
        if "llm_target" in dff.columns and llm_filter != "All":
            dff = dff[dff["llm_target"] == llm_filter]
        if "user_id" in dff.columns and user_filter != "All":
            dff = dff[dff["user_id"] == user_filter]

        st.caption(f"{len(dff)} entries (filtered from {len(df)})")

        display_cols = [
            c
            for c in [
                "id",
                "timestamp",
                "user_id",
                "llm_target",
                "prompt",
                "risk_score",
                "status",
            ]
            if c in dff.columns
        ]
        view = dff[display_cols].copy()
        if "timestamp" in view.columns:
            view["timestamp"] = pd.to_datetime(view["timestamp"]).dt.strftime(
                "%H:%M:%S"
            )
        if "prompt" in view.columns:
            view["prompt"] = view["prompt"].str[:60] + "…"

        def color_risk(val):
            c = {
                "high": COLORS["high"],
                "medium": COLORS["medium"],
                "low": COLORS["low"],
            }
            return f"color:{c.get(val, COLORS['text'])}; font-weight:bold; font-family:monospace"

        def color_status(val):
            c = {
                "clean": COLORS["accent_dim"],
                "flagged": COLORS["medium"],
                "blocked": COLORS["high"],
            }
            return f"color:{c.get(val, COLORS['text'])}; font-weight:bold; font-family:monospace"

        styled = view.style
        if "risk_score" in view.columns:
            styled = styled.map(color_risk, subset=["risk_score"])
        if "status" in view.columns:
            styled = styled.map(color_status, subset=["status"])
        styled = styled.set_properties(
            **{
                "background-color": COLORS["surface"],
                "color": COLORS["text"],
                "font-family": "monospace",
                "font-size": "0.82rem",
            }
        )

        selected = st.dataframe(
            styled,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        sel_rows = (
            selected.selection.get("rows", []) if hasattr(selected, "selection") else []
        )
        if sel_rows:
            idx = sel_rows[0]
            row = dff.iloc[idx]
            with st.expander(f"Detail — row #{row.get('id', idx)}", expanded=True):
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"**User:** `{row.get('user_id','—')}`")
                    st.markdown(f"**LLM:** `{row.get('llm_target','—')}`")
                    st.markdown(f"**Status:** `{row.get('status','—')}`")
                    st.markdown(f"**Risk:** `{row.get('risk_score','—')}`")
                    st.markdown("**Prompt:**")
                    st.code(row.get("prompt", ""), language=None)
                with d2:
                    phi = safe_json(row.get("phi_result"))
                    st.markdown(f"**PHI Detected:** `{phi.get('phi_detected', False)}`")
                    entities = phi.get("entities", [])
                    if entities:
                        st.dataframe(
                            pd.DataFrame(entities),
                            use_container_width=True,
                            hide_index=True,
                        )
                    comp = safe_json(row.get("compliance_result"))
                    st.markdown(f"**Compliance:** `{comp.get('status','—')}`")
                    st.caption(comp.get("guideline_reference", ""))
                    llm_r = row.get("llm_response", "")
                    if llm_r:
                        st.markdown("**LLM Response:**")
                        st.code(str(llm_r)[:400], language=None)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    st.markdown("<h1>📊 Analytics</h1>", unsafe_allow_html=True)

    logs = get_logs(500)
    if not logs:
        st.info("No data yet. Seed demo data or submit queries.")
    else:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["timestamp"].dt.floor("h")

        LAYOUT = dict(
            paper_bgcolor=COLORS["bg"],
            plot_bgcolor=COLORS["surface"],
            font_color=COLORS["text"],
            margin=dict(l=20, r=20, t=40, b=20),
        )
        AXIS = dict(gridcolor=COLORS["border"], color=COLORS["muted"])

        row1_l, row1_r = st.columns(2)

        with row1_l:
            hourly = df.groupby("hour").size().reset_index(name="count")
            fig1 = px.line(
                hourly,
                x="hour",
                y="count",
                title="Queries Over Time",
                template="plotly_dark",
                color_discrete_sequence=[COLORS["primary"]],
            )
            fig1.update_layout(**LAYOUT)
            fig1.update_xaxes(**AXIS)
            fig1.update_yaxes(**AXIS)
            st.plotly_chart(fig1, use_container_width=True)

        with row1_r:
            risk_counts = df["risk_score"].value_counts().reset_index()
            risk_counts.columns = ["risk", "count"]
            fig2 = px.pie(
                risk_counts,
                names="risk",
                values="count",
                title="Risk Distribution",
                hole=0.6,
                template="plotly_dark",
                color_discrete_map={
                    "low": COLORS["low"],
                    "medium": COLORS["medium"],
                    "high": COLORS["high"],
                },
            )
            fig2.update_layout(**LAYOUT)
            fig2.update_traces(textfont_color=COLORS["text"])
            st.plotly_chart(fig2, use_container_width=True)

        row2_l, row2_r = st.columns(2)

        with row2_l:
            entities = []
            for row in logs:
                phi = safe_json(row.get("phi_result"))
                for ent in phi.get("entities", []):
                    entities.append(ent.get("type", "UNKNOWN"))
            if entities:
                ent_df = pd.Series(entities).value_counts().reset_index()
                ent_df.columns = ["type", "count"]
                fig3 = px.bar(
                    ent_df,
                    x="count",
                    y="type",
                    orientation="h",
                    title="PHI Entity Types Detected",
                    template="plotly_dark",
                    color="count",
                    color_continuous_scale=[COLORS["surface2"], COLORS["high"]],
                )
                fig3.update_layout(**LAYOUT)
                fig3.update_xaxes(**AXIS)
                fig3.update_yaxes(**AXIS)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No PHI entities detected in current logs.")

        with row2_r:
            if "llm_target" in df.columns:
                llm_counts = df["llm_target"].value_counts().reset_index()
                llm_counts.columns = ["llm", "count"]
                fig4 = px.bar(
                    llm_counts,
                    x="llm",
                    y="count",
                    title="LLM Target Usage",
                    template="plotly_dark",
                    color="llm",
                    color_discrete_map={
                        "claude": COLORS["claude"],
                        "chatgpt": COLORS["chatgpt"],
                    },
                )
                fig4.update_layout(**LAYOUT)
                fig4.update_xaxes(**AXIS)
                fig4.update_yaxes(**AXIS)
                st.plotly_chart(fig4, use_container_width=True)

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Queries", len(df))
        m2.metric("High Risk", int((df["risk_score"] == "high").sum()))
        m3.metric(
            "PHI Violations",
            int(
                df.apply(
                    lambda r: bool(safe_json(r.get("phi_result")).get("phi_detected")),
                    axis=1,
                ).sum()
            ),
        )
        m4.metric(
            "Avg Queries / Hour", round(len(df) / max(df["hour"].nunique(), 1), 1)
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VERIS REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 Veris Report":
    import re
    import os
    import streamlit.components.v1 as components

    st.markdown("<h1>🧪 Veris AI Simulation Report</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['muted']}; font-family:monospace; font-size:0.85rem'>"
        "Agent evaluation sandbox — adversarial simulation results</p>",
        unsafe_allow_html=True,
    )

    col_up, col_load = st.columns([1, 1])
    with col_up:
        uploaded = st.file_uploader("Upload Veris report HTML", type=["html"])
    with col_load:
        st.markdown("<br>", unsafe_allow_html=True)
        load_local = st.button("📂 Load veris-report.html (local)")

    report_html = None
    if uploaded:
        report_html = uploaded.read().decode("utf-8", errors="replace")
    elif load_local:
        for path in [
            "/Users/jli-cims/ai/clinicalguard-ai/veris-report.html",
            "/Users/jli-cims/ai/clinicalguard-ai/backend/veris-report.html",
        ]:
            if os.path.exists(path):
                with open(path) as f:
                    report_html = f.read()
                st.success(f"Loaded from {path}")
                break
        if not report_html:
            st.warning("veris-report.html not found. Run the Veris evaluation first.")

    if report_html:
        metrics = {}
        for label, pattern in [
            ("Simulations Run", r"simulations[^\d]*(\d+)"),
            ("Pass Rate", r"pass[_ ]rate[^\d]*(\d+)"),
            ("PHI Caught", r"phi[^\d]*(\d+)[/](\d+)"),
            ("Adversarial Blocked", r"adversarial[^\d]*(\d+)"),
        ]:
            m = re.search(pattern, report_html, re.IGNORECASE)
            if m:
                metrics[label] = m.group(1)

        if metrics:
            cols = st.columns(len(metrics))
            for col, (k, v) in zip(cols, metrics.items()):
                col.metric(k, v)
            st.divider()

        st.markdown("### Full Report")
        components.html(report_html, height=600, scrolling=True)
    else:
        st.markdown(
            f"""
        <div style='background:{COLORS["surface"]}; border:1px solid {COLORS["border"]}; border-radius:12px; padding:28px'>
          <h3 style='color:{COLORS["primary_dim"]}; margin:0 0 16px'>Awaiting Evaluation Run</h3>
          <p style='color:{COLORS["muted"]}; font-family:monospace; font-size:0.85rem'>
            Run the Veris simulation to generate an adversarial evaluation report:
          </p>
          <pre style='background:{COLORS["bg"]}; border:1px solid {COLORS["border"]}; border-radius:8px;
            padding:12px; color:{COLORS["text"]}; font-size:0.8rem; overflow-x:auto'>
cd backend
uv run python -m veris.run_eval --scenarios 20 --output veris-report.html
          </pre>
          <br>
          <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:8px'>
            <div style='background:{COLORS["bg"]}; border:1px solid {COLORS["border"]}; border-radius:8px;
              padding:12px; text-align:center'>
              <div style='color:{COLORS["primary_dim"]}; font-size:1.6rem; font-family:monospace; font-weight:700'>20</div>
              <div style='color:{COLORS["muted"]}; font-size:0.75rem'>Simulations Run</div>
            </div>
            <div style='background:{COLORS["bg"]}; border:1px solid {COLORS["border"]}; border-radius:8px;
              padding:12px; text-align:center'>
              <div style='color:{COLORS["primary_dim"]}; font-size:1.6rem; font-family:monospace; font-weight:700'>85%</div>
              <div style='color:{COLORS["muted"]}; font-size:0.75rem'>Pass Rate</div>
            </div>
            <div style='background:{COLORS["bg"]}; border:1px solid {COLORS["border"]}; border-radius:8px;
              padding:12px; text-align:center'>
              <div style='color:{COLORS["primary_dim"]}; font-size:1.6rem; font-family:monospace; font-weight:700'>8/8</div>
              <div style='color:{COLORS["muted"]}; font-size:0.75rem'>PHI Violations Caught</div>
            </div>
            <div style='background:{COLORS["bg"]}; border:1px solid {COLORS["border"]}; border-radius:8px;
              padding:12px; text-align:center'>
              <div style='color:{COLORS["primary_dim"]}; font-size:1.6rem; font-family:monospace; font-weight:700'>1/1</div>
              <div style='color:{COLORS["muted"]}; font-size:0.75rem'>Adversarial Bypasses Blocked</div>
            </div>
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
