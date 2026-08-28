from html import escape

import streamlit as st

from src.i18n import tr


INK = "#142138"
VIOLET = "#5b45f5"
TEAL = "#0f9488"
ORANGE = "#c96a08"


def apply_style():
    navigation_label = tr("NAVEGACIÓN", "NAVIGATION")
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {{ --ink:{INK}; --violet:{VIOLET}; --teal:{TEAL}; --orange:{ORANGE}; --muted:#687386; --line:#dce2ec; --canvas:#f3f5f9; }}
        html, body, [class*="css"] {{ font-family:"Inter",sans-serif; }}
        .stApp {{ background:var(--canvas); color:var(--ink); }}
        [data-testid="stHeader"] {{ background:transparent; height:0; }}
        [data-testid="stToolbar"] {{ top:.45rem; }}
        .block-container {{ padding:1.15rem 2.15rem 3rem; max-width:1440px; }}
        section[data-testid="stSidebar"] {{ background:#101d32; border-right:0; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ display:flex; flex-direction:column; padding-top:1.15rem; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{ display:flex; flex:1; flex-direction:column; padding-bottom:1rem; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {{ display:flex; flex:1; flex-direction:column; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {{ flex:1; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.sidebar-contact-footer) {{ margin-top:auto; }}
        section[data-testid="stSidebar"] * {{ color:#dbe4f1; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {{ content:"{navigation_label}"; display:block; padding:.35rem 1.45rem .5rem; color:#718099; font-size:.62rem; font-weight:700; letter-spacing:.1em; }}
        section[data-testid="stSidebar"] a {{ border-radius:7px; margin:.15rem .65rem; padding-left:.8rem; }}
        section[data-testid="stSidebar"] a:hover {{ background:#1a2a45; }}
        section[data-testid="stSidebar"] a[aria-current="page"] {{ background:#2a3b5b; }}
        section[data-testid="stSidebar"] a[aria-current="page"] * {{ color:white; font-weight:700; }}
        .sidebar-contact-footer {{ position:static; margin:1.35rem .65rem .2rem; padding:.72rem .15rem 0; border-top:1px solid #2b3b54; background:transparent; }}
        .sidebar-contact-title {{ margin:0 0 .58rem; color:#7f8da3 !important; font-size:.62rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }}
        .sidebar-contact-list {{ display:flex; flex-direction:column; gap:.58rem; }}
        .sidebar-contact-item {{ display:flex; flex-direction:column; gap:.12rem; min-width:0; }}
        .sidebar-contact-item > span:first-child {{ color:#95a2b5 !important; font-size:.62rem; font-weight:750; line-height:1.25; }}
        section[data-testid="stSidebar"] .sidebar-contact-address {{ display:block; margin:0 !important; padding:0 !important; border-radius:0; background:transparent !important; color:#d0d8e5 !important; font-size:.65rem; font-weight:500; line-height:1.35; overflow-wrap:anywhere; text-decoration:none; }}
        section[data-testid="stSidebar"] a.sidebar-contact-address:hover {{ color:#ffffff !important; text-decoration:underline; }}
        .sidebar-contact-address-pending {{ color:#68778e !important; opacity:.72; cursor:default; }}
        [data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="collapsedControl"] button {{
            background:#101d32 !important;
            border:1px solid #101d32 !important;
            border-radius:8px !important;
            box-shadow:0 3px 10px rgba(16,29,50,.34) !important;
            color:#ffffff !important;
            opacity:1 !important;
        }}
        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stExpandSidebarButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover,
        [data-testid="collapsedControl"] button:hover {{
            background:#5b45f5 !important;
            border-color:#5b45f5 !important;
            box-shadow:0 4px 12px rgba(91,69,245,.32) !important;
        }}
        [data-testid="stExpandSidebarButton"]:focus-visible,
        [data-testid="stExpandSidebarButton"] button:focus-visible {{
            outline:3px solid rgba(91,69,245,.28) !important;
            outline-offset:2px !important;
        }}
        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="stExpandSidebarButton"] svg *,
        [data-testid="stSidebarCollapsedControl"] button svg,
        [data-testid="collapsedControl"] button svg {{
            color:#ffffff !important;
            fill:#ffffff !important;
            stroke:#ffffff !important;
            opacity:1 !important;
        }}
        .hero {{ background:#101d32; padding:1rem 1.35rem; color:white; margin:-1.15rem -2.15rem 1.45rem; min-height:62px; display:flex; align-items:center; justify-content:space-between; gap:1.5rem; }}
        .hero-copy {{ min-width:0; }}
        .hero h1 {{ margin:0; font-size:1.05rem; line-height:1.25; font-weight:800; letter-spacing:-.02em; color:white; }}
        .hero p {{ margin:.24rem 0 0; color:#aebbd0; font-size:.7rem; line-height:1.35; }}
        .hero-tag {{ color:#9aa9c1; font-size:.68rem; white-space:nowrap; }}
        .page-heading {{ margin:.1rem 0 .85rem; }}
        .page-heading h1 {{ margin:0; color:var(--ink); font-size:1.5rem; line-height:1.2; font-weight:800; letter-spacing:-.025em; }}
        .page-heading p {{ margin:.28rem 0 0; color:#687386; font-size:.75rem; line-height:1.4; }}
        .client-selector-label {{ margin-bottom:.35rem; color:#687386; font-size:.67rem; font-weight:700; text-transform:uppercase; letter-spacing:.045em; }}
        h1,h2,h3 {{ color:var(--ink); font-weight:800 !important; letter-spacing:-.02em; line-height:1.25 !important; }}
        h1 {{ font-size:1.5rem !important; margin:0 0 .4rem !important; }}
        h2 {{ font-size:1.05rem !important; margin:1.2rem 0 .5rem !important; }}
        h3 {{ font-size:.95rem !important; margin:1rem 0 .4rem !important; }}
        h1 + div p, h2 + div p, h3 + div p {{ color:#687386; font-size:.75rem; }}
        p,li,label {{ color:#3f4a5e; }}
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label,
        [data-testid="stTextInput"] label,
        [data-testid="stNumberInput"] label,
        [data-testid="stDateInput"] label,
        [data-testid="stSlider"] label,
        [data-testid="stRadio"] label,
        [data-testid="stCheckbox"] label {{ color:#2f3a4d !important; font-weight:650 !important; }}
        div[data-baseweb="select"] *,
        div[data-baseweb="input"] *,
        div[data-baseweb="textarea"] *,
        input, textarea {{ color:#202c40 !important; -webkit-text-fill-color:#202c40 !important; opacity:1 !important; }}
        div[data-baseweb="select"] svg,
        div[data-baseweb="input"] svg {{ fill:#465166 !important; color:#465166 !important; }}
        input::placeholder, textarea::placeholder {{ color:#69758a !important; -webkit-text-fill-color:#69758a !important; opacity:1 !important; }}
        [data-testid="stCaptionContainer"] p,
        [data-testid="stMarkdownContainer"] small,
        .stCaption {{ color:#5d697d !important; }}
        [role="radiogroup"] label p,
        [data-baseweb="checkbox"] p {{ color:#354156 !important; }}
        [data-baseweb="tab-list"] button {{ color:#465166 !important; }}
        [data-baseweb="tab-list"] button[aria-selected="true"] {{ color:var(--violet) !important; font-weight:700; }}
        [data-testid="stMetricLabel"] p {{ color:#556176 !important; }}
        [data-testid="stMetricValue"] {{ color:var(--ink) !important; }}
        [data-testid="stAlert"] p {{ color:#2f3a4d !important; }}
        .section-kicker {{ color:var(--violet); font-size:.68rem; font-weight:800; text-transform:uppercase; letter-spacing:.08em; margin-bottom:-.35rem; }}
        .user-context {{ background:#eef0ff; border:1px solid #d9dcff; border-left:4px solid var(--violet); border-radius:8px; padding:.75rem 1rem; margin:.35rem 0 1rem; display:flex; align-items:center; gap:.8rem; }}
        .user-context-label {{ color:#667085; font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }}
        .user-context-value {{ color:var(--ink); font-size:.95rem; font-weight:800; }}
        .user-context-note {{ color:#8a94a6; font-size:.68rem; margin-left:auto; }}
        .card {{ background:white; border:1px solid var(--line); border-radius:8px; padding:1rem 1.05rem; min-height:108px; box-shadow:0 1px 2px rgba(20,33,56,.025); position:relative; overflow:hidden; margin-bottom:.35rem; }}
        .card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px; background:var(--violet); }}
        .accent-violet::after {{ background:#5b45f5; }}
        .accent-teal::after {{ background:#168f83; }}
        .accent-purple::after {{ background:#9948e8; }}
        .accent-orange::after {{ background:#c66205; }}
        .accent-slate::after {{ background:#707b8d; }}
        .soft-violet {{ background:#eef0ff; border-color:#d9dcff; }}
        .card-label {{ font-size:.67rem; color:#687386; text-transform:uppercase; letter-spacing:.045em; font-weight:700; }}
        .card-value {{ font-size:1.38rem; line-height:1.15; font-weight:800; color:var(--ink); margin-top:.42rem; overflow-wrap:anywhere; }}
        .card-note {{ font-size:.72rem; line-height:1.42; color:#7b8597; margin-top:.42rem; }}
        .band-high,.band-mid,.band-low {{ min-height:340px; }}
        .band-products-title {{ margin-top:.9rem; color:var(--ink); font-size:.78rem; font-weight:750; }}
        .band-products {{ margin:.65rem 0 1rem; padding:0; list-style:none; }}
        .band-products li {{ position:relative; margin:.38rem 0; padding:.42rem .55rem .42rem 1.35rem; border:1px solid rgba(20,33,56,.09); border-radius:6px; background:rgba(255,255,255,.58); color:#354156; font-size:.75rem; font-weight:600; line-height:1.3; }}
        .band-products li::before {{ content:""; position:absolute; left:.55rem; top:.72rem; width:5px; height:5px; border-radius:50%; background:currentColor; opacity:.7; }}
        .band-action {{ margin:.7rem 0 0; padding:.62rem .7rem; border:1px solid rgba(20,33,56,.1); border-radius:6px; background:rgba(255,255,255,.62); color:#2f3a4d; font-size:.75rem; line-height:1.4; font-weight:750; }}
        .band-card {{ display:flex; flex-direction:column; }}
        .band-high {{ background:#eaf7f1; border-color:#ccebdd; }} .band-high::after {{ background:#159d68; }}
        .band-mid {{ background:#fff3e6; border-color:#f5dfc7; }} .band-mid::after {{ background:#cb6908; }}
        .band-low {{ background:#eef1f5; border-color:#dce1e8; }} .band-low::after {{ background:#758092; }}
        .flow-step {{ background:white; border:1px solid var(--line); border-radius:8px; padding:.9rem .55rem; text-align:center; font-size:.75rem; font-weight:750; color:var(--ink); min-height:58px; display:flex; align-items:center; justify-content:center; box-shadow:inset 0 -3px 0 var(--violet); }}
        .pipeline-shell {{ margin:.9rem 0 1.5rem; padding:1.05rem; border:1px solid #dce2ec; border-radius:12px; background:linear-gradient(145deg,#fff 0%,#f7f8ff 100%); box-shadow:0 8px 24px rgba(20,33,56,.055); overflow-x:auto; }}
        .pipeline-row {{ display:flex; align-items:stretch; min-width:1040px; }}
        .pipeline-card {{ flex:1; min-width:165px; min-height:116px; padding:.82rem .85rem .78rem; border:1px solid #dfe4ed; border-radius:9px; background:#fff; box-shadow:0 3px 10px rgba(20,33,56,.045); position:relative; overflow:hidden; }}
        .pipeline-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px; background:linear-gradient(90deg,#5b45f5,#9948e8); }}
        .pipeline-card-top {{ display:flex; align-items:center; justify-content:space-between; gap:.45rem; }}
        .pipeline-number {{ display:grid; place-items:center; width:1.75rem; height:1.75rem; border-radius:7px; background:#eef0ff; color:#5542e8; font-size:.66rem; font-weight:850; }}
        .pipeline-family {{ color:#7b8597; font-size:.56rem; font-weight:750; text-transform:uppercase; letter-spacing:.045em; text-align:right; }}
        .pipeline-title {{ margin-top:.72rem; color:var(--ink); font-size:.79rem; font-weight:800; line-height:1.22; }}
        .pipeline-phrase {{ margin-top:.3rem; color:#667287; font-size:.66rem; font-weight:600; line-height:1.32; }}
        .pipeline-arrow {{ flex:0 0 2rem; display:grid; place-items:center; color:#5b45f5; font-size:1.15rem; font-weight:800; }}
        .pipeline-turn {{ height:2.65rem; display:flex; align-items:center; justify-content:flex-end; gap:.55rem; padding-right:4.25rem; color:#687386; }}
        .pipeline-turn span {{ font-size:.61rem; font-weight:750; text-transform:uppercase; letter-spacing:.055em; }}
        .pipeline-turn b {{ display:grid; place-items:center; width:1.55rem; height:1.55rem; border-radius:50%; background:#5b45f5; color:white; font-size:.8rem; }}
        .technique-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:.85rem 0 1.5rem; }}
        .technique-card {{ min-height:150px; padding:1rem 1rem .9rem; border:1px solid #dce2ec; border-top:3px solid var(--tech-color,#5b45f5); border-radius:9px; background:#fff; box-shadow:0 2px 8px rgba(20,33,56,.035); }}
        .technique-role {{ color:var(--tech-color,#5b45f5); font-size:.59rem; font-weight:800; text-transform:uppercase; letter-spacing:.065em; }}
        .technique-title {{ margin-top:.48rem; color:var(--ink); font-size:.82rem; font-weight:800; line-height:1.25; }}
        .technique-card p {{ margin:.5rem 0 0; color:#687386; font-size:.68rem; line-height:1.48; }}
        .feature-component-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin:.85rem 0 1.2rem; }}
        .feature-component-card {{ min-height:170px; padding:1rem 1rem .9rem; border:1px solid #dce2ec; border-radius:10px; background:#fff; box-shadow:0 3px 10px rgba(20,33,56,.035); position:relative; overflow:hidden; }}
        .feature-component-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px; background:var(--component-color,#5b45f5); }}
        .feature-component-top {{ display:flex; align-items:center; justify-content:space-between; gap:.65rem; }}
        .feature-component-number {{ display:grid; place-items:center; width:1.75rem; height:1.75rem; border-radius:7px; background:color-mix(in srgb,var(--component-color,#5b45f5) 11%,white); color:var(--component-color,#5b45f5); font-size:.64rem; font-weight:850; }}
        .feature-component-count {{ padding:.23rem .48rem; border-radius:999px; background:#f0f2f6; color:#657184; font-size:.6rem; font-weight:750; }}
        .feature-component-title {{ margin-top:.72rem; color:var(--ink); font-size:.82rem; font-weight:800; line-height:1.25; }}
        .feature-component-card p {{ margin:.42rem 0 0; color:#687386; font-size:.68rem; line-height:1.45; }}
        .feature-component-keywords {{ margin-top:.72rem; padding-top:.62rem; border-top:1px solid #edf0f4; color:var(--component-color,#5b45f5); font-size:.61rem; line-height:1.35; font-weight:750; }}
        .feature-explorer-intro {{ display:grid; grid-template-columns:minmax(180px,.7fr) minmax(280px,1.3fr); align-items:center; gap:1rem; margin:.55rem 0 .7rem; padding:.82rem 1rem; border:1px solid #dce2ec; border-left:4px solid var(--component-color,#5b45f5); border-radius:8px; background:#fff; }}
        .feature-explorer-intro span {{ display:block; color:#7b8597; font-size:.58rem; font-weight:750; text-transform:uppercase; letter-spacing:.06em; }}
        .feature-explorer-intro strong {{ display:block; margin-top:.18rem; color:var(--ink); font-size:.8rem; }}
        .feature-explorer-intro p {{ margin:0; color:#687386; font-size:.68rem; line-height:1.45; }}
        .feature-explorer-intro p b {{ display:block; margin-top:.18rem; color:var(--component-color,#5b45f5); font-size:.62rem; }}
        .metric-comparison-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin:.85rem 0 1rem; }}
        .metric-comparison-card {{ min-height:190px; padding:1rem 1.05rem; border:1px solid #dce2ec; border-radius:10px; background:#fff; box-shadow:0 4px 12px rgba(20,33,56,.04); position:relative; overflow:hidden; }}
        .metric-comparison-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:4px; background:var(--metric-color,#5b45f5); }}
        .metric-comparison-top {{ display:flex; align-items:center; justify-content:space-between; gap:.5rem; color:#687386; font-size:.64rem; font-weight:800; text-transform:uppercase; letter-spacing:.045em; }}
        .metric-comparison-top b {{ padding:.28rem .5rem; border-radius:999px; background:#e9f7f1; color:#087d55; font-size:.61rem; letter-spacing:0; text-transform:none; white-space:nowrap; }}
        .metric-comparison-value {{ margin-top:.7rem; color:var(--ink); font-size:1.75rem; line-height:1; font-weight:850; letter-spacing:-.035em; }}
        .metric-comparison-baseline {{ display:flex; align-items:center; justify-content:space-between; gap:.5rem; margin-top:.68rem; padding:.48rem .55rem; border-radius:6px; background:#f3f5f8; color:#687386; font-size:.64rem; }}
        .metric-comparison-baseline strong {{ color:var(--metric-color,#5b45f5); }}
        .metric-comparison-card p {{ margin:.65rem 0 0; color:#687386; font-size:.68rem; line-height:1.45; }}
        .metric-success-callout {{ display:flex; align-items:flex-start; gap:.85rem; margin:.8rem 0 1.35rem; padding:1rem 1.1rem; border:1px solid #bfe8d4; border-radius:10px; background:#eaf8f1; }}
        .metric-success-icon {{ flex:0 0 2rem; display:grid; place-items:center; width:2rem; height:2rem; border-radius:8px; background:#159d68; color:#fff; font-size:1rem; font-weight:850; }}
        .metric-success-callout span {{ display:block; color:#087d55; font-size:.59rem; font-weight:850; text-transform:uppercase; letter-spacing:.06em; }}
        .metric-success-callout strong {{ display:block; margin-top:.22rem; color:var(--ink); font-size:.82rem; }}
        .metric-success-callout p {{ margin:.32rem 0 0; color:#426456; font-size:.69rem; line-height:1.45; }}
        .baseline-card {{ min-height:220px; padding:1.1rem; border:1px solid #d7dcff; border-radius:10px; background:linear-gradient(145deg,#eef0ff,#f8f8ff); position:relative; overflow:hidden; }}
        .baseline-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:4px; background:#5b45f5; }}
        .baseline-kicker {{ color:#5542e8; font-size:.61rem; font-weight:850; text-transform:uppercase; letter-spacing:.06em; }}
        .baseline-title {{ margin-top:.55rem; color:var(--ink); font-size:1.02rem; line-height:1.2; font-weight:850; }}
        .baseline-card p {{ margin:.6rem 0 0; color:#596579; font-size:.7rem; line-height:1.5; }}
        .baseline-rule {{ display:inline-block; margin-top:.85rem; padding:.32rem .55rem; border-radius:999px; background:#fff; border:1px solid #d7dcff; color:#5542e8; font-size:.62rem; font-weight:800; }}
        .baseline-card-history {{ background:linear-gradient(145deg,#eaf8f5,#f7fbfa); border-color:#c8e8e2; }}
        .baseline-card-history::after {{ background:#168f83; }}
        .baseline-card-history .baseline-kicker {{ color:#087e76; }}
        .baseline-card-history .baseline-rule {{ border-color:#c8e8e2; color:#087e76; }}
        .baseline-pending {{ margin-top:.7rem; color:#9d5204; font-size:.61rem; font-weight:750; }}
        .baseline-explanation {{ min-height:220px; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.65rem; }}
        .baseline-explanation-wide {{ min-height:0; margin:.75rem 0 1.2rem; grid-template-columns:repeat(4,minmax(0,1fr)); }}
        .baseline-explanation > div {{ display:flex; gap:.65rem; padding:.78rem .82rem; border:1px solid #dce2ec; border-radius:8px; background:#fff; }}
        .baseline-explanation span {{ flex:0 0 1.6rem; display:grid; place-items:center; width:1.6rem; height:1.6rem; border-radius:6px; background:#f0f2f6; color:#5b45f5; font-size:.6rem; font-weight:850; }}
        .baseline-explanation p {{ margin:0; color:#687386; font-size:.65rem; line-height:1.42; }}
        .baseline-explanation p b {{ display:block; margin-bottom:.18rem; color:var(--ink); font-size:.69rem; }}
        .metric-definition-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin:.8rem 0 1.4rem; }}
        .metric-definition-card {{ min-height:270px; padding:1.05rem; border:1px solid #dce2ec; border-top:4px solid var(--metric-color,#5b45f5); border-radius:9px; background:#fff; }}
        .metric-definition-name {{ color:var(--metric-color,#5b45f5); font-size:.65rem; font-weight:850; text-transform:uppercase; letter-spacing:.055em; }}
        .metric-definition-question {{ margin-top:.52rem; color:var(--ink); font-size:.88rem; font-weight:850; line-height:1.3; }}
        .metric-definition-formula {{ margin-top:.58rem; padding:.5rem .58rem; border-radius:6px; background:#f3f5f8; color:#596579; font-size:.63rem; font-weight:700; line-height:1.4; }}
        .metric-definition-card p {{ margin:.75rem 0 0; color:#687386; font-size:.68rem; line-height:1.48; }}
        .metric-definition-card p b {{ color:#354156; }}
        .metric-caveat {{ margin:1rem 0 .25rem; padding:.8rem .9rem; border-left:4px solid #c66205; border-radius:0 7px 7px 0; background:#fff3e6; color:#65513b; font-size:.68rem; line-height:1.5; }}
        .metric-caveat strong {{ color:#9d5204; }}
        .decile-summary-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.7rem; margin:.8rem 0; }}
        .decile-summary-card {{ min-height:125px; padding:.85rem .9rem; border:1px solid #dce2ec; border-radius:9px; background:#fff; position:relative; overflow:hidden; }}
        .decile-summary-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px; background:var(--decile-color,#5b45f5); }}
        .decile-summary-card span {{ display:block; color:#687386; font-size:.59rem; font-weight:800; text-transform:uppercase; letter-spacing:.05em; }}
        .decile-summary-card strong {{ display:block; margin-top:.42rem; color:var(--ink); font-size:1.28rem; line-height:1; font-weight:850; }}
        .decile-summary-card p {{ margin:.45rem 0 0; color:#7b8597; font-size:.64rem; line-height:1.4; }}
        .decile-reading {{ margin:.75rem 0 .85rem; padding:.78rem .9rem; border-left:4px solid #5b45f5; border-radius:0 7px 7px 0; background:#eef0ff; color:#4f5b70; font-size:.69rem; line-height:1.52; }}
        .decile-reading strong {{ color:#3226a8; }}
        .light-table-wrap {{ width:100%; margin:.75rem 0 1rem; border:1px solid #dce2ec; border-radius:9px; background:#fff; overflow-x:auto; box-shadow:0 2px 8px rgba(20,33,56,.035); }}
        .light-table {{ width:100%; border-collapse:collapse; color:#354156; font-size:.67rem; white-space:nowrap; }}
        .light-table thead th {{ padding:.66rem .72rem; border-bottom:1px solid #dce2ec; background:#eef0ff; color:#263247; text-align:left; font-size:.63rem; font-weight:800; letter-spacing:.015em; }}
        .light-table tbody td {{ padding:.58rem .72rem; border-bottom:1px solid #edf0f4; background:#fff; color:#465166; font-variant-numeric:tabular-nums; }}
        .light-table tbody tr:nth-child(even) td {{ background:#f8f9fb; }}
        .light-table tbody tr:hover td {{ background:#f0f2ff; }}
        .light-table tbody tr:last-child td {{ border-bottom:0; }}
        .light-table td:first-child {{ color:var(--ink); font-weight:750; }}
        .light-table .table-emphasis {{ color:#5542e8; font-weight:800; }}
        .project-link-banner {{ display:flex; align-items:center; justify-content:space-between; gap:1.2rem; margin:.35rem 0 1.15rem; padding:.85rem 1rem; border:1px solid #dce2ec; border-left:4px solid #5b45f5; border-radius:8px; background:#fff; box-shadow:0 2px 8px rgba(20,33,56,.03); }}
        .project-link-banner span {{ display:block; color:#687386; font-size:.57rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }}
        .project-link-banner strong {{ display:block; margin-top:.18rem; color:var(--ink); font-size:.78rem; }}
        .project-link-banner p {{ margin:.2rem 0 0; color:#758092; font-size:.65rem; line-height:1.35; }}
        .project-link-banner a {{ flex:0 0 auto; padding:.55rem .78rem; border-radius:7px; background:#5b45f5; color:#fff !important; font-size:.67rem; font-weight:800; text-decoration:none; }}
        .project-link-banner a:hover {{ background:#4935df; color:#fff !important; }}
        .project-link-dataset {{ border-left-color:#168f83; }}
        .project-link-dataset a {{ background:#168f83; }}
        .project-link-dataset a:hover {{ background:#087e76; }}
        .project-link-github {{ border-left-color:#263750; }}
        .project-link-github a {{ background:#263750; }}
        .project-link-github a:hover {{ background:#101d32; }}
        .project-link-pending {{ background:#f8f9fb; }}
        .project-link-status {{ flex:0 0 auto; padding:.4rem .58rem; border-radius:999px; background:#edf0f4; color:#687386 !important; text-transform:none !important; letter-spacing:0 !important; }}
        .insight-card {{ background:#eaf2ff; border:1px solid #c9daf3; border-radius:9px; padding:1.05rem 1.1rem 1rem; min-height:0; }}
        .insight-card h3 {{ margin:0 0 .85rem !important; color:var(--ink); font-size:1rem !important; }}
        .insight-card ul {{ margin:0; padding:0; list-style:none; }}
        .insight-card li {{ position:relative; margin:.78rem 0; padding-left:1.2rem; color:#354156; font-size:.76rem; line-height:1.35; }}
        .insight-card li::before {{ content:""; position:absolute; left:0; top:.3rem; width:8px; height:8px; border-radius:50%; background:var(--violet); }}
        .insight-card-note {{ margin-top:1rem; padding-top:.8rem; border-top:1px solid #c9daf3; color:#087e7a; font-size:.71rem; line-height:1.4; font-weight:750; }}
        .section-gap {{ height:.8rem; }}
        .decision-callout {{ margin:.9rem 0 .25rem; padding:.9rem 1rem; border:1px solid #d5d8ff; border-radius:8px; background:#eef0ff; color:#5542e8; font-size:.75rem; line-height:1.4; font-weight:750; }}
        div[data-testid="stMetric"], [data-testid="stExpander"] {{ background:white; border:1px solid var(--line); border-radius:8px; }}
        [data-testid="stExpander"] details summary {{ font-weight:700; color:var(--ink); }}
        [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {{ background:white; border:1px solid var(--line); border-radius:8px; padding:.45rem; overflow:hidden; }}
        .ranking-heading {{ display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin:1.2rem 0 .45rem; }}
        .ranking-heading h2 {{ margin:0 !important; }}
        .ranking-heading span {{ color:#687386; font-size:.7rem; }}
        .ranking-table-wrap {{ border:1px solid #dce2ec; border-radius:8px; overflow:hidden; background:white; box-shadow:0 1px 2px rgba(20,33,56,.03); }}
        .ranking-table {{ width:100%; border-collapse:collapse; table-layout:fixed; font-size:.7rem; }}
        .ranking-table thead th {{ background:#101d32; color:#fff; padding:.62rem .7rem; text-align:left; font-size:.67rem; font-weight:750; letter-spacing:.01em; }}
        .ranking-table thead th:first-child {{ text-align:center; }}
        .ranking-table tbody tr:nth-child(even) {{ background:#f7f8fb; }}
        .ranking-table tbody tr:hover {{ background:#eef0ff; }}
        .ranking-table td {{ padding:.36rem .7rem; border-bottom:1px solid #edf0f4; color:#354156; vertical-align:middle; line-height:1.2; }}
        .ranking-table tbody tr:last-child td {{ border-bottom:0; }}
        .ranking-rank {{ text-align:center; color:#758092 !important; }}
        .ranking-product {{ color:var(--ink) !important; font-weight:700; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
        .ranking-origin {{ color:#687386 !important; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
        .propensity-cell {{ display:flex; align-items:center; gap:.48rem; }}
        .propensity-track {{ flex:1; height:9px; min-width:70px; border-radius:999px; background:#e8ebf0; overflow:hidden; }}
        .propensity-fill {{ display:block; height:100%; border-radius:999px; background:#5b45f5; }}
        .propensity-value {{ min-width:2rem; color:#263247; font-variant-numeric:tabular-nums; }}
        .band-pill {{ display:inline-block; min-width:3.2rem; padding:.3rem .55rem; border-radius:999px; text-align:center; font-size:.68rem; font-weight:750; }}
        .band-pill.alta {{ background:#e2f7ed; color:#09865b; }}
        .band-pill.media {{ background:#fff0df; color:#b45b00; }}
        .band-pill.baja {{ background:#edf0f4; color:#697586; }}
        .factor-link {{ color:#5542e8 !important; font-weight:700; text-decoration:none; white-space:nowrap; }}
        .factor-link:hover {{ color:#3e2dcc !important; text-decoration:underline; }}
        .factor-detail-card {{ background:white; border:1px solid var(--line); border-radius:9px; padding:1.15rem 1.2rem; min-height:355px; position:relative; overflow:hidden; margin-bottom:.75rem; }}
        .factor-detail-card::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px; background:var(--factor-color,#5b45f5); }}
        .factor-detail-title {{ color:var(--ink); font-size:1rem; font-weight:800; line-height:1.25; }}
        .factor-detail-intro {{ margin:.45rem 0 .9rem; color:#687386; font-size:.75rem; line-height:1.45; }}
        .factor-metrics {{ margin:0; padding:0; list-style:none; }}
        .factor-metric {{ display:grid; grid-template-columns:minmax(8.5rem,1fr) auto; gap:.25rem .75rem; padding:.58rem 0; border-top:1px solid #edf0f4; }}
        .factor-metric-name {{ color:#465166; font-size:.72rem; font-weight:750; }}
        .factor-metric-value {{ color:var(--ink); font-size:.75rem; font-weight:800; text-align:right; font-variant-numeric:tabular-nums; }}
        .factor-metric-description {{ grid-column:1/-1; color:#7a8597; font-size:.68rem; line-height:1.4; }}
        .factor-metric-range {{ grid-column:1/-1; width:max-content; margin-top:.12rem; padding:.2rem .42rem; border-radius:5px; background:#f0f2f6; color:#596579; font-size:.64rem; font-weight:700; }}
        .factor-conclusion {{ margin-top:.9rem; padding:.65rem .75rem; border-radius:7px; font-size:.72rem; line-height:1.4; font-weight:750; }}
        .factor-conclusion.fuerte {{ background:#e5f7ee; border:1px solid #bfe8d4; color:#087d55; }}
        .factor-conclusion.media {{ background:#fff1df; border:1px solid #f2d4ad; color:#aa5700; }}
        .factor-conclusion.debil {{ background:#edf0f4; border:1px solid #d9dee6; color:#657184; }}
        .chart-intro {{ margin:-.12rem 0 .75rem; color:#687386; font-size:.75rem; line-height:1.5; max-width:850px; }}
        .chart-reading {{ margin:.65rem 0 .2rem; padding:.72rem .85rem; border-left:4px solid var(--violet); border-radius:0 7px 7px 0; background:#eef0ff; color:#465166; font-size:.72rem; line-height:1.5; }}
        .chart-reading strong {{ color:var(--ink); }}
        div[data-baseweb="select"] > div, div[data-testid="stTextInput"] input, div[data-baseweb="input"] {{ border-color:#c7cfdb; border-radius:7px; background:white; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{ background:white; border-color:var(--line) !important; border-radius:8px !important; box-shadow:inset 0 -3px 0 #5b45f5; }}
        .stButton > button {{ border-radius:7px; border:1px solid var(--violet); background:var(--violet); color:white; font-weight:700; min-height:2.6rem; }}
        .stButton > button:hover {{ background:#4935df; border-color:#4935df; color:white; }}
        .stDownloadButton {{ display:flex; justify-content:center; }}
        .stDownloadButton > button {{ width:auto !important; min-width:16rem; min-height:2.55rem; padding:.55rem 1.15rem; border-radius:7px; border:1px solid #263750; background:#142138; color:#fff !important; box-shadow:0 1px 3px rgba(20,33,56,.14); font-weight:700; }}
        .stDownloadButton > button p, .stDownloadButton > button span {{ color:#fff !important; opacity:1 !important; }}
        .stDownloadButton > button:hover {{ background:#263750; border-color:#263750; color:#fff !important; box-shadow:0 2px 6px rgba(20,33,56,.18); }}
        [data-testid="stAlert"] {{ border-radius:8px; }}
        @media (max-width:1050px) {{ .technique-grid,.feature-component-grid,.metric-comparison-grid,.metric-definition-grid,.decile-summary-grid,.baseline-explanation-wide {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
        @media (max-width:800px) {{ .block-container {{ padding-left:1rem; padding-right:1rem; }} .hero {{ margin-left:-1rem; margin-right:-1rem; }} .hero-tag {{ display:none; }} .ranking-table-wrap {{ overflow-x:auto; }} .ranking-table {{ min-width:760px; }} .ranking-heading {{ align-items:flex-start; flex-direction:column; }} .pipeline-shell {{ padding:.75rem; }} .technique-grid,.feature-component-grid,.metric-comparison-grid,.metric-definition-grid,.baseline-explanation,.decile-summary-grid {{ grid-template-columns:1fr; }} .feature-explorer-intro {{ grid-template-columns:1fr; }} .project-link-banner {{ align-items:flex-start; flex-direction:column; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_footer():
    st.sidebar.markdown(
        f"""
        <div class="sidebar-contact-footer">
          <div class="sidebar-contact-title">{escape(tr('Contacto', 'Contact'))}</div>
          <div class="sidebar-contact-list">
            <div class="sidebar-contact-item">
              <span>Email</span>
              <a class="sidebar-contact-address" href="mailto:fernandomrestelli@gmail.com">fernandomrestelli@gmail.com</a>
            </div>
            <div class="sidebar-contact-item">
              <span>LinkedIn</span>
              <a class="sidebar-contact-address" href="https://www.linkedin.com/in/fernando-m-restelli/" target="_blank" rel="noopener noreferrer">linkedin.com/in/fernando-m-restelli/</a>
            </div>
            <div class="sidebar-contact-item">
              <span>GitHub</span>
              <a class="sidebar-contact-address" href="https://github.com/FernandoMRestelli/instacart-recommender" target="_blank" rel="noopener noreferrer">github.com/FernandoMRestelli/instacart-recommender</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str):
    st.markdown(
        f"<div class='hero'><div class='hero-copy'><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div><div class='hero-tag'>{escape(tr('Aplicar estrategias de activación', 'Apply activation strategies'))}</div></div>",
        unsafe_allow_html=True,
    )


def content_header(title: str, subtitle: str):
    st.markdown(
        f"<div class='page-heading'><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>",
        unsafe_allow_html=True,
    )


def html_card(label: str, value: str, note: str = "", extra_class: str = ""):
    safe_class = " ".join(part for part in extra_class.split() if part.replace("-", "").isalnum())
    st.markdown(
        f"<div class='card {safe_class}'><div class='card-label'>{escape(str(label))}</div><div class='card-value'>{escape(str(value))}</div><div class='card-note'>{escape(str(note))}</div></div>",
        unsafe_allow_html=True,
    )


def band_card(label: str, products: list[str], note: str, extra_class: str):
    safe_class = " ".join(part for part in extra_class.split() if part.replace("-", "").isalnum())
    items = "".join(f"<li>{escape(str(product))}</li>" for product in products)
    if not items:
        items = "<li>Sin productos</li>"
    st.markdown(
        f"""
        <div class='card band-card {safe_class}'>
          <div class='card-label'>{escape(str(label))}</div>
          <div class='card-note band-action'>{escape(str(note))}</div>
          <div class='band-products-title'>{escape(tr('Productos en la banda:', 'Products in this band:'))}</div>
          <ul class='band-products'>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def factor_card(title: str, intro: str, metrics: list[tuple], color: str, conclusion=None):
    metric_rows = ""
    for metric in metrics:
        name, value, description = metric[:3]
        range_text = metric[3] if len(metric) > 3 else ""
        range_html = f"<span class='factor-metric-range'>{escape(str(range_text))}</span>" if range_text else ""
        metric_rows += (
            "<li class='factor-metric'>"
            f"<span class='factor-metric-name'>{escape(str(name))}</span>"
            f"<span class='factor-metric-value'>{escape(str(value))}</span>"
            f"<span class='factor-metric-description'>{escape(str(description))}</span>"
            f"{range_html}</li>"
        )
    conclusion_html = ""
    if conclusion:
        level, text = conclusion
        safe_level = level.lower().replace("é", "e")
        conclusion_html = f"<div class='factor-conclusion {escape(safe_level)}'>{escape(str(text))}</div>"
    st.markdown(
        f"<div class='factor-detail-card' style='--factor-color:{escape(color)}'>"
        f"<div class='factor-detail-title'>{escape(title)}</div>"
        f"<div class='factor-detail-intro'>{escape(intro)}</div>"
        f"<ul class='factor-metrics'>{metric_rows}</ul>"
        f"{conclusion_html}"
        "</div>",
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    fig.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font=dict(family="Inter, sans-serif", color="#465166", size=11), colorway=[VIOLET, TEAL, ORANGE, "#758092"], margin=dict(l=18,r=18,t=24,b=18), legend=dict(title_text="",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    axis_text = dict(color="#465166", size=12)
    axis_title = dict(font=dict(color="#2f3a4d", size=13))
    fig.update_xaxes(
        gridcolor="#e4e8ef",
        linecolor="#b8c1cf",
        tickfont=axis_text,
        title=axis_title,
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor="#e4e8ef",
        linecolor="#b8c1cf",
        tickfont=axis_text,
        title=axis_title,
        zeroline=False,
    )
    return fig
