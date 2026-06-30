"""Page 1 — Crop Type Map"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import mock_data as md


def _popup(row: pd.Series) -> str:
    fill = md.CROP_FILL[row['Crop']]
    return f"""
<div style="background:#0A0F0A;border:1px solid {fill};border-radius:4px;
            padding:11px 13px;font-family:'Courier New',monospace;
            color:#2ECC40;min-width:220px;max-width:260px;">
  <div style="font-size:13px;font-weight:bold;color:#5CDB5C;
              border-bottom:1px solid #1A4A1A;padding-bottom:7px;margin-bottom:9px;">
    &#128225; &nbsp;{row['Field_ID']}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:11px;">
    <tr><td style="color:#82E0AA;padding:2px 0;">CROP TYPE</td>
        <td style="color:{fill};font-weight:bold;">{row['Crop']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">CONFIDENCE</td>
        <td style="color:#2ECC40;">{row['Confidence']}%</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">SOURCE</td>
        <td style="color:#2ECC40;">{row['Source']}</td></tr>
    <tr><td style="color:#82E0AA;padding:2px 0;">AREA</td>
        <td style="color:#2ECC40;">{row['Area_ha']} ha</td></tr>
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
        fill = md.CROP_FILL[row['Crop']]
        folium.Rectangle(
            bounds=[[row['Lat1'], row['Lon1']], [row['Lat2'], row['Lon2']]],
            color=fill,
            weight=2,
            fill_color=fill,
            fill_opacity=0.65,
            tooltip=folium.Tooltip(f"<span style='font-family:Courier New;color:{fill};'>{row['Field_ID']} | {row['Crop']}</span>"),
            popup=folium.Popup(_popup(row), max_width=270),
        ).add_to(m)
    return m


def render(df: pd.DataFrame):
    col_map, col_panel = st.columns([3, 1], gap="small")

    with col_map:
        st.markdown('<div class="sec-title">📡 FIELD MAP — CROP TYPE CLASSIFICATION</div>',
                    unsafe_allow_html=True)
        m = _build_map(df)
        st_folium(m, width="100%", height=520, returned_objects=[])

    with col_panel:
        # Legend card
        st.markdown('<div class="sec-title">&#127807; CROP LEGEND</div>', unsafe_allow_html=True)
        crop_counts = df['Crop'].value_counts()
        total       = len(df)
        for crop in md.CROPS:
            n   = crop_counts.get(crop, 0)
            pct = round(100 * n / total, 1)
            col = md.CROP_FILL[crop]
            st.markdown(f"""
            <div class="dark-card" style="display:flex;align-items:center;
                        gap:7px;padding:7px 10px;margin-bottom:4px;">
                <span class="swatch" style="background:{col};border:1px solid {col};"></span>
                <span style="color:#2ECC40;font-size:12px;flex:1;">{crop}</span>
                <span style="color:#82E0AA;font-size:11px;">{pct}%</span>
            </div>""", unsafe_allow_html=True)

        # Stats card
        st.markdown('<div class="sec-title" style="margin-top:16px;">&#128202; AREA STATS</div>',
                    unsafe_allow_html=True)
        total_ha  = df['Area_ha'].sum()
        irrig_ha  = df[df['Crop'] != 'Fallow']['Area_ha'].sum()
        stats = [
            ("Total Area",   f"{total_ha:.1f} ha"),
            ("Irrigated",    f"{irrig_ha:.1f} ha"),
            ("Season",       "Kharif 2024"),
            ("Classifier",   "RF+SVM Fusion"),
            ("Resolution",   "10 m"),
            ("Fields",       str(total)),
        ]
        for label, val in stats:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                        padding:4px 0;border-bottom:1px solid #0D2A0D;font-size:11px;">
                <span style="color:#82E0AA;">{label}</span>
                <span style="color:#2ECC40;">{val}</span>
            </div>""", unsafe_allow_html=True)
