import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader import CLUSTER_COLOR, FITUR_LABEL, TARGETS

NAVY   = "#0B1F3A"
TEAL   = "#0E7B6C"
WHITE  = "#FFFFFF"
BORDER = "#DDE3EA"
MUTED  = "#6B7A8D"


def _base_layout(**kwargs):
    base = dict(
        font=dict(family="Inter, sans-serif", size=12, color=NAVY),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        margin=dict(t=48, b=40, l=40, r=20),
        legend=dict(bgcolor=WHITE, bordercolor=BORDER, borderwidth=1),
    )
    base.update(kwargs)
    return base


def _grid(fig):
    fig.update_xaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False, linecolor=BORDER)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False, linecolor=BORDER)
    return fig


# ── Scatter map (bubble) ──────────────────────────────────────────────────────
def province_map(df, color_col='cluster_label', size_col=None, title="Peta Klaster Provinsi"):
    hover_cols = {
        'cluster_label': True,
        'NEET_usiamuda': ':.2f',
        'gabungan_pendudukmiskin': ':.2f',
        'TPT': ':.2f',
        'lat': False, 'lon': False,
    }
    # Add ARPS columns if present
    for t in TARGETS:
        if t in df.columns:
            hover_cols[t] = ':.2f'

    size_data = df[size_col].abs() + 2 if size_col and size_col in df.columns else None

    fig = px.scatter_mapbox(
        df,
        lat='lat', lon='lon',
        color=color_col,
        color_discrete_map=CLUSTER_COLOR,
        size=size_data if size_data is not None else [10] * len(df),
        size_max=30,
        hover_name='Provinsi',
        hover_data=hover_cols,
        zoom=3.8,
        center={'lat': -2.5, 'lon': 118},
        mapbox_style='carto-positron',
        title=title,
        labels={'cluster_label': 'Klaster'},
    )
    fig.update_layout(
        height=520,
        margin=dict(t=50, b=10, l=10, r=10),
        legend=dict(orientation='h', y=0.02, x=0.02, bgcolor='rgba(255,255,255,0.85)'),
        font=dict(family='Inter, sans-serif', color=NAVY),
    )
    return fig


# ── PCA scatter ───────────────────────────────────────────────────────────────
def pca_scatter(df):
    fig = px.scatter(
        df, x='PC1', y='PC2',
        color='cluster_label',
        color_discrete_map=CLUSTER_COLOR,
        text='Provinsi',
        hover_data={'NEET_usiamuda': ':.2f', 'gabungan_pendudukmiskin': ':.2f', 'cluster_label': False},
        labels={'PC1': 'PC1 — Pola Sosial-Ekonomi', 'PC2': 'PC2 — Struktur Pendidikan'},
        title='Visualisasi Klaster Provinsi (Ruang PCA)',
    )
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=8.5, color=NAVY),
        marker=dict(size=11, opacity=0.85, line=dict(width=1, color=WHITE)),
    )
    fig.update_layout(**_base_layout(height=460, legend_title_text='Klaster'))
    return _grid(fig)


# ── Cluster profile bar ───────────────────────────────────────────────────────
def cluster_profile_bar(df, feature):
    profile = df.groupby('cluster_label')[feature].mean().reset_index()
    label = FITUR_LABEL.get(feature, feature)
    fig = go.Figure(go.Bar(
        x=profile['cluster_label'],
        y=profile[feature],
        marker_color=[CLUSTER_COLOR.get(c, TEAL) for c in profile['cluster_label']],
        text=profile[feature].round(3),
        textposition='outside',
    ))
    fig.update_layout(**_base_layout(
        title=f'Rata-rata {label} per Klaster',
        xaxis_title='Klaster', yaxis_title=label, height=320,
    ))
    return _grid(fig)


# ── Cluster radar ─────────────────────────────────────────────────────────────
def cluster_radar(df, features_show=None):
    if features_show is None:
        features_show = [
            'gabungan_pendudukmiskin', 'TPT', 'NEET_usiamuda',
            'tenagakerjaformal', 'gabungan_HLS', 'gabungan_RLS',
        ]
    profile = df.groupby('cluster_label')[features_show].mean()
    # Normalize 0–10
    mn, mx = profile.min(), profile.max()
    norm = (profile - mn) / (mx - mn + 1e-9) * 10

    labels = [FITUR_LABEL.get(f, f).split('(')[0].strip() for f in features_show]
    fig = go.Figure()
    for cl, color in CLUSTER_COLOR.items():
        if cl not in norm.index:
            continue
        vals = norm.loc[cl].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name=cl,
            line=dict(color=color, width=2),
            fillcolor=color.replace(')', ',0.15)').replace('rgb', 'rgba') if 'rgb' in color else color + '26',
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=WHITE,
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=9)),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        title='Profil Multidimensi Tiap Klaster (Normalized 0–10)',
        height=420,
        paper_bgcolor=WHITE,
        font=dict(family='Inter, sans-serif', color=NAVY),
        legend=dict(orientation='h', y=-0.15),
        margin=dict(t=60, b=60, l=40, r=40),
    )
    return fig


# ── ARPS bar chart ────────────────────────────────────────────────────────────
def arps_bar(df_cluster, target_col, title=None):
    if target_col not in df_cluster.columns:
        return None
    df_s = df_cluster.sort_values(target_col, ascending=True)
    colors = [CLUSTER_COLOR.get(c, MUTED) for c in df_s['cluster_label']]
    fig = go.Figure(go.Bar(
        x=df_s[target_col], y=df_s['Provinsi'],
        orientation='h',
        marker_color=colors,
        text=df_s[target_col].round(2),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x:.2f}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(
        title=title or f'{target_col} per Provinsi',
        xaxis_title='Nilai (%)',
        height=820,
        yaxis=dict(tickfont=dict(size=10)),
    ))
    return _grid(fig)


# ── Prediction gauge ─────────────────────────────────────────────────────────
def prediction_gauge(value, threshold, target_label):
    pct = min(100, max(0, (value / (threshold * 2)) * 100))
    color = '#C0392B' if value >= threshold else '#1A7F4B'
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=round(value, 2),
        delta={'reference': threshold, 'valueformat': '.2f'},
        title={'text': target_label, 'font': {'size': 13, 'color': NAVY, 'family': 'Inter'}},
        number={'suffix': '%', 'font': {'color': color, 'size': 28}},
        gauge={
            'axis': {'range': [0, threshold * 2], 'tickcolor': MUTED},
            'bar': {'color': color},
            'bgcolor': WHITE,
            'borderwidth': 1,
            'bordercolor': BORDER,
            'threshold': {
                'line': {'color': '#D4850A', 'width': 3},
                'thickness': 0.8,
                'value': threshold,
            },
            'steps': [
                {'range': [0, threshold], 'color': '#D1FAE5'},
                {'range': [threshold, threshold * 2], 'color': '#FEE2E2'},
            ],
        },
    ))
    fig.update_layout(
        height=240,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor=WHITE,
        font=dict(family='Inter, sans-serif', color=NAVY),
    )
    return fig


# ── Feature importance bar ───────────────────────────────────────────────────
def feature_importance_bar(model, top_n=10):
    if not hasattr(model, 'feature_importances_'):
        return None
    imp = pd.Series(model.feature_importances_, index=FITUR_LABEL.keys())
    imp = imp.sort_values(ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(
        x=imp.values,
        y=[FITUR_LABEL.get(i, i) for i in imp.index],
        orientation='h',
        marker_color=TEAL,
        opacity=0.85,
    ))
    fig.update_layout(**_base_layout(
        title=f'Feature Importance (Top {top_n})',
        xaxis_title='Importance Score',
        height=360,
        yaxis=dict(tickfont=dict(size=10)),
    ))
    return _grid(fig)
