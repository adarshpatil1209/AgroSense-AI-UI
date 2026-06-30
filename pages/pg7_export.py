"""Page 7 — Export"""

import streamlit as st
import pandas as pd
import mock_data as md


def _build_full_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Concatenate 12-month time-series for all 64 fields into one CSV."""
    all_rows = []
    for fid in df['Field_ID'].tolist():
        ts = md.generate_timeseries(fid)
        fi = df[df['Field_ID'] == fid].iloc[0]
        ts.insert(0, 'Field_ID', fid)
        ts['Crop']   = fi['Crop']
        ts['Stage']  = fi['Stage']
        ts['Stress'] = fi['Stress']
        ts['Source'] = fi['Source']
        all_rows.append(ts)
    return pd.concat(all_rows, ignore_index=True)


def render(df: pd.DataFrame):
    st.markdown("""
    <div style="font-size:12px;color:#82E0AA;margin-bottom:16px;line-height:1.65;">
        Export satellite-derived products from the current analysis session.<br>
        <span style="color:#3A6A3A;">
            GeoTIFF and PDF exports are placeholders in this demo — the full operational version
            generates live outputs from Google Earth Engine pipelines.
        </span>
    </div>""", unsafe_allow_html=True)

    # Build CSV once (cached implicitly by Python)
    full_ts   = _build_full_timeseries(df)
    csv_bytes = full_ts.to_csv(index=False).encode('utf-8')

    btn_cols = st.columns(4)
    export_items = [
        ("🗺️", "Crop Map", "GeoTIFF · 10 m", "Sentinel-2 classified output",
         "📥 Download Crop Map (GeoTIFF)", "dl_crop", False, None, None),
        ("⚡", "Stress Map", "GeoTIFF · PGSIF", "Multi-sensor fusion output",
         "📥 Download Stress Map (GeoTIFF)", "dl_stress", False, None, None),
        ("📄", "Advisory Report", "PDF · FAO-56", "Irrigation schedule",
         "📥 Download Advisory Report (PDF)", "dl_pdf", False, None, None),
        ("📊", "Time-Series", "CSV · 12 months", f"All {len(df)} fields",
         "📥 Download Time-Series (CSV)", "dl_csv", True, csv_bytes,
         "agrosense_timeseries_jayakwadi_kharif2024.csv"),
    ]

    for col, (icon, title, meta, desc, btn_label, key, is_real, data, fname) in \
            zip(btn_cols, export_items):
        with col:
            st.markdown(f"""
            <div class="dark-card" style="text-align:center;padding:22px 10px;margin-bottom:8px;">
                <div style="font-size:26px;margin-bottom:8px;">{icon}</div>
                <div style="font-size:12px;color:#5CDB5C;font-weight:bold;">{title}</div>
                <div style="font-size:10px;color:#82E0AA;margin:3px 0;">{meta}</div>
                <div style="font-size:9px;color:#3A6A3A;">{desc}</div>
            </div>""", unsafe_allow_html=True)

            if is_real:
                st.download_button(
                    label=btn_label,
                    data=data,
                    file_name=fname,
                    mime="text/csv",
                    key=key,
                    use_container_width=True,
                )
            else:
                st.button(btn_label, key=key, use_container_width=True)
                st.markdown(
                    "<div style='font-size:9px;color:#3A6A3A;text-align:center;"
                    "margin-top:3px;'>Placeholder — full version generates live output</div>",
                    unsafe_allow_html=True)

    # CSV Preview
    st.markdown('<div class="sec-title" style="margin-top:22px;">📋 CSV PREVIEW — FIRST 24 ROWS</div>',
                unsafe_allow_html=True)

    preview = full_ts.head(24)[['Field_ID','Month','NDVI','NDWI','SAR_VH_VV','Crop','Stage','Stress']]
    st.dataframe(
        preview.style
            .format({'NDVI': '{:.3f}', 'NDWI': '{:.3f}', 'SAR_VH_VV': '{:.3f}'})
            .background_gradient(subset=['NDVI','NDWI','SAR_VH_VV'], cmap='Greens'),
        use_container_width=True,
        height=370,
    )

    # Summary stats
    st.markdown('<div class="sec-title">📦 EXPORT SUMMARY</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="dark-card">
            <div class="kpi-value">{len(full_ts):,}</div>
            <div class="kpi-label">Total CSV rows</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="dark-card">
            <div class="kpi-value">{len(df)}</div>
            <div class="kpi-label">Fields exported</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="dark-card">
            <div class="kpi-value">12</div>
            <div class="kpi-label">Months per field</div>
        </div>""", unsafe_allow_html=True)
