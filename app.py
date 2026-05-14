"""
DropAlert — Sistem Deteksi Dini Risiko Putus Sekolah
Berbasis Ensemble Learning & Clustering Provinsi Indonesia
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="DropAlert | Deteksi Dini Risiko Putus Sekolah",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.style import CSS, hero, sec, metric_row, cluster_badge, insight, risk_badge
from style import CSS, hero, sec, metric_row, cluster_badge, insight, risk_badge
from data_loader import load_cluster_data, build_synthetic_model_data, train_models, FITUR, FITUR_LABEL, TARGETS, CLUSTER_LABEL, CLUSTER_COLOR
from charts import province_map, pca_scatter, cluster_profile_bar, cluster_radar, arps_bar, prediction_gauge, feature_importance_bar
from utils.data_loader import (
    load_cluster_data, build_synthetic_model_data, train_models,
    FITUR, FITUR_LABEL, TARGETS, CLUSTER_LABEL, CLUSTER_COLOR,
)
from utils.charts import (
    province_map, pca_scatter, cluster_profile_bar, cluster_radar,
    arps_bar, prediction_gauge, feature_importance_bar,
)

st.markdown(CSS, unsafe_allow_html=True)

# ── Load & cache data ─────────────────────────────────────────────────────────
@st.cache_data
def get_cluster_df():
    return load_cluster_data()

@st.cache_resource
def get_models(df_cluster):
    df_model = build_synthetic_model_data(df_cluster)
    models, scaler, thresholds = train_models(df_model)
    return models, scaler, thresholds, df_model

df_cluster = get_cluster_df()
models, scaler, thresholds, df_model = get_models(df_cluster)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.4rem;text-align:center;">
        <p style="font-size:1.35rem;font-weight:800;color:#FFFFFF;margin:0;letter-spacing:0.05em;">DropAlert</p>
        <p style="font-size:0.70rem;color:#475569;margin:0;text-transform:uppercase;letter-spacing:0.1em;">
            Deteksi Dini Risiko Putus Sekolah
        </p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.08);margin:0.7rem 0;"/>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "NAVIGASI",
        [
            "Beranda",
            "Prediksi Risiko Putus Sekolah",
            "Peta Klaster Indonesia",
            "Analisis Klaster",
        ],
        label_visibility="visible",
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:1rem 0 0.8rem'/>", unsafe_allow_html=True)

    # Global filters
    st.markdown("<p style='font-size:0.78rem;color:#94A3B8;font-weight:600;margin-bottom:0.4rem;'>FILTER DATA</p>", unsafe_allow_html=True)
    filter_cluster = st.multiselect(
        "Klaster",
        options=['Klaster 1', 'Klaster 2', 'Klaster 3'],
        default=['Klaster 1', 'Klaster 2', 'Klaster 3'],
        label_visibility="collapsed",
    )
    filter_prov = st.multiselect(
        "Provinsi",
        options=sorted(df_cluster['Provinsi'].unique()),
        default=[],
        placeholder="Semua provinsi",
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:0.8rem 0;'/>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.72rem;color:#334155;text-align:center;'>Data: BPS Indonesia · 2021–2025</p>", unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df_view = df_cluster.copy()
if filter_cluster:
    df_view = df_view[df_view['cluster_label'].isin(filter_cluster)]
if filter_prov:
    df_view = df_view[df_view['Provinsi'].isin(filter_prov)]


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BERANDA
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "Beranda":
    st.markdown(hero(
        badge="Sistem Deteksi Dini Berbasis Data · Indonesia 2024",
        title="DropAlert:",
        accent="Risiko Putus Sekolah Regional",
        sub=(
            "Platform analitik berbasis <strong>Ensemble Learning</strong> dan "
            "<strong>K-Means Clustering</strong> untuk mendeteksi, memetakan, dan "
            "memprediksi risiko putus sekolah di 38 provinsi Indonesia."
        ),
        quote=(
            "Putus sekolah bukan sekadar keputusan individu — ia merupakan hasil "
            "akumulasi tekanan struktural: kemiskinan, ketimpangan akses, dan "
            "keterbatasan infrastruktur pendidikan yang berbeda antar wilayah."
        ),
    ), unsafe_allow_html=True)

    # Summary metrics
    n_prov   = df_cluster['Provinsi'].nunique()
    n_feat   = len(FITUR)
    n_clust  = df_cluster['cluster'].nunique()
    avg_neet = df_cluster['NEET_usiamuda'].mean()
    st.markdown(metric_row(
        (n_prov,          "Provinsi Tercakup"),
        (n_feat,          "Variabel Prediktor"),
        (n_clust,         "Klaster Risiko"),
        (f"{avg_neet:.1f}%", "Rata-rata NEET Nasional"),
    ), unsafe_allow_html=True)

    # Overview charts
    st.markdown(sec("Peta Sebaran Klaster", "Distribusi spasial kelompok risiko putus sekolah antar provinsi"), unsafe_allow_html=True)
    st.plotly_chart(province_map(df_view), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(sec("Sebaran Klaster (Ruang PCA)"), unsafe_allow_html=True)
        st.plotly_chart(pca_scatter(df_view), use_container_width=True)
    with col2:
        st.markdown(sec("Komposisi Klaster"), unsafe_allow_html=True)
        summary = df_view.groupby('cluster_label').agg(
            Jumlah=('Provinsi', 'count'),
            NEET_Rata=('NEET_usiamuda', 'mean'),
            Kemiskinan_Rata=('gabungan_pendudukmiskin', 'mean'),
            TPT_Rata=('TPT', 'mean'),
        ).round(2).reset_index()
        for _, row in summary.iterrows():
            badge = cluster_badge(row['cluster_label'])
            st.markdown(f"""
            <div class="card" style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.55rem;">
                    <strong style="font-size:0.95rem;">{row['cluster_label']}</strong>
                    {badge}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.35rem;font-size:0.83rem;color:#475569;">
                    <div>Provinsi: <strong>{int(row['Jumlah'])}</strong></div>
                    <div>NEET: <strong>{row['NEET_Rata']:.1f}%</strong></div>
                    <div>Miskin: <strong>{row['Kemiskinan_Rata']:.1f}%</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(sec("Profil Indikator Klaster"), unsafe_allow_html=True)
    st.plotly_chart(cluster_radar(df_view), use_container_width=True)

    st.markdown(insight(
        "<strong>Temuan Utama:</strong> Analisis klaster mengidentifikasi tiga kelompok provinsi dengan "
        "profil risiko yang berbeda. Provinsi dalam Klaster 3 menunjukkan kombinasi kemiskinan tinggi, "
        "NEET tinggi, dan rasio guru/sekolah rendah — indikator struktural utama risiko putus sekolah. "
        "Sebagian besar provinsi Papua dan Nusa Tenggara masuk dalam kelompok ini."
    ), unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:3rem;padding:1.2rem 1.8rem;background:#0B1F3A;border-radius:14px;
                display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
        <div>
            <p style="font-size:0.95rem;font-weight:700;color:#FFFFFF;margin:0;">DropAlert</p>
            <p style="font-size:0.72rem;color:#475569;margin:0;">Sistem Deteksi Dini Risiko Putus Sekolah Indonesia</p>
        </div>
        <div style="font-size:0.75rem;color:#475569;text-align:center;">
            Sumber: BPS · Kemdikbud · Data Resmi Nasional 2021–2025
        </div>
        <div style="font-size:0.75rem;color:#475569;text-align:right;">
            Ensemble Learning · K-Means Clustering · PCA
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDIKSI
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Prediksi Risiko Putus Sekolah":
    st.markdown(hero(
        badge="Ensemble Learning — Gradient Boosting",
        title="Prediksi",
        accent="Risiko Putus Sekolah",
        sub=(
            "Masukkan kondisi sosial-ekonomi dan pendidikan suatu wilayah untuk mendapatkan "
            "estimasi Angka Risiko Putus Sekolah (ARPS) di empat kelompok usia."
        ),
    ), unsafe_allow_html=True)

    st.markdown(sec("Input Indikator Wilayah", "Isi minimal 3 indikator utama — nilai lain menggunakan rata-rata nasional"), unsafe_allow_html=True)

    # Use province defaults as starting point
    prov_list = ['(Manual)'] + sorted(df_cluster['Provinsi'].tolist())
    prov_sel = st.selectbox("Mulai dari data provinsi (opsional):", prov_list)

    if prov_sel != '(Manual)':
        defaults = df_cluster[df_cluster['Provinsi'] == prov_sel].iloc[0]
    else:
        defaults = df_cluster[FITUR].mean()

    nat_mean = df_cluster[FITUR].mean()
    nat_std  = df_cluster[FITUR].std()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Kondisi Sosial-Ekonomi**")
        pend_miskin = st.number_input(
            "Persentase Penduduk Miskin (%)",
            min_value=0.0, max_value=50.0,
            value=float(round(defaults['gabungan_pendudukmiskin'], 2)),
            step=0.1, format="%.2f",
        )
        tpt = st.number_input(
            "Tingkat Pengangguran Terbuka / TPT (%)",
            min_value=0.0, max_value=30.0,
            value=float(round(defaults['TPT'], 2)),
            step=0.1, format="%.2f",
        )
        neet = st.number_input(
            "NEET Usia Muda 15–24 Tahun (%)",
            min_value=0.0, max_value=60.0,
            value=float(round(defaults['NEET_usiamuda'], 2)),
            step=0.1, format="%.2f",
        )
        tk_formal = st.number_input(
            "Tenaga Kerja Formal (%)",
            min_value=0.0, max_value=100.0,
            value=float(round(defaults['tenagakerjaformal'], 2)),
            step=0.1, format="%.2f",
        )

    with col2:
        st.markdown("**Kualitas Pendidikan**")
        hls = st.number_input(
            "Harapan Lama Sekolah (Tahun)",
            min_value=5.0, max_value=20.0,
            value=float(round(defaults['gabungan_HLS'], 2)),
            step=0.1, format="%.2f",
        )
        rls = st.number_input(
            "Rata-rata Lama Sekolah (Tahun)",
            min_value=3.0, max_value=15.0,
            value=float(round(defaults['gabungan_RLS'], 2)),
            step=0.1, format="%.2f",
        )
        rasio_guru_sma = st.number_input(
            "Rasio Guru/Murid SMA",
            min_value=0.01, max_value=0.5,
            value=float(round(defaults['rasio_guru_SMA'], 4)),
            step=0.001, format="%.4f",
        )
        rasio_guru_smk = st.number_input(
            "Rasio Guru/Murid SMK",
            min_value=0.01, max_value=0.5,
            value=float(round(defaults['rasio_guru_SMK'], 4)),
            step=0.001, format="%.4f",
        )

    with col3:
        st.markdown("**Infrastruktur Pendidikan**")
        rasio_guru_sd = st.number_input(
            "Rasio Guru/Murid SD",
            min_value=0.01, max_value=0.5,
            value=float(round(defaults['rasio_guru_SD'], 4)),
            step=0.001, format="%.4f",
        )
        rasio_guru_smp = st.number_input(
            "Rasio Guru/Murid SMP",
            min_value=0.01, max_value=0.5,
            value=float(round(defaults['rasio_guru_SMP'], 4)),
            step=0.001, format="%.4f",
        )
        rasio_sek_sma = st.number_input(
            "Rasio Sekolah/Murid SMA",
            min_value=0.0001, max_value=0.05,
            value=float(round(defaults['rasio_sekolah_SMA'], 5)),
            step=0.0001, format="%.5f",
        )
        rasio_sek_smk = st.number_input(
            "Rasio Sekolah/Murid SMK",
            min_value=0.0001, max_value=0.05,
            value=float(round(defaults['rasio_sekolah_SMK'], 5)),
            step=0.0001, format="%.5f",
        )

    # remaining features from defaults
    rasio_sek_sd  = float(defaults['rasio_sekolah_SD'])
    rasio_sek_smp = float(defaults['rasio_sekolah_SMP'])

    run_pred = st.button("Jalankan Prediksi", use_container_width=False)

    if run_pred:
        X_input = np.array([[
            pend_miskin, tpt, neet, tk_formal,
            hls, rls,
            rasio_guru_sma, rasio_guru_smk, rasio_guru_sd, rasio_guru_smp,
            rasio_sek_sma, rasio_sek_smk, rasio_sek_sd, rasio_sek_smp,
        ]])

        # Validate — no NaN
        if np.any(np.isnan(X_input)):
            st.error("Terdapat nilai kosong. Pastikan semua input terisi.")
        else:
            X_scaled = scaler.transform(X_input)

            st.markdown(sec("Hasil Prediksi ARPS", "Angka Risiko Putus Sekolah per kelompok usia"), unsafe_allow_html=True)

            results = {}
            for target, label in TARGETS.items():
                pred_val = float(models[target].predict(X_scaled)[0])
                pred_val = max(0.0, pred_val)
                thr = thresholds[target]
                risk_cat = "Tinggi" if pred_val >= thr else "Rendah"
                results[target] = {'value': pred_val, 'threshold': thr, 'risk': risk_cat, 'label': label}

            # Gauge charts
            gcols = st.columns(4)
            for i, (target, res) in enumerate(results.items()):
                with gcols[i]:
                    st.plotly_chart(
                        prediction_gauge(res['value'], res['threshold'], res['label'].split('(')[0].strip()),
                        use_container_width=True,
                    )

            # Summary table
            st.markdown(sec("Ringkasan Prediksi"), unsafe_allow_html=True)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            summary_rows = []
            for target, res in results.items():
                badge_html = risk_badge(res['risk'])
                summary_rows.append({
                    'Kelompok Usia': res['label'],
                    'Prediksi ARPS (%)': round(res['value'], 3),
                    'Ambang Batas (%)': round(res['threshold'], 3),
                    'Selisih': round(res['value'] - res['threshold'], 3),
                    'Status': res['risk'],
                })
            df_summary = pd.DataFrame(summary_rows)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Narrative insight
            tinggi = [r['label'].split('(')[0].strip() for r in results.values() if r['risk'] == 'Tinggi']
            if tinggi:
                st.markdown(insight(
                    f"<strong>Perhatian:</strong> Prediksi menunjukkan risiko putus sekolah <strong>tinggi</strong> "
                    f"pada kelompok usia: <strong>{', '.join(tinggi)}</strong>. "
                    f"Kondisi ini dipengaruhi terutama oleh tingkat kemiskinan ({pend_miskin:.1f}%) "
                    f"dan NEET ({neet:.1f}%) yang relatif tinggi. "
                    f"Intervensi program beasiswa, peningkatan infrastruktur sekolah, dan program ketenagakerjaan "
                    f"pemuda sangat direkomendasikan."
                ), unsafe_allow_html=True)
            else:
                st.markdown(insight(
                    "<strong>Kondisi relatif baik:</strong> Seluruh kelompok usia menunjukkan risiko putus sekolah "
                    "di bawah ambang batas nasional. Tetap perlu pemantauan berkala, khususnya pada kelompok "
                    "usia menengah atas (16–23 tahun) yang lebih sensitif terhadap perubahan ekonomi."
                ), unsafe_allow_html=True)

            # Feature importance
            st.markdown(sec("Kontribusi Variabel (Model SMA/16-18 Thn)"), unsafe_allow_html=True)
            fig_imp = feature_importance_bar(models['ARPS_16to18'])
            if fig_imp:
                st.plotly_chart(fig_imp, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PETA KLASTER
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Peta Klaster Indonesia":
    st.markdown(hero(
        badge="Visualisasi Spasial · 38 Provinsi",
        title="Peta Klaster",
        accent="Risiko Putus Sekolah",
        sub=(
            "Sebaran geografis klaster risiko putus sekolah di seluruh provinsi Indonesia "
            "berdasarkan analisis K-Means pada indikator sosial-ekonomi dan pendidikan."
        ),
    ), unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Peta Interaktif", "Tabel Data Provinsi"])

    with tab1:
        size_opt = st.selectbox(
            "Ukuran gelembung berdasarkan:",
            ['(default)', 'NEET_usiamuda', 'gabungan_pendudukmiskin', 'TPT'],
            format_func=lambda x: x if x == '(default)' else FITUR_LABEL.get(x, x),
        )
        size_col = None if size_opt == '(default)' else size_opt

        st.plotly_chart(
            province_map(df_view, size_col=size_col,
                         title=f"Peta Klaster Provinsi — {len(df_view)} provinsi ditampilkan"),
            use_container_width=True,
        )

        # Legend boxes
        col1, col2, col3 = st.columns(3)
        cluster_meta = {
            'Klaster 1': {
                'bg': '#F0FDF4', 'border': '#86EFAC', 'txt': '#065F46',
                'desc': 'Risiko relatif rendah. Kemiskinan rendah, NEET terkendali, infrastruktur pendidikan memadai.',
                'contoh': 'Bali, DKI Jakarta, Banten, Kep. Riau',
            },
            'Klaster 2': {
                'bg': '#FFFBEB', 'border': '#FCD34D', 'txt': '#92400E',
                'desc': 'Risiko menengah. Indikator pendidikan cukup baik namun tekanan ketenagakerjaan masih terasa.',
                'contoh': 'Sebagian besar Jawa, Sumatra, Kalimantan, Sulawesi',
            },
            'Klaster 3': {
                'bg': '#FFF1F2', 'border': '#FCA5A5', 'txt': '#991B1B',
                'desc': 'Risiko tinggi. Kemiskinan dan NEET tinggi, rasio guru/sekolah rendah, akses pendidikan terbatas.',
                'contoh': 'Papua Tengah, Papua Pegunungan, NTT, Aceh',
            },
        }
        for col, (klabel, meta) in zip([col1, col2, col3], cluster_meta.items()):
            with col:
                n_prov_cl = len(df_cluster[df_cluster['cluster_label'] == klabel])
                st.markdown(f"""
                <div class="card" style="background:{meta['bg']};border-color:{meta['border']};margin-top:0.5rem;">
                    <strong style="color:{meta['txt']};">{klabel}</strong>
                    <p style="font-size:0.78rem;color:{meta['txt']};margin:0.3rem 0;font-weight:600;">{n_prov_cl} provinsi</p>
                    <p style="font-size:0.82rem;color:#374151;margin:0 0 0.4rem;">{meta['desc']}</p>
                    <p style="font-size:0.76rem;color:#6B7A8D;margin:0;"><em>Contoh: {meta['contoh']}</em></p>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        show_cols = ['Provinsi', 'cluster_label', 'NEET_usiamuda',
                     'gabungan_pendudukmiskin', 'TPT', 'tenagakerjaformal',
                     'gabungan_HLS', 'gabungan_RLS']
        show_cols = [c for c in show_cols if c in df_view.columns]
        display_df = df_view[show_cols].copy().rename(columns={
            **FITUR_LABEL, 'cluster_label': 'Klaster',
        }).round(4)
        st.dataframe(display_df, use_container_width=True, height=500)
        st.download_button(
            "Unduh Data",
            data=display_df.to_csv(index=False),
            file_name="dropalert_cluster_data.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALISIS KLASTER
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Analisis Klaster":
    st.markdown(hero(
        badge="K-Means Clustering · 3 Klaster Optimal",
        title="Profil dan Analisis",
        accent="Tiap Klaster",
        sub=(
            "Perbandingan mendalam karakteristik sosial-ekonomi dan pendidikan "
            "antar klaster untuk mendukung perumusan kebijakan yang tepat sasaran."
        ),
    ), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Profil Klaster", "Perbandingan Variabel", "Anggota Klaster", "Rekomendasi Kebijakan"
    ])

    with tab1:
        st.plotly_chart(cluster_radar(df_view), use_container_width=True)

        profile = df_view.groupby('cluster_label')[FITUR].mean().round(4)
        st.markdown("**Rata-rata Indikator per Klaster**")
        st.dataframe(
            profile.rename(columns=FITUR_LABEL),
            use_container_width=True,
        )

        st.markdown(insight(
            "Klaster 3 secara konsisten menunjukkan nilai tertinggi pada indikator tekanan "
            "(kemiskinan, NEET, TPT) dan terendah pada indikator kapasitas (tenaga kerja formal, HLS, RLS). "
            "Pola ini mengkonfirmasi bahwa risiko putus sekolah bersifat multidimensi — tidak hanya soal "
            "kemiskinan, tetapi juga keterbatasan infrastruktur pendidikan yang saling memperkuat."
        ), unsafe_allow_html=True)

    with tab2:
        feat_sel = st.selectbox(
            "Pilih variabel:",
            FITUR,
            format_func=lambda x: FITUR_LABEL.get(x, x),
        )
        st.plotly_chart(cluster_profile_bar(df_view, feat_sel), use_container_width=True)

        # Distribution boxplot
        import plotly.graph_objects as go
        from utils.charts import CLUSTER_COLOR, _base_layout, _grid
        fig_box = go.Figure()
        for cl, color in CLUSTER_COLOR.items():
            sub = df_view[df_view['cluster_label'] == cl]
            if len(sub) == 0:
                continue
            fig_box.add_trace(go.Box(
                y=sub[feat_sel], name=cl,
                marker_color=color,
                boxmean='sd', jitter=0.4, pointpos=-1.8,
                marker=dict(size=5, opacity=0.6),
            ))
        label = FITUR_LABEL.get(feat_sel, feat_sel)
        fig_box.update_layout(**_base_layout(
            title=f'Distribusi {label} per Klaster',
            yaxis_title=label, height=320,
        ))
        st.plotly_chart(_grid(fig_box), use_container_width=True)

    with tab3:
        for klabel in ['Klaster 1', 'Klaster 2', 'Klaster 3']:
            provs = df_cluster[df_cluster['cluster_label'] == klabel]['Provinsi'].sort_values().tolist()
            with st.expander(f"{klabel} — {len(provs)} provinsi"):
                # Show as grid
                cols3 = st.columns(3)
                for i, p in enumerate(provs):
                    with cols3[i % 3]:
                        row = df_cluster[df_cluster['Provinsi'] == p].iloc[0]
                        st.markdown(f"""
                        <div style="background:#F8FAFC;border:1px solid #DDE3EA;border-radius:8px;
                                    padding:0.6rem 0.8rem;margin-bottom:0.5rem;font-size:0.83rem;">
                            <strong>{p.title()}</strong><br>
                            <span style="color:#6B7A8D;">NEET: {row['NEET_usiamuda']:.1f}% &nbsp;|&nbsp;
                            Miskin: {row['gabungan_pendudukmiskin']:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)

    with tab4:
        recs = [
            {
                'klaster': 'Klaster 3',
                'bg': '#FFF1F2', 'border': '#FCA5A5', 'txt': '#991B1B',
                'judul': 'Intervensi Prioritas Tinggi',
                'items': [
                    ('Penguatan Program Beasiswa Daerah Tertinggal',
                     'Perluas cakupan KIP (Kartu Indonesia Pintar) dan beasiswa daerah 3T untuk memutus rantai putus sekolah akibat keterbatasan ekonomi.'),
                    ('Rekrutmen dan Distribusi Guru ke Daerah Terpencil',
                     'Program redistribusi guru dengan insentif penugasan di daerah dengan rasio guru/murid rendah, khususnya Papua dan NTT.'),
                    ('Pembangunan Sekolah Menengah Atas Terpadu',
                     'Prioritas pembangunan SMA/SMK di kecamatan yang belum terlayani untuk meningkatkan akses pendidikan jenjang menengah.'),
                    ('Program Pengurangan NEET Usia Muda',
                     'Pelatihan vokasional dan kewirausahaan berbasis potensi lokal untuk usia 15–24 tahun yang tidak sekolah dan tidak bekerja.'),
                ],
            },
            {
                'klaster': 'Klaster 2',
                'bg': '#FFFBEB', 'border': '#FCD34D', 'txt': '#92400E',
                'judul': 'Penguatan Kapasitas',
                'items': [
                    ('Peningkatan Kualitas Pembelajaran',
                     'Program peningkatan kompetensi guru dan penyediaan media pembelajaran digital untuk meningkatkan kualitas pendidikan.'),
                    ('Penguatan Koneksi Sekolah-Industri',
                     'Pengembangan SMK berbasis kebutuhan industri lokal untuk meningkatkan serapan lulusan dan mencegah pengangguran muda.'),
                    ('Bantuan Sosial Berbasis Kehadiran Sekolah',
                     'Program conditional cash transfer yang mengaitkan bantuan sosial dengan kehadiran dan prestasi sekolah anak.'),
                ],
            },
            {
                'klaster': 'Klaster 1',
                'bg': '#F0FDF4', 'border': '#86EFAC', 'txt': '#065F46',
                'judul': 'Pengembangan Berkelanjutan',
                'items': [
                    ('Inovasi Pendidikan Berbasis Teknologi',
                     'Akselerasi digitalisasi sekolah, platform pembelajaran adaptif, dan pengembangan kompetensi abad 21.'),
                    ('Peran Sebagai Model dan Transfer Pengetahuan',
                     'Jadikan provinsi resilien sebagai laboratorium praktik baik pendidikan yang dapat direplikasi ke daerah lain.'),
                    ('Penguatan Akses Pendidikan Tinggi',
                     'Program transisi SMA ke perguruan tinggi melalui beasiswa meritokrasi untuk mempertahankan capaian pendidikan.'),
                ],
            },
        ]
        for rec in recs:
            st.markdown(f"""
            <div class="card" style="background:{rec['bg']};border-color:{rec['border']};margin-bottom:1.2rem;">
                <div style="margin-bottom:0.8rem;">
                    <strong style="color:{rec['txt']};font-size:1rem;">{rec['klaster']}</strong>
                    <span style="font-size:0.85rem;color:{rec['txt']};margin-left:0.5rem;">— {rec['judul']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"Lihat {len(rec['items'])} rekomendasi untuk {rec['klaster']}"):
                for title_r, desc_r in rec['items']:
                    st.markdown(f"**{title_r}**")
                    st.write(desc_r)
                    st.markdown("---")
