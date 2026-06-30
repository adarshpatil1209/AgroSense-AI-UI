"""Page 6 — Accuracy & Validation Report"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import mock_data as md

_DARK = dict(
    paper_bgcolor='#0A0F0A', plot_bgcolor='#0D1F0D',
    font=dict(color='#2ECC40', family='Courier New'),
)

_GREEN_SCALE = [
    [0.0,  '#0A0F0A'],
    [0.15, '#0D3A0D'],
    [0.40, '#145A32'],
    [0.70, '#1E8449'],
    [0.85, '#27AE60'],
    [1.0,  '#2ECC40'],
]


def render():
    # ── KPI Row ──────────────────────────────────────────────────────────────
    cols = st.columns(4)
    kpis = [
        ("Overall Accuracy", "83.4%",  "Ground-truth validated"),
        ("Kappa Coefficient","0.78",   "Chance-corrected agreement"),
        ("F1-Score",         "0.81",   "Harmonic mean P & R"),
        ("Fields Validated", "320",    "Kharif 2024 samples"),
    ]
    for col, (label, val, sub) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────────────
    col_cm, col_bar = st.columns([1, 1], gap="small")
    cm, per_class   = md.get_accuracy_data()

    # Normalize CM for color scale (raw values as text)
    cm_norm = cm / cm.sum(axis=1, keepdims=True) * 100

    with col_cm:
        st.markdown('<div class="sec-title">🧮 CONFUSION MATRIX — RAW COUNTS</div>',
                    unsafe_allow_html=True)
        # Annotation: raw counts
        annotations = []
        for i in range(len(md.CLASSES)):
            for j in range(len(md.CLASSES)):
                annotations.append(dict(
                    x=md.CLASSES[j], y=md.CLASSES[i],
                    text=str(int(cm[i, j])),
                    showarrow=False,
                    font=dict(color='white' if cm_norm[i,j] > 40 else '#82E0AA',
                               family='Courier New', size=12),
                ))
        fig_cm = go.Figure(go.Heatmap(
            z=cm_norm,
            x=md.CLASSES,
            y=md.CLASSES,
            colorscale=_GREEN_SCALE,
            showscale=True,
            zmin=0, zmax=100,
            colorbar=dict(
                tickfont=dict(color='#82E0AA', family='Courier New', size=10),
                title=dict(text='%', font=dict(color='#82E0AA')),
            ),
        ))
        fig_cm.update_layout(
            **_DARK,
            annotations=annotations,
            height=380,
            margin=dict(t=20, b=50, l=70, r=20),
            xaxis=dict(title='Predicted', side='bottom',
                       tickfont=dict(color='#82E0AA', family='Courier New', size=11)),
            yaxis=dict(title='Actual',
                       tickfont=dict(color='#82E0AA', family='Courier New', size=11)),
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_bar:
        st.markdown('<div class="sec-title">📊 PER-CLASS PRECISION / RECALL / F1</div>',
                    unsafe_allow_html=True)
        fig_bar = go.Figure()
        bar_data = [
            ('Precision', per_class['Precision'], '#27AE60'),
            ('Recall',    per_class['Recall'],    '#E67E22'),
            ('F1-Score',  per_class['F1_Score'],  '#2980B9'),
        ]
        for name, vals, color in bar_data:
            fig_bar.add_trace(go.Bar(
                name=name,
                x=per_class['Class'],
                y=vals,
                marker_color=color,
                text=[f"{v:.3f}" for v in vals],
                textposition='outside',
                textfont=dict(color=color, family='Courier New', size=9),
            ))
        fig_bar.update_layout(
            **_DARK,
            height=380,
            margin=dict(t=20, b=50, l=40, r=20),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.05,
            legend=dict(
                bgcolor='#0D1F0D', bordercolor='#1A4A1A', borderwidth=1,
                font=dict(color='#2ECC40', family='Courier New', size=10),
            ),
            xaxis=dict(gridcolor='#1A4A1A',
                       tickfont=dict(color='#82E0AA', family='Courier New', size=11)),
            yaxis=dict(gridcolor='#1A4A1A', range=[0, 1.15],
                       tickfont=dict(color='#82E0AA', family='Courier New', size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Validation note ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="dark-card" style="font-size:11px;color:#82E0AA;line-height:1.65;">
        &#128203; <strong style="color:#5CDB5C;">Validation Note</strong> — Ground truth: 320
        field-verified samples, Kharif 2024, Jayakwadi CA. Stratified random sampling across
        5 crop classes. Classification via Random Forest + SVM Fusion on multi-temporal
        Sentinel-1 (SAR C-band, 10 m) + Sentinel-2 (optical, 10 m) stack.
        Reference standard: FAO LCCS Level II.
    </div>""", unsafe_allow_html=True)
