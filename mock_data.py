"""
AgroSense AI — Mock Data Generator
All data generated with fixed seed=42 globally; per-field seeds derived from field ID.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

# ─── GLOBAL SEED ─────────────────────────────────────────────────────────────
np.random.seed(42)

# ─── GEOGRAPHIC CONSTANTS ────────────────────────────────────────────────────
CENTER_LAT = 19.4848      # Jayakwadi Dam
CENTER_LON = 75.3687
GRID_ROWS  = 8
GRID_COLS  = 8
CELL_LAT   = 0.007        # ~780 m per cell
CELL_LON   = 0.009        # ~840 m per cell

# ─── CROP DEFINITIONS ────────────────────────────────────────────────────────
CROPS         = ['Paddy', 'Cotton', 'Sugarcane', 'Soybean', 'Fallow']
CROP_WEIGHTS  = [0.40,    0.20,     0.15,        0.15,      0.10]
CROP_FILL     = {
    'Paddy':     '#27AE60',
    'Cotton':    '#C8A84B',
    'Sugarcane': '#145A32',
    'Soybean':   '#C7B570',
    'Fallow':    '#7F8C8D',
}

# ─── PHENOLOGY STAGES ────────────────────────────────────────────────────────
STAGES        = ['Sowing', 'Vegetative', 'Reproductive', 'Maturity']
STAGE_WEIGHTS = [0.10,     0.35,         0.40,           0.15]
STAGE_FILL    = {
    'Sowing':       '#F9E79F',
    'Vegetative':   '#82E0AA',
    'Reproductive': '#1E8449',
    'Maturity':     '#784212',
}
STAGE_DAT     = {
    'Sowing':       '0–20 DAT',
    'Vegetative':   '21–55 DAT',
    'Reproductive': '56–90 DAT',
    'Maturity':     '91+ DAT',
}
STAGE_DAT_RANGE = {
    'Sowing':       (1,  20),
    'Vegetative':   (21, 55),
    'Reproductive': (56, 90),
    'Maturity':     (91, 120),
}

# ─── PGSIF INDEX GATING ──────────────────────────────────────────────────────
STAGE_INDEX = {
    'Sowing':       'NDVI Anomaly + SMI',
    'Vegetative':   'NDWI (Sentinel-2 B8/B11)',
    'Reproductive': 'SAR VH/VV Ratio (Sentinel-1 GRD)',
    'Maturity':     'VCI (MODIS 250m)',
}
GATE_NOTES = {
    'Sowing':       'PGSIF Gate: Pre-emergence phase → NDVI Anomaly + Soil Moisture Index (SMI) active. Low canopy cover; optical anomaly detection most reliable.',
    'Vegetative':   'PGSIF Gate: Canopy development → NDWI optical moisture index active. Green canopy enables water-sensitive B8/B11 band response.',
    'Reproductive': 'PGSIF Gate: Ear/panicle emergence → SAR VH/VV microwave backscatter gate active. Penetrates canopy; sensitive to grain moisture.',
    'Maturity':     'PGSIF Gate: Senescence phase → VCI (Vegetation Condition Index, MODIS 250m) thermal gate. Multi-temporal anomaly vs. historical median.',
}

# ─── STRESS LEVELS ───────────────────────────────────────────────────────────
STRESS_LEVELS  = ['Low', 'Moderate', 'Severe']
STRESS_WEIGHTS = [0.40,  0.38,       0.22]
STRESS_FILL    = {
    'No Stress': '#1A5C1A',
    'Low':       '#4A7A1A',
    'Moderate':  '#C07A00',
    'High':      '#8B2500',
    'Severe':    '#4A0000',
}
STRESS_BORDER  = {
    'No Stress': '#2ECC40',
    'Low':       '#82E0AA',
    'Moderate':  '#E67E22',
    'High':      '#E74C3C',
    'Severe':    '#8B0000',
}
STRESS_DISPLAY = {
    'No Stress': '#27AE60',
    'Low':       '#82E0AA',
    'Moderate':  '#E67E22',
    'High':      '#E74C3C',
    'Severe':    '#8B0000',
}

# ─── FIELD GENERATION ────────────────────────────────────────────────────────

def generate_fields() -> pd.DataFrame:
    """Generate 8×8 = 64 fields with reproducible random attributes."""
    start_lat = CENTER_LAT - (GRID_ROWS / 2) * CELL_LAT
    start_lon = CENTER_LON - (GRID_COLS / 2) * CELL_LON
    rows = []

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            fid  = f"F{r:02d}{c:02d}"
            rng  = np.random.RandomState(42 + r * GRID_COLS + c)

            lat1 = round(start_lat + r * CELL_LAT, 6)
            lat2 = round(lat1 + CELL_LAT,           6)
            lon1 = round(start_lon + c * CELL_LON,  6)
            lon2 = round(lon1 + CELL_LON,            6)

            crop   = rng.choice(CROPS,         p=CROP_WEIGHTS)
            stage  = rng.choice(STAGES,        p=STAGE_WEIGHTS) if crop != 'Fallow' else 'Maturity'
            stress = rng.choice(STRESS_LEVELS, p=STRESS_WEIGHTS) if crop != 'Fallow' else 'No Stress'
            conf   = int(rng.randint(78, 95))
            source = rng.choice(['Sentinel-2', 'EOS-04'], p=[0.70, 0.30])
            area   = round(float(rng.uniform(1.5, 4.5)), 1)
            deficit= round(float(rng.uniform(0, 45)),   1)
            dat    = int(rng.randint(*STAGE_DAT_RANGE[stage]))

            idx_name = STAGE_INDEX[stage]
            if   'NDVI' in idx_name: idx_val = round(float(rng.uniform(0.20, 0.55)), 2)
            elif 'NDWI' in idx_name: idx_val = round(float(rng.uniform(-0.30, 0.25)), 2)
            elif 'SAR'  in idx_name: idx_val = round(float(rng.uniform(0.45, 0.85)), 2)
            else:                    idx_val = round(float(rng.uniform(15,   55)),   1)

            rows.append({
                'Field_ID':    fid,
                'Row': r, 'Col': c,
                'Lat1': lat1, 'Lat2': lat2,
                'Lon1': lon1, 'Lon2': lon2,
                'Center_Lat': round((lat1 + lat2) / 2, 6),
                'Center_Lon': round((lon1 + lon2) / 2, 6),
                'Crop':        crop,
                'Stage':       stage,
                'Stress':      stress,
                'Confidence':  conf,
                'Source':      source,
                'Area_ha':     area,
                'Deficit_mm':  deficit,
                'DAT':         dat,
                'Index_Name':  idx_name,
                'Index_Value': idx_val,
                'Gate_Note':   GATE_NOTES[stage],
            })

    return pd.DataFrame(rows)


# ─── TIME-SERIES ─────────────────────────────────────────────────────────────

MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

# Kharif seasonal base curves (Paddy / Jayakwadi CA)
_NDVI_BASE = [0.20, 0.18, 0.22, 0.25, 0.28, 0.42,
              0.60, 0.72, 0.80, 0.65, 0.45, 0.28]
_NDWI_BASE = [-0.20,-0.22,-0.18,-0.15,-0.10, 0.05,
               0.25, 0.38, 0.45, 0.30, 0.10,-0.10]
_SAR_BASE  = [ 0.38, 0.36, 0.38, 0.40, 0.42, 0.52,
               0.63, 0.70, 0.76, 0.65, 0.52, 0.42]

def generate_timeseries(field_id: str) -> pd.DataFrame:
    """12-month spectral time-series with per-field noise."""
    r   = int(field_id[1:3])
    c   = int(field_id[3:5])
    rng = np.random.RandomState(42 + r * GRID_COLS + c + 1000)
    ndvi = np.clip([v + rng.normal(0, 0.025) for v in _NDVI_BASE], 0.0, 1.0)
    ndwi = np.clip([v + rng.normal(0, 0.020) for v in _NDWI_BASE], -1.0, 1.0)
    sar  = np.clip([v + rng.normal(0, 0.018) for v in _SAR_BASE],  0.0, 1.0)
    return pd.DataFrame({
        'Month':     MONTH_NAMES,
        'Month_Num': list(range(1, 13)),
        'NDVI':      np.round(ndvi, 3),
        'NDWI':      np.round(ndwi, 3),
        'SAR_VH_VV': np.round(sar,  3),
    })


# ─── ACCURACY DATA ───────────────────────────────────────────────────────────

CLASSES   = ['Paddy', 'Cotton', 'Sugarcane', 'Soybean', 'Fallow']
CM_VALUES = [
    [187,  8,  3,  5,  2],
    [  6,142,  4,  7,  1],
    [  2,  3, 98,  2,  0],
    [  4,  8,  2,131,  3],
    [  1,  2,  0,  3, 82],
]

def get_accuracy_data():
    cm        = np.array(CM_VALUES, dtype=float)
    precision = cm.diagonal() / cm.sum(axis=0)
    recall    = cm.diagonal() / cm.sum(axis=1)
    f1        = 2 * precision * recall / (precision + recall)
    per_class = pd.DataFrame({
        'Class':     CLASSES,
        'Precision': np.round(precision, 3),
        'Recall':    np.round(recall,    3),
        'F1_Score':  np.round(f1,        3),
    })
    return cm, per_class


# ─── FAO-56 CHAIN ────────────────────────────────────────────────────────────

FAO56 = {
    'ET0':         4.8,
    'Kc':          1.20,
    'ETc':         5.76,
    'RainStorage': 3.17,
    'Deficit8d':   20.7,
}


# ─── COLOR UTILITIES ─────────────────────────────────────────────────────────

def _lerp_color(c1: str, c2: str, t: float) -> str:
    """Linear-interpolate between two hex colors."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return '#{:02x}{:02x}{:02x}'.format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

def deficit_color(val: float, vmin: float = 0, vmax: float = 45) -> str:
    """Map deficit value → light-yellow → orange → dark-red hex color."""
    t = max(0, min(1, (val - vmin) / (vmax - vmin)))
    stops = ['#FFFDE7', '#FFB300', '#E65100', '#B71C1C']
    seg   = t * (len(stops) - 1)
    idx   = min(int(seg), len(stops) - 2)
    return _lerp_color(stops[idx], stops[idx + 1], seg - idx)
