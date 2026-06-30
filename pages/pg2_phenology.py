"""Page 2 — Phenology Stage Map"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
import mock_data as md

_DARK = dict(
    paper_bgcolor='#0A0F0A', plot_bgcolor='#0D1F0D',
    font=dict(color='#2ECC40', family='Courier New'),
)

_STAGE_INDEX_BRIEF = {
    'Sowing':       'NDVI Anomaly + SMI',
    'Vegetative':   'NDWI (S2 B8/B11)',
    'Reproductive': 'SAR VH/VV (S1 GRD)',
    'Maturity':     'VCI (MODIS 250m)',
}


def _popup(row: pd.Series) -> str:
    fill = md.STAGE_FILL[row['Stage']]
    return f"""
<div style="background:#0A0F0A;border:1px solid {fill};border-radius:4px;
            padding:11px 13px;font-family:'Courier New',monospace;
            color:#2ECC40;min-width:230px;max-width:280px;">
  <div style="font-size:13px;font-weight:bold;color:{fill};
              border-bottom:1px solid #1A4A1A;padding-bottom:7px;margin-bottom:9px;">
    &#128225; &nbsp;{row['Field_ID']}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:11px;">
    <tr><td style="color:#82E0AA;padding:2px 0;">CROP</td>
        <td style="color:#2ECC40;">{row['Crop']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">STAGE</td>
        <td style="color:{fill};font-weight:bold;">{row['Stage']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">DAT</td>
        <td style="color:#2ECC40;">{row['DAT']} days</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">RANGE</td>
        <td style="color:#2ECC40;">{md.STAGE_DAT[row['Stage']]}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">INDEX</td>
        <td style="color:#2ECC40;">{_STAGE_INDEX_BRIEF[row['Stage']]}</td></tr>
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
        fill = md.STAGE_FILL[row['Stage']]
        folium.Rectangle(
            bounds=[[row['Lat1'], row['Lon1']], [row['Lat2'], row['Lon2']]],
            color=fill,
            weight=2,
            fill_color=fill,
            fill_opacity=0.65,
            tooltip=folium.Tooltip(
                f"<span style='font-family:Courier New;color:{fill};'>"
                f"{row['Field_ID']} | {row['Stage']}</span>"),
            popup=folium.Popup(_popup(row), max_width=290),
        ).add_to(m)
    return m


def render(df: pd.DataFrame):
    col_map, col_panel = st.columns([3, 1], gap="small")
    stage_counts = df['Stage'].value_counts()
    total        = len(df)

    with col_map:
        st.markdown('<div class="sec-title">📅 PHENOLOGY STAGE MAP — GROWTH STAGE DETECTION</div>',
                    unsafe_allow_html=True)
        m = _build_map(df)
        st_folium(m, width="100%", height=420, returned_objects=[])

        # Horizontal bar chart
        pcts   = [round(100 * stage_counts.get(s, 0) / total, 1) for s in md.STAGES]
        colors = [md.STAGE_FILL[s] for s in md.STAGES]
        fig = go.Figure(go.Bar(
            x=pcts, y=md.STAGES, orientation='h',
            marker_color=colors,
            text=[f"{p}%" for p in pcts],
            textposition='outside',
            textfont=dict(color='#2ECC40', family='Courier New', size=11),
        ))
        fig.update_layout(
            **_DARK,
            title=dict(text="Stage Distribution — % of Fields This Week",
                       font=dict(color='#5CDB5C', size=12, family='Courier New')),
            height=200,
            margin=dict(t=35, b=20, l=10, r=60),
            xaxis=dict(gridcolor='#1A4A1A', title='% of Fields', range=[0, 60]),
            yaxis=dict(gridcolor='#1A4A1A'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_panel:
        st.markdown('<div class="sec-title">📅 STAGE LEGEND</div>', unsafe_allow_html=True)
        for stage in md.STAGES:
            color  = md.STAGE_FILL[stage]
            n      = stage_counts.get(stage, 0)
            pct    = round(100 * n / total, 1)
            st.markdown(f"""
            <div class="dark-card" style="border-left:3px solid {color};padding:9px 10px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
                    <span style="display:inline-block;width:11px;height:11px;
                                 background:{color};border:1px solid {color};border-radius:2px;"></span>
                    <span style="color:{color};font-size:12px;font-weight:bold;flex:1;">{stage}</span>
                    <span style="color:#82E0AA;font-size:10px;">{pct}%</span>
                </div>
                <div style="font-size:10px;color:#82E0AA;">{md.STAGE_DAT[stage]}</div>
                <div style="font-size:9px;color:#3A6A3A;margin-top:2px;">
                    {_STAGE_INDEX_BRIEF[stage]}
                </div>
            </div>""", unsafe_allow_html=True)
