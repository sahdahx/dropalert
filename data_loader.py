import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import os

FITUR = [
    'gabungan_pendudukmiskin',
    'TPT',
    'NEET_usiamuda',
    'tenagakerjaformal',
    'gabungan_HLS',
    'gabungan_RLS',
    'rasio_guru_SMA',
    'rasio_guru_SMK',
    'rasio_guru_SD',
    'rasio_guru_SMP',
    'rasio_sekolah_SMA',
    'rasio_sekolah_SMK',
    'rasio_sekolah_SD',
    'rasio_sekolah_SMP',
]

FITUR_LABEL = {
    'gabungan_pendudukmiskin': 'Persentase Penduduk Miskin (%)',
    'TPT': 'Tingkat Pengangguran Terbuka (%)',
    'NEET_usiamuda': 'NEET Usia Muda 15-24 Thn (%)',
    'tenagakerjaformal': 'Tenaga Kerja Formal (%)',
    'gabungan_HLS': 'Harapan Lama Sekolah (Tahun)',
    'gabungan_RLS': 'Rata-rata Lama Sekolah (Tahun)',
    'rasio_guru_SMA': 'Rasio Guru/Murid SMA',
    'rasio_guru_SMK': 'Rasio Guru/Murid SMK',
    'rasio_guru_SD': 'Rasio Guru/Murid SD',
    'rasio_guru_SMP': 'Rasio Guru/Murid SMP',
    'rasio_sekolah_SMA': 'Rasio Sekolah/Murid SMA',
    'rasio_sekolah_SMK': 'Rasio Sekolah/Murid SMK',
    'rasio_sekolah_SD': 'Rasio Sekolah/Murid SD',
    'rasio_sekolah_SMP': 'Rasio Sekolah/Murid SMP',
}

TARGETS = {
    'ARPS_07to12': 'Risiko Putus Sekolah Usia 7-12 Thn (SD)',
    'ARPS_13to15': 'Risiko Putus Sekolah Usia 13-15 Thn (SMP)',
    'ARPS_16to18': 'Risiko Putus Sekolah Usia 16-18 Thn (SMA)',
    'ARPS_19to23': 'Risiko Putus Sekolah Usia 19-23 Thn (PT)',
}

CLUSTER_LABEL = {0: 'Klaster 1', 1: 'Klaster 2', 2: 'Klaster 3'}
CLUSTER_COLOR = {
    'Klaster 1': '#1A7F4B',
    'Klaster 2': '#D4850A',
    'Klaster 3': '#C0392B',
}

# Approximate province centroids (lat, lon)
PROV_COORDS = {
    'ACEH': (4.695, 96.749), 'SUMATERA UTARA': (2.115, 99.545),
    'SUMATERA BARAT': (-0.740, 100.800), 'RIAU': (0.293, 101.707),
    'JAMBI': (-1.485, 102.438), 'SUMATERA SELATAN': (-3.319, 104.914),
    'BENGKULU': (-3.793, 102.260), 'LAMPUNG': (-4.559, 105.407),
    'KEP. BANGKA BELITUNG': (-2.741, 106.441), 'KEP. RIAU': (3.946, 108.143),
    'DKI JAKARTA': (-6.209, 106.846), 'JAWA BARAT': (-6.918, 107.619),
    'JAWA TENGAH': (-7.150, 110.140), 'DI YOGYAKARTA': (-7.875, 110.426),
    'JAWA TIMUR': (-7.536, 112.238), 'BANTEN': (-6.406, 106.064),
    'BALI': (-8.410, 115.189), 'NUSA TENGGARA BARAT': (-8.653, 117.362),
    'NUSA TENGGARA TIMUR': (-8.657, 121.079), 'KALIMANTAN BARAT': (0.000, 110.000),
    'KALIMANTAN TENGAH': (-1.681, 113.382), 'KALIMANTAN SELATAN': (-3.093, 115.284),
    'KALIMANTAN TIMUR': (1.641, 116.419), 'KALIMANTAN UTARA': (3.073, 116.041),
    'SULAWESI UTARA': (0.627, 123.975), 'SULAWESI TENGAH': (-1.430, 121.446),
    'SULAWESI SELATAN': (-3.669, 119.974), 'SULAWESI TENGGARA': (-4.145, 122.175),
    'GORONTALO': (0.700, 122.447), 'SULAWESI BARAT': (-2.844, 119.232),
    'MALUKU': (-3.239, 130.145), 'MALUKU UTARA': (1.571, 127.809),
    'PAPUA BARAT DAYA': (-1.336, 132.500), 'PAPUA BARAT': (-1.336, 133.175),
    'PAPUA': (-4.270, 138.080), 'PAPUA SELATAN': (-6.500, 140.000),
    'PAPUA TENGAH': (-4.000, 136.500), 'PAPUA PEGUNUNGAN': (-4.500, 139.500),
}


def load_cluster_data():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cluster_provinsi.csv')
    df = pd.read_csv(path)
    df['Provinsi'] = df['Provinsi'].str.upper().str.strip()
    df['cluster_label'] = df['cluster'].astype(int).map(CLUSTER_LABEL)
    df['lat'] = df['Provinsi'].map(lambda p: PROV_COORDS.get(p, (0, 118))[0])
    df['lon'] = df['Provinsi'].map(lambda p: PROV_COORDS.get(p, (0, 118))[1])
    return df


def build_synthetic_model_data(df_cluster):
    """
    Build a synthetic panel dataset from the cluster CSV for demo predictions.
    The notebook's actual panel data (df_model) is not uploaded, so we
    reconstruct feature statistics per cluster and simulate training data.
    """
    np.random.seed(42)
    rows = []
    # Use province means from the cluster CSV directly as basis
    for _, row in df_cluster.iterrows():
        for year in range(2021, 2026):
            noise = np.random.normal(0, 0.02, len(FITUR))
            feat_vals = {f: float(row[f]) * (1 + noise[i]) for i, f in enumerate(FITUR)}
            # ARPS approximation: higher poverty/NEET/TPT = higher ARPS
            base = (
                float(row['gabungan_pendudukmiskin']) * 0.08
                + float(row['NEET_usiamuda']) * 0.04
                + float(row['TPT']) * 0.02
                - float(row['tenagakerjaformal']) * 0.02
                - float(row['gabungan_HLS']) * 0.15
            )
            feat_vals['Tahun'] = year
            feat_vals['Provinsi'] = row['Provinsi']
            feat_vals['ARPS_07to12'] = max(0.1, min(15, base * 0.3 + np.random.normal(0, 0.3)))
            feat_vals['ARPS_13to15'] = max(0.1, min(20, base * 0.5 + np.random.normal(0, 0.4)))
            feat_vals['ARPS_16to18'] = max(0.5, min(40, base * 1.2 + np.random.normal(0, 0.6)))
            feat_vals['ARPS_19to23'] = max(1.0, min(60, base * 2.5 + np.random.normal(0, 1.0)))
            rows.append(feat_vals)
    return pd.DataFrame(rows)


@staticmethod
def _safe_float(v):
    try:
        return float(v)
    except Exception:
        return np.nan


def train_models(df_model):
    """Train one GradientBoosting model per ARPS target. Returns dict of fitted models + scaler."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler

    df_sorted = df_model.sort_values(['Tahun', 'Provinsi'])
    train = df_sorted[df_sorted['Tahun'] <= 2024]

    X_train = train[FITUR].fillna(train[FITUR].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    fitted = {}
    thresholds = {}
    for target in TARGETS:
        y = train[target]
        m = GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.03,
            max_depth=2, subsample=0.7, random_state=42
        )
        m.fit(X_scaled, y)
        fitted[target] = m
        thresholds[target] = float(y.median())

    return fitted, scaler, thresholds
