CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --navy:   #0B1F3A;
    --teal:   #0E7B6C;
    --sky:    #4CB8C4;
    --cream:  #F5F4F0;
    --white:  #FFFFFF;
    --muted:  #6B7A8D;
    --border: #DDE3EA;
    --red:    #C0392B;
    --yellow: #D4850A;
    --green:  #1A7F4B;
    --shadow: 0 2px 14px rgba(11,31,58,0.09);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--navy);
    background: var(--cream) !important;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 7px 10px;
    border-radius: 7px;
    transition: background 0.18s;
    cursor: pointer;
    display: block;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
}

/* main */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

/* hero */
.hero {
    background: linear-gradient(135deg, #0B1F3A 0%, #0E3D5A 55%, #0E7B6C 100%);
    border-radius: 18px;
    padding: 3rem 3rem 2.5rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(76,184,196,0.10);
}
.hero-badge {
    display: inline-block;
    background: rgba(76,184,196,0.18);
    border: 1px solid rgba(76,184,196,0.35);
    color: #4CB8C4 !important;
    padding: 3px 13px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #FFFFFF !important;
    line-height: 1.15;
    margin: 0 0 0.5rem;
}
.hero-title span { color: #4CB8C4 !important; }
.hero-sub {
    font-size: 1rem;
    color: #94A3B8 !important;
    max-width: 660px;
    line-height: 1.7;
    margin-bottom: 1.4rem;
}
.hero-quote {
    background: rgba(255,255,255,0.05);
    border-left: 3px solid #4CB8C4;
    padding: 0.9rem 1.3rem;
    border-radius: 0 8px 8px 0;
    color: #CBD5E1 !important;
    font-style: italic;
    font-size: 0.92rem;
    max-width: 700px;
}

/* section header */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 2rem 0 1.1rem;
    padding-bottom: 0.7rem;
    border-bottom: 2px solid var(--border);
}
.sec-pill {
    width: 5px; height: 28px;
    background: linear-gradient(180deg, #0E7B6C, #4CB8C4);
    border-radius: 3px; flex-shrink: 0;
}
.sec-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.45rem;
    color: var(--navy);
    margin: 0;
}
.sec-sub { font-size: 0.84rem; color: var(--muted); margin: 0.15rem 0 0; }

/* cards */
.card {
    background: var(--white);
    border-radius: 12px;
    padding: 1.3rem 1.4rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    height: 100%;
}
.card-accent { border-top: 4px solid var(--teal); }

/* metric cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.9rem;
    margin: 1.4rem 0;
}
.metric-card {
    background: var(--white);
    border-radius: 12px;
    padding: 1.2rem 1.1rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}
.m-val {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--navy);
    line-height: 1;
    margin-bottom: 0.25rem;
}
.m-label {
    font-size: 0.78rem;
    color: var(--muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* cluster badges */
.badge-k1 { display:inline-block; background:#D1FAE5; color:#065F46;
             padding:3px 11px; border-radius:20px; font-size:0.77rem; font-weight:700; }
.badge-k2 { display:inline-block; background:#FEF3C7; color:#92400E;
             padding:3px 11px; border-radius:20px; font-size:0.77rem; font-weight:700; }
.badge-k3 { display:inline-block; background:#FEE2E2; color:#991B1B;
             padding:3px 11px; border-radius:20px; font-size:0.77rem; font-weight:700; }

/* risk badges */
.badge-rendah { display:inline-block; background:#D1FAE5; color:#065F46;
                padding:4px 14px; border-radius:20px; font-size:0.85rem; font-weight:700; }
.badge-tinggi { display:inline-block; background:#FEE2E2; color:#991B1B;
                padding:4px 14px; border-radius:20px; font-size:0.85rem; font-weight:700; }

/* insight box */
.insight {
    background: linear-gradient(135deg, #EFF8FF, #F0FDF4);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    border-left: 4px solid var(--teal);
    margin: 0.9rem 0;
    font-size: 0.91rem;
    color: #1E3A5F;
    line-height: 1.65;
}

/* result box */
.result-box {
    background: var(--white);
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    margin-top: 1rem;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--white);
    border-radius: 9px;
    padding: 3px;
    border: 1px solid var(--border);
    gap: 3px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.86rem;
    color: var(--muted);
    padding: 7px 15px;
}
.stTabs [aria-selected="true"] {
    background: var(--navy) !important;
    color: white !important;
}

/* buttons */
.stButton > button {
    background: var(--teal) !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.3rem !important;
    letter-spacing: 0.02em !important;
    font-family: 'Inter', sans-serif !important;
    transition: background 0.18s !important;
}
.stButton > button:hover { background: var(--navy) !important; }

/* dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden;
    border: 1px solid var(--border) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
</style>
"""


def hero(badge, title, accent, sub, quote=""):
    q = f'<div class="hero-quote">{quote}</div>' if quote else ''
    return f"""
    <div class="hero">
        <div class="hero-badge">{badge}</div>
        <h1 class="hero-title">{title} <span>{accent}</span></h1>
        <p class="hero-sub">{sub}</p>
        {q}
    </div>"""


def sec(title, sub=""):
    s = f'<p class="sec-sub">{sub}</p>' if sub else ''
    return f"""
    <div class="sec-header">
        <div class="sec-pill"></div>
        <div><h2 class="sec-title">{title}</h2>{s}</div>
    </div>"""


def metric_row(*items):
    cards = ''.join(
        f'<div class="metric-card"><div class="m-val">{v}</div><div class="m-label">{l}</div></div>'
        for v, l in items
    )
    return f'<div class="metric-row">{cards}</div>'


def cluster_badge(label):
    m = {'Klaster 1': 'badge-k1', 'Klaster 2': 'badge-k2', 'Klaster 3': 'badge-k3'}
    cls = m.get(label, 'badge-k2')
    return f'<span class="{cls}">{label}</span>'


def insight(text):
    return f'<div class="insight">{text}</div>'


def risk_badge(label):
    cls = 'badge-rendah' if label == 'Rendah' else 'badge-tinggi'
    return f'<span class="{cls}">Risiko {label}</span>'
