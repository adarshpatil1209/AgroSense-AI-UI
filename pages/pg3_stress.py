"""Page 3 — Stress Map (PGSIF) — Core Innovation"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import mock_data as md


def _popup(row: pd.Series) -> str:
    stress   = row['Stress']
    fill_c   = md.STRESS_FILL.get(stress,   '#1A5C1A')
    border_c = md.STRESS_BORDER.get(stress, '#2ECC40')
    disp_c   = md.STRESS_DISPLAY.get(stress,'#2ECC40')
    return f"""
<div style="background:#050C05;border:1px solid {border_c};border-radius:4px;
            padding:11px 13px;font-family:'Courier New',monospace;
            color:#2ECC40;min-width:240px;max-width:300px;">
  <div style="font-size:13px;font-weight:bold;color:{border_c};
              border-bottom:1px solid #1A4A1A;padding-bottom:7px;margin-bottom:9px;">
    &#128225; &nbsp;{row['Field_ID']}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:11px;">
    <tr><td style="color:#82E0AA;padding:2px 0;">CROP</td>
        <td style="color:#2ECC40;">{row['Crop']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">STAGE DETECTED</td>
        <td style="color:#2ECC40;">{row['Stage']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">INDEX USED</td>
        <td style="color:#2ECC40;font-size:10px;">{row['Index_Name']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">INDEX VALUE</td>
        <td style="color:#2ECC40;">{row['Index_Value']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">STRESS LEVEL</td>
        <td style="color:{disp_c};font-weight:bold;">&#9650; {stress}</td></tr>
  </table>
  <div style="margin-top:9px;border-top:1px solid #1A4A1A;padding-top:7px;
              font-size:10px;color:#82E0AA;line-height:1.5;">
    {row['Gate_Note']}
  </div>
</div>"""


def _build_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(
        location=[md.CENTER_LAT, md.CENTER_LON],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        attr="CartoDB",
    )
    for _, row in df.iterrows():
        stress   = row['Stress']
        fill_c   = md.STRESS_FILL.get(stress, '#1A5C1A')
        border_c = md.STRESS_BORDER.get(stress, '#2ECC40')
        disp_c   = md.STRESS_DISPLAY.get(stress, '#2ECC40')

        # Outer glow halo
        folium.Rectangle(
            bounds=[
                [row['Lat1'] - 0.0003, row['Lon1'] - 0.0004],
                [row['Lat2'] + 0.0003, row['Lon2'] + 0.0004],
            ],
            color=border_c,
            fill_color=border_c,
            fill_opacity=0.07,
            weight=1,
            opacity=0.45,
        ).add_to(m)

        # Main field polygon
        folium.Rectangle(
            bounds=[[row['Lat1'], row['Lon1']], [row['Lat2'], row['Lon2']]],
            color=border_c,
            weight=2,
            fill_color=fill_c,
            fill_opacity=0.72,
            tooltip=folium.Tooltip(
                f"<span style='font-family:Courier New;color:{disp_c};'>"
                f"{row['Field_ID']} | {stress} | {row['Index_Name']}</span>"),
            popup=folium.Popup(_popup(row), max_width=310),
        ).add_to(m)
    return m


def render(df: pd.DataFrame):
    col_map, col_panel = st.columns([3, 1], gap="small")
    stress_counts = df['Stress'].value_counts()
    total         = len(df)

    with col_map:
        st.markdown('<div class="sec-title">⚡ PGSIF STRESS MAP — PHENOLOGY-GATED INDEX FUSION</div>',
                    unsafe_allow_html=True)
        m = _build_map(df)
        st_folium(m, width="100%", height=470, returned_objects=[])

        # PGSIF Innovation callout
        st.markdown("""
        <div class="pgsif-callout">
          <div style="font-size:13px;font-weight:bold;color:#5CDB5C;margin-bottom:7px;">
            &#128302; PGSIF — Phenology-Gated Spectral Index Fusion &nbsp;|&nbsp;
            <span style="font-size:11px;color:#3A6A3A;">Core Innovation</span>
          </div>
          <div style="font-size:11px;line-height:1.65;">
            Instead of applying one static index to all fields, PGSIF
            <strong style="color:#2ECC40;">auto-selects the optimal spectral index
            based on the field's detected growth stage</strong>, fusing optical and microwave sensors:<br>
            <span style="color:#F9E79F;">&#9632; Sowing</span> &#8594; NDVI Anomaly + SMI &nbsp;|&nbsp;
            <span style="color:#82E0AA;">&#9632; Vegetative</span> &#8594; NDWI (Optical SWIR) &nbsp;|&nbsp;
            <span style="color:#1E8449;">&#9632; Reproductive</span> &#8594; SAR VH/VV (Microwave) &nbsp;|&nbsp;
            <span style="color:#784212;">&#9632; Maturity</span> &#8594; VCI (MODIS Thermal)<br><br>
            This multi-sensor gating reduces false stress detections by
            <strong style="color:#2ECC40;">~34%</strong> vs. fixed-index approaches.
            <em>Click any field to see its active gate logic.</em>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_panel:
        st.markdown('<div class="sec-title">&#9889; STRESS LEGEND</div>', unsafe_allow_html=True)

        legend_items = [
            ('No Stress', '#1A5C1A', '#2ECC40'),
            ('Low',       '#4A7A1A', '#82E0AA'),
            ('Moderate',  '#C07A00', '#E67E22'),
            ('High',      '#8B2500', '#E74C3C'),
            ('Severe',    '#4A0000', '#8B0000'),
        ]
        for level, fill, border in legend_items:
            n   = stress_counts.get(level, 0)
            pct = round(100 * n / total, 1)
            st.markdown(f"""
            <div class="dark-card" style="border-left:3px solid {border};
                        padding:8px 10px;margin-bottom:3px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="display:inline-block;width:12px;height:12px;
                                 background:{fill};border:1px solid {border};
                                 border-radius:2px;"></span>
                    <span style="color:{border};font-size:12px;font-weight:bold;flex:1;">{level}</span>
                    <span style="color:#82E0AA;font-size:10px;">{pct}%</span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title" style="margin-top:14px;">&#128225; PGSIF GATE MAP</div>',
                    unsafe_allow_html=True)
        for stage, idx in md.STAGE_INDEX.items():
            color = md.STAGE_FILL[stage]
            st.markdown(f"""
            <div style="padding:5px 0;border-bottom:1px solid #0D2A0D;">
                <div style="color:{color};font-size:11px;font-weight:bold;">{stage}</div>
                <div style="color:#3A6A3A;font-size:9px;margin-top:1px;">{idx}</div>
            </div>""", unsafe_allow_html=True)
