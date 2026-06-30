"""Page 5 — Time-Series Inspector"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import mock_data as md

_DARK = dict(
    paper_bgcolor='#0A0F0A', plot_bgcolor='#0D1F0D',
    font=dict(color='#2ECC40', family='Courier New'),
)

# Month index → name for vertical lines
_MONTH_X = {m: i for i, m in enumerate(md.MONTH_NAMES)}

# Stage transition months
_STAGE_TRANSITIONS = [
    ('Jun', 'Sowing',       '#F9E79F'),
    ('Jul', 'Vegetative',   '#82E0AA'),
    ('Aug', 'Reproductive', '#1E8449'),
    ('Oct', 'Maturity',     '#784212'),
]


def render(df: pd.DataFrame):
    all_fields = sorted(df['Field_ID'].tolist())

    col_ctrl, _ = st.columns([1, 3])
    with col_ctrl:
        sel = st.selectbox(
            "SELECT FIELD ID",
            all_fields,
            index=0,
            key="ts_field_sel",
        )

    ts        = md.generate_timeseries(sel)
    field_row = df[df['Field_ID'] == sel].iloc[0]

    # Field metadata strip
    disp_c = md.STRESS_DISPLAY.get(field_row['Stress'], '#2ECC40')
    st.markdown(f"""
    <div class="dark-card" style="display:flex;flex-wrap:wrap;gap:20px;
                padding:10px 14px;font-size:11px;margin-bottom:4px;">
        <span><span style="color:#82E0AA;">CROP&nbsp;:&nbsp;</span>{field_row['Crop']}</span>
        <span><span style="color:#82E0AA;">STAGE&nbsp;:&nbsp;</span>{field_row['Stage']}</span>
        <span><span style="color:#82E0AA;">STRESS&nbsp;:&nbsp;</span>
              <span style="color:{disp_c};">{field_row['Stress']}</span></span>
        <span><span style="color:#82E0AA;">AREA&nbsp;:&nbsp;</span>{field_row['Area_ha']} ha</span>
        <span><span style="color:#82E0AA;">INDEX&nbsp;:&nbsp;</span>{field_row['Index_Name']}</span>
        <span><span style="color:#82E0AA;">SOURCE&nbsp;:&nbsp;</span>{field_row['Source']}</span>
    </div>""", unsafe_allow_html=True)

    # Time-series chart
    fig = go.Figure()

    # NDVI — green line
    fig.add_trace(go.Scatter(
        x=ts['Month'], y=ts['NDVI'],
        name='NDVI', mode='lines+markers',
        line=dict(color='#27AE60', width=2.5),
        marker=dict(size=5, color='#27AE60', symbol='circle'),
    ))
    # NDWI — blue line
    fig.add_trace(go.Scatter(
        x=ts['Month'], y=ts['NDWI'],
        name='NDWI', mode='lines+markers',
        line=dict(color='#2980B9', width=2.5),
        marker=dict(size=5, color='#2980B9', symbol='diamond'),
    ))
    # SAR VH/VV — orange dashed
    fig.add_trace(go.Scatter(
        x=ts['Month'], y=ts['SAR_VH_VV'],
        name='SAR VH/VV', mode='lines+markers',
        line=dict(color='#E67E22', width=2.5, dash='dash'),
        marker=dict(size=5, color='#E67E22', symbol='square'),
    ))

    # Phenology stage transition lines (use integer x-index for categorical axis)
    month_idx = {m: i for i, m in enumerate(md.MONTH_NAMES)}
    for month, label, color in _STAGE_TRANSITIONS:
        xi = month_idx.get(month, 0)
        fig.add_shape(
            type='line',
            x0=xi, x1=xi, y0=-0.45, y1=1.05,
            line=dict(color=color, width=1.5, dash='dot'),
        )
        fig.add_annotation(
            x=xi, y=1.0,
            text=label,
            showarrow=False,
            font=dict(color=color, size=10, family='Courier New'),
            xanchor='left',
            yanchor='bottom',
            textangle=0,
        )

    fig.update_layout(
        **_DARK,
        title=dict(
            text=f"Spectral Signature Time-Series — Field {sel} | Jayakwadi CA",
            font=dict(color='#5CDB5C', size=13, family='Courier New'),
        ),
        height=420,
        margin=dict(t=50, b=45, l=65, r=20),
        legend=dict(
            bgcolor='#0D1F0D', bordercolor='#1A4A1A', borderwidth=1,
            font=dict(color='#2ECC40', family='Courier New', size=11),
        ),
        xaxis=dict(
            gridcolor='#1A4A1A', linecolor='#1A4A1A',
            title=dict(text='Month — 2024', font=dict(color='#82E0AA', size=11)),
        ),
        yaxis=dict(
            gridcolor='#1A4A1A', linecolor='#1A4A1A',
            title=dict(text='Index Value', font=dict(color='#82E0AA', size=11)),
            range=[-0.45, 1.05],
            zeroline=True, zerolinecolor='#1A4A1A',
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Raw data table
    st.markdown('<div class="sec-title">📋 RAW INDEX VALUES</div>', unsafe_allow_html=True)
    display_ts = ts[['Month', 'NDVI', 'NDWI', 'SAR_VH_VV']].copy()
    display_ts.columns = ['Month', 'NDVI', 'NDWI', 'SAR VH/VV']
    st.dataframe(
        display_ts.style
            .format({'NDVI': '{:.3f}', 'NDWI': '{:.3f}', 'SAR VH/VV': '{:.3f}'})
            .background_gradient(subset=['NDVI', 'NDWI', 'SAR VH/VV'], cmap='Greens'),
        use_container_width=True,
        height=220,
    )
