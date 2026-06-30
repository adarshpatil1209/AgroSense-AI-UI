"""Page 4 — Irrigation Advisory"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import mock_data as md


def _popup(row: pd.Series) -> str:
    col = md.deficit_color(row['Deficit_mm'])
    return f"""
<div style="background:#0A0F0A;border:1px solid #E67E22;border-radius:4px;
            padding:11px 13px;font-family:'Courier New',monospace;
            color:#2ECC40;min-width:230px;max-width:270px;">
  <div style="font-size:13px;font-weight:bold;color:#E67E22;
              border-bottom:1px solid #1A4A1A;padding-bottom:7px;margin-bottom:9px;">
    &#128167; &nbsp;{row['Field_ID']}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:11px;">
    <tr><td style="color:#82E0AA;padding:2px 0;">CROP</td>
        <td style="color:#2ECC40;">{row['Crop']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">STAGE</td>
        <td style="color:#2ECC40;">{row['Stage']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">DEFICIT</td>
        <td style="color:{col};font-weight:bold;">{row['Deficit_mm']} mm</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">STRESS</td>
        <td style="color:#2ECC40;">{row['Stress']}</td></tr>
  </table>
</div>"""


def _build_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(
        location=[md.CENTER_LAT, md.CENTER_LON],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        attr="CartoDB",
    )
    for _, row in df.iterrows():
        fill = md.deficit_color(row['Deficit_mm'])
        folium.Rectangle(
            bounds=[[row['Lat1'], row['Lon1']], [row['Lat2'], row['Lon2']]],
            color='#2a2a2a',
            weight=1,
            fill_color=fill,
            fill_opacity=0.85,
            tooltip=folium.Tooltip(
                f"<span style='font-family:Courier New;color:{fill};'>"
                f"{row['Field_ID']} — {row['Deficit_mm']} mm deficit</span>"),
            popup=folium.Popup(_popup(row), max_width=280),
        ).add_to(m)
    return m


def render(df: pd.DataFrame):
    col_map, col_panel = st.columns([3, 1], gap="small")

    with col_map:
        st.markdown('<div class="sec-title">💧 WATER DEFICIT MAP — 8-DAY FAO-56 MODEL</div>',
                    unsafe_allow_html=True)
        m = _build_map(df)
        st_folium(m, width="100%", height=390, returned_objects=[])

        # FAO-56 Calculation Chain
        st.markdown('<div class="sec-title">📐 FAO-56 CALCULATION CHAIN</div>',
                    unsafe_allow_html=True)
        fao    = md.FAO56
        cols   = st.columns(5)
        items  = [
            ("ET&#8320;",        f"{fao['ET0']} mm/d",      "Reference ET (P-M)"),
            ("Kc",               f"{fao['Kc']}",             "Paddy (Reproductive)"),
            ("ETc",              f"{fao['ETc']} mm/d",      "Crop Evapotranspiration"),
            ("Rain+Storage",     f"{fao['RainStorage']} mm/d","Effective supply"),
            ("Deficit",          f"{fao['Deficit8d']} mm",   "8-day water gap"),
        ]
        for col, (label, val, sub) in zip(cols, items):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        # SMS Advisory
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("📱  Generate Farmer SMS Advisory", key="sms_btn"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div class="sms-box">
                  <div style="font-size:11px;font-weight:bold;color:#5CDB5C;
                              border-bottom:1px solid #1A4A1A;padding-bottom:5px;margin-bottom:7px;">
                    &#127468;&#127463; ENGLISH ADVISORY
                  </div>
                  AgroSense Advisory | Field F0304 | 18-Sep-2024<br>
                  Crop: Paddy | Stage: Reproductive<br>
                  Stress: <strong style="color:#E67E22;">MODERATE</strong>
                  (SAR VH/VV = 0.68)<br>
                  &#8594; Apply ~21 mm irrigation within 8 days.<br>
                  Best time: 6–8 AM. Avoid midday.
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div class="sms-box">
                  <div style="font-size:11px;font-weight:bold;color:#5CDB5C;
                              border-bottom:1px solid #1A4A1A;padding-bottom:5px;margin-bottom:7px;">
                    &#127470;&#127475; हिन्दी परामर्श
                  </div>
                  एग्रोसेंस परामर्श | खेत F0304 | 18 सितं. 2024<br>
                  फसल: धान | अवस्था: प्रजनन अवस्था<br>
                  तनाव: <strong style="color:#E67E22;">मध्यम</strong>
                  (SAR VH/VV = 0.68)<br>
                  &#8594; 8 दिनों में ~21 mm सिंचाई करें।<br>
                  सर्वोत्तम समय: प्रातः 6–8 बजे।
                </div>""", unsafe_allow_html=True)

    with col_panel:
        st.markdown('<div class="sec-title">🌡 DEFICIT SCALE</div>', unsafe_allow_html=True)
        scale_items = [
            ('#FFFDE7', '0–10 mm',  'Adequate — no action'),
            ('#FFB300', '11–20 mm', 'Monitor closely'),
            ('#E65100', '21–35 mm', 'Irrigate soon'),
            ('#B71C1C', '36–45 mm', 'URGENT irrigation'),
        ]
        for color, rng, action in scale_items:
            st.markdown(f"""
            <div class="dark-card" style="padding:8px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="display:inline-block;width:14px;height:14px;
                                 background:{color};border-radius:2px;flex-shrink:0;"></span>
                    <div>
                        <div style="font-size:11px;color:#2ECC40;">{rng}</div>
                        <div style="font-size:9px;color:#82E0AA;">{action}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:9px;color:#3A6A3A;margin-top:12px;
                    border-top:1px solid #1A4A1A;padding-top:8px;line-height:1.7;">
            FAO-56 Penman-Monteith<br>Kharif 2024 Season<br>
            Jayakwadi Command Area
        </div>""", unsafe_allow_html=True)
