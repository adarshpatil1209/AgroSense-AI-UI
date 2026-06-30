"""
AgroSense AI — Main Streamlit Entry Point
Run: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="AgroSense AI | Satellite Crop Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
# Inline CSS — no file read required (avoids Windows encoding issues)

GLOBAL_CSS = """
<style>
/* ── Hide native Streamlit page nav ───────────────────────────── */
[data-testid="stSidebarNav"]            { display: none !important; }
[data-testid="stToolbar"]              { display: none !important; }
[data-testid="stDecoration"]           { display: none !important; }
[data-testid="stStatusWidget"]         { display: none !important; }
footer                                 { display: none !important; }
#MainMenu                              { display: none !important; }

/* ── Base palette ─────────────────────────────────────────────── */
html, body                             { background-color: #0A0F0A !important; }
.stApp                                 { background-color: #0A0F0A !important; }
[data-testid="stSidebar"]              { background: #0D1F0D !important;
                                         border-right: 1px solid #1A4A1A !important; }
[data-testid="stSidebar"] *            { color: #82E0AA !important; }

/* ── Global font: Courier New terminal feel ───────────────────── */
*, *::before, *::after {
    font-family: 'Courier New', Courier, monospace !important;
}

/* ── Main content area ────────────────────────────────────────── */
.block-container { background: #0A0F0A !important;
                   padding-top: 0.8rem !important; }

/* ── Radio buttons (sidebar nav) ─────────────────────────────── */
.stRadio > div { gap: 2px !important; }
.stRadio > div > label {
    background: #0D1F0D !important;
    border: 1px solid #1A4A1A !important;
    border-radius: 3px !important;
    color: #82E0AA !important;
    font-size: 12px !important;
    padding: 5px 10px !important;
    margin: 1px 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: border-color 0.15s, color 0.15s;
}
.stRadio > div > label:hover {
    border-color: #2ECC40 !important;
    color: #2ECC40 !important;
}

/* ── Selectbox ────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: #0D1F0D !important;
    border: 1px solid #1A4A1A !important;
    color: #2ECC40 !important;
    font-family: 'Courier New', monospace !important;
}
.stSelectbox label { color: #82E0AA !important; font-size: 11px !important; }

/* ── Date input ───────────────────────────────────────────────── */
[data-testid="stDateInput"] input {
    background: #0D1F0D !important;
    border: 1px solid #1A4A1A !important;
    color: #2ECC40 !important;
}
[data-testid="stDateInput"] label { color: #82E0AA !important; font-size: 11px !important; }

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton > button {
    background: #0D1F0D !important;
    border: 1px solid #2ECC40 !important;
    color: #2ECC40 !important;
    font-family: 'Courier New', monospace !important;
    border-radius: 3px !important;
    transition: background 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    background: #1A4A1A !important;
    box-shadow: 0 0 8px rgba(46,204,64,0.3) !important;
}

/* ── Download button ──────────────────────────────────────────── */
.stDownloadButton > button {
    background: #0D1F0D !important;
    border: 1px solid #2ECC40 !important;
    color: #2ECC40 !important;
    font-family: 'Courier New', monospace !important;
    border-radius: 3px !important;
}
.stDownloadButton > button:hover { background: #1A4A1A !important; }

/* ── Metric cards ─────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #0D1F0D !important;
    border: 1px solid #1A4A1A !important;
    border-top: 3px solid #2ECC40 !important;
    border-radius: 4px !important;
    padding: 10px 12px !important;
}
[data-testid="metric-container"] label { color: #82E0AA !important; font-size: 11px !important; }
[data-testid="stMetricValue"]          { color: #2ECC40  !important; }

/* ── DataFrame ────────────────────────────────────────────────── */
[data-testid="stDataFrame"]            { background: #0D1F0D !important; }
.stDataFrame                           { background: #0D1F0D !important; }

/* ── Scrollbars ───────────────────────────────────────────────── */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0A0F0A; }
::-webkit-scrollbar-thumb { background: #1A4A1A; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2ECC40; }

/* ── Animations ───────────────────────────────────────────────── */
@keyframes pulse-dot {
    0%   { box-shadow: 0 0 0 0   rgba(46,204,64,0.8); }
    70%  { box-shadow: 0 0 0 7px rgba(46,204,64,0);   }
    100% { box-shadow: 0 0 0 0   rgba(46,204,64,0);   }
}
@keyframes blink {
    0%, 100% { opacity: 1;   }
    50%       { opacity: 0.3; }
}
.radar-dot {
    display: inline-block;
    width: 10px; height: 10px;
    background: #2ECC40;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
    vertical-align: middle;
    margin-right: 6px;
}
.live-badge {
    background: #0A1F0A;
    border: 1px solid #2ECC40;
    color: #2ECC40;
    padding: 2px 9px;
    border-radius: 3px;
    font-size: 11px;
    animation: blink 1.8s infinite;
}

/* ── Reusable component classes ───────────────────────────────── */
.g-header {
    background: #0D1F0D;
    border: 1px solid #2ECC40;
    border-radius: 4px;
    padding: 7px 14px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.g-footer {
    border-top: 1px solid #1A4A1A;
    margin-top: 24px;
    padding-top: 10px;
    text-align: center;
    font-style: italic;
    color: #3A6A3A !important;
    font-size: 11px;
}
.dark-card {
    background: #0D1F0D;
    border: 1px solid #1A4A1A;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 6px;
}
.kpi-card {
    background: #0D1F0D;
    border: 1px solid #1A4A1A;
    border-top: 3px solid #2ECC40;
    border-radius: 4px;
    padding: 14px 10px;
    text-align: center;
}
.kpi-value { font-size: 21px; font-weight: bold; color: #2ECC40; }
.kpi-label { font-size: 10px; color: #82E0AA; margin-top: 4px; letter-spacing: 0.04em; }
.kpi-sub   { font-size: 9px;  color: #3A6A3A; margin-top: 2px; }
.sec-title {
    font-size: 12px;
    font-weight: bold;
    color: #5CDB5C;
    border-left: 3px solid #2ECC40;
    padding-left: 7px;
    margin: 14px 0 8px;
    letter-spacing: 0.05em;
}
.swatch {
    display: inline-block;
    width: 13px; height: 13px;
    border-radius: 2px;
    vertical-align: middle;
    margin-right: 6px;
}
.pgsif-callout {
    background: #0A1F0A;
    border: 1px solid #2ECC40;
    border-left: 4px solid #2ECC40;
    border-radius: 4px;
    padding: 12px 16px;
    margin-top: 10px;
    font-size: 12px;
    color: #82E0AA;
    line-height: 1.65;
}
.sms-box {
    background: #0A1F0A;
    border: 1px solid #2ECC40;
    border-radius: 4px;
    padding: 12px;
    font-size: 11px;
    color: #82E0AA;
    line-height: 1.7;
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
import mock_data as md

@st.cache_data
def _load():
    return md.generate_fields()

fields_df = _load()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 14px;border-bottom:1px solid #1A4A1A;margin-bottom:10px;">
        <div style="font-size:28px;">🛰️</div>
        <div style="font-size:16px;font-weight:bold;color:#5CDB5C;letter-spacing:3px;margin-top:4px;">
            AGROSENSE AI
        </div>
        <div style="font-size:9px;color:#3A6A3A;margin-top:2px;letter-spacing:1px;">
            SATELLITE CROP INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("NAVIGATE", [
        "1 · Crop Map",
        "2 · Phenology Stage",
        "3 · Stress Map (PGSIF)",
        "4 · Irrigation Advisory",
        "5 · Time-Series Inspector",
        "6 · Accuracy & Validation",
        "7 · Export",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1A4A1A;margin:10px 0;'>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:10px;color:#82E0AA;margin-bottom:3px;'>📍 COMMAND AREA</div>",
                unsafe_allow_html=True)
    command_area = st.selectbox("_ca", [
        "Jayakwadi (Godavari Basin), Maharashtra",
        "Bhima Basin, Solapur",
        "Nira Valley, Pune",
    ], label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;color:#82E0AA;margin:8px 0 3px;'>📅 DATE WINDOW (8-day)</div>",
                unsafe_allow_html=True)
    from datetime import date, timedelta
    _default_start = date(2024, 9, 18)
    date_range = st.date_input("_dr",
        value=(_default_start, _default_start + timedelta(days=7)),
        min_value=date(2024, 1, 1),
        max_value=date(2025, 3, 31),
        label_visibility="collapsed",
    )

    # Safely extract date range
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        d_start, d_end = date_range
    elif isinstance(date_range, date):
        d_start = d_end = date_range
    else:
        d_start = d_end = _default_start

    st.markdown(f"""
    <div style="margin-top:12px;font-size:9px;color:#3A6A3A;border-top:1px solid #1A4A1A;padding-top:8px;line-height:1.7;">
        FIELDS &nbsp;: {len(fields_df)}<br>
        AREA &nbsp;&nbsp;&nbsp;: {fields_df['Area_ha'].sum():.0f} ha<br>
        SEASON &nbsp;: Kharif 2024<br>
        CLASSFR : RF+SVM Fusion<br>
        RESOLTN : 10 m
    </div>
    """, unsafe_allow_html=True)

# ─── GLOBAL HEADER ───────────────────────────────────────────────────────────
PAGE_NAMES = {
    "1 · Crop Map":              "CROP TYPE MAP",
    "2 · Phenology Stage":       "PHENOLOGY STAGE",
    "3 · Stress Map (PGSIF)":    "STRESS MAP — PGSIF",
    "4 · Irrigation Advisory":   "IRRIGATION ADVISORY",
    "5 · Time-Series Inspector": "TIME-SERIES INSPECTOR",
    "6 · Accuracy & Validation": "ACCURACY & VALIDATION",
    "7 · Export":                "EXPORT",
}
pname    = PAGE_NAMES.get(page, "")
date_str = f"{d_start.strftime('%d %b %Y')} → {d_end.strftime('%d %b %Y')}"

st.markdown(f"""
<div class="g-header">
    <div style="display:flex;align-items:center;gap:8px;">
        <span class="radar-dot"></span>
        <span style="color:#5CDB5C;font-size:16px;font-weight:bold;">AgroSense AI</span>
        <span style="color:#1A4A1A;font-size:18px;font-weight:300;">|</span>
        <span style="color:#2ECC40;font-size:14px;">{pname}</span>
    </div>
    <div style="display:flex;align-items:center;gap:16px;font-size:11px;color:#82E0AA;">
        <span>📍 {command_area}</span>
        <span>📅 {date_str}</span>
        <span class="live-badge">● LIVE DEMO MODE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── PAGE ROUTING ────────────────────────────────────────────────────────────
if   page == "1 · Crop Map":
    from pages.pg1_crop_map  import render; render(fields_df)
elif page == "2 · Phenology Stage":
    from pages.pg2_phenology import render; render(fields_df)
elif page == "3 · Stress Map (PGSIF)":
    from pages.pg3_stress    import render; render(fields_df)
elif page == "4 · Irrigation Advisory":
    from pages.pg4_irrigation import render; render(fields_df)
elif page == "5 · Time-Series Inspector":
    from pages.pg5_timeseries import render; render(fields_df)
elif page == "6 · Accuracy & Validation":
    from pages.pg6_accuracy  import render; render()
elif page == "7 · Export":
    from pages.pg7_export    import render; render(fields_df)

# ─── GLOBAL FOOTER ───────────────────────────────────────────────────────────
st.markdown("""
<div class="g-footer">
⚠️ Demo dashboard with illustrative data — full version runs on live Sentinel-1/2, LISS-III/AWiFS,
and EOS-04 feeds via Google Earth Engine. | AgroSense AI v1.0
</div>
""", unsafe_allow_html=True)
