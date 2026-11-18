import streamlit as st

import advisor
import db
import html
import logic
import mailer
import weather

DB_PATH = db.DEFAULT_PATH


def friendly_error(error):
    if isinstance(error, ValueError):
        return str(error)
    return "We could not reach the game right now. Please try again in a moment."


def flash(scope, message, kind="success"):
    st.session_state[f"flash_{scope}"] = {"message": message, "kind": kind}


def notice(kind, message):
    icons = {"success": "check", "error": "alert", "info": "info", "warning": "alert"}
    st.markdown(
        f'<div class="notice notice-{kind}"><span class="notice-icon">{icon(icons[kind], 20)}</span>'
        f'<span>{html.escape(str(message))}</span></div>',
        unsafe_allow_html=True,
    )


def show_flash(scope):
    item = st.session_state.pop(f"flash_{scope}", None)
    if not item:
        return
    message = item["message"]
    kind = item.get("kind", "success")
    if kind == "closed_day":
        show_closed_day(message, PLAYER, scope)
    elif kind == "toast":
        st.toast(message)
    elif kind == "error":
        notice("error", message)
    elif kind == "info":
        notice("info", message)
    elif kind == "warning":
        notice("warning", message)
    else:
        notice("success", message)

st.set_page_config(page_title="Campus Tycoon", page_icon=":material/local_cafe:", layout="wide")


ICONS = {
    "coffee": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13v7a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8Z"/><path d="M17 10h1a3 3 0 0 1 0 6h-2M7 3v2m5-2v2m5-2v2"/></svg>',
    "croissant": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8c1-3 4-5 7-5s6 2 7 5l2 8-5 5-4-3-4 3-5-5 2-8Z"/><path d="m5 8 5 5m9-5-5 5m-6 6 3-6m8 6-3-6"/></svg>',
    "droplet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3s-7 7.5-7 12a7 7 0 0 0 14 0c0-4.5-7-12-7-12Z"/><path d="M9 16a3 3 0 0 0 3 3"/></svg>',
    "cart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/><path d="M2 3h2l3 12h12l3-9H5"/></svg>',
    "wallet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 8h18m-5 6h2M6 5V3h12v2"/></svg>',
    "trending-up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 17 6-6 4 4 8-9"/><path d="M15 6h6v6"/></svg>',
    "trophy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8m-4-4v4M7 4h10v6a5 5 0 0 1-10 0V4Z"/><path d="M7 7H4v2a4 4 0 0 0 4 4m9-6h3v2a4 4 0 0 1-4 4"/></svg>',
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2H3Zm13-9a3 3 0 1 0 0-6m1 9a5 5 0 0 1 4 5v1h-3"/></svg>',
    "cloud-rain": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 15a5 5 0 1 1 1-9.9A7 7 0 0 1 21 9a4 4 0 0 1-1 6"/><path d="m8 17-1 3m6-3-1 3m6-3-1 3"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "cloud-sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17a5 5 0 1 1 1-9.9A7 7 0 0 1 21 11a4 4 0 0 1-1 6H7Z"/><path d="M12 2v2m-5 .2 1.4 1.4M3 10h2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>',
    "alert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 2.6 17.2A2 2 0 0 0 4.3 20h15.4a2 2 0 0 0 1.7-2.8L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/></svg>',
    "info": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="M3 8v9l9 5 9-5V8m-9 5v9"/></svg>',
}


def icon(name, size=22):
    svg = ICONS.get(name, ICONS["box"])
    return f'<span class="app-icon" style="width:{size}px;height:{size}px">{svg}</span>'


PRODUCT_ICONS = {"Café": "coffee", "Croissant": "croissant", "Water": "droplet"}


def section_heading(icon_name, text):
    st.markdown(
        f'<div class="section-heading">{icon(icon_name)} {html.escape(str(text))}</div>',
        unsafe_allow_html=True,
    )


def product_card(name, stats, footer, key=None):
    stat_html = "".join(
        f'<div class="stat-box"><div class="stat-label">{html.escape(str(label))}</div>'
        f'<div class="stat-value">{html.escape(str(value))}</div></div>'
        for label, value in stats
    )
    with st.container(border=True, key=key or f"product_card_{name}"):
        st.markdown(
            f'{icon(PRODUCT_ICONS.get(name, "box"))} {html.escape(str(name))}',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="stat-grid">{stat_html}</div>', unsafe_allow_html=True)
        if footer:
            st.caption(footer)


def inject_css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root { --bg1:#2A1A12; --glow1:#7A3B16; --glow2:#C2410C; --amber:#F5A524; --orange:#FF7A18; --text:#F6EBDD; --muted:#C9B8A6; --card:rgba(255,255,255,0.06); --card-border:rgba(255,255,255,0.10); --good:#4ADE80; --bad:#F87171; }
html { font-size:15px; }
html, body, [class*="css"] { font-family:'Plus Jakarta Sans', sans-serif; }
.stApp { background: radial-gradient(circle at 8% 7%, rgba(245,165,36,.55) 0, transparent 30%), radial-gradient(circle at 92% 24%, rgba(255,122,24,.45) 0, transparent 27%), radial-gradient(circle at 8% 88%, rgba(194,65,12,.45) 0, transparent 32%), radial-gradient(circle at 88% 82%, rgba(94,234,212,.18) 0, transparent 22%), radial-gradient(circle at 52% 14%, rgba(255,236,210,.12) 0, transparent 24%), linear-gradient(180deg, #43291C 0%, #2A1A12 52%, #20130D 100%); background-attachment:fixed; color:var(--text); }
[data-testid="stHeader"], [data-testid="stToolbar"] { background:transparent; }
[data-testid="stMainBlockContainer"] { max-width:1180px; margin:0 auto; padding:2rem 2rem 4rem; }
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stExpander"] { background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(255,255,255,.05)); -webkit-backdrop-filter:blur(18px) saturate(140%); backdrop-filter:blur(18px) saturate(140%); border:1px solid rgba(255,255,255,.18); border-radius:22px; box-shadow:inset 0 1px 0 rgba(255,255,255,.28),inset 0 -1px 0 rgba(255,255,255,.04),0 12px 32px rgba(0,0,0,.30); transition:transform .2s ease,background .2s ease,border-color .2s ease; }
[data-testid="stMetric"] { padding:16px; }
[data-testid="stMetricLabel"] { font-size:.8rem !important; }
[data-testid="stMetricValue"] { font-size:1.7rem !important; }
[data-testid="stMetric"]:hover, [data-testid="stVerticalBlockBorderWrapper"]:hover, [data-testid="stExpander"]:hover { transform:translateY(-2px); background:linear-gradient(135deg,rgba(255,255,255,.21),rgba(255,255,255,.08)); border-color:rgba(245,165,36,.45); }
.stButton button, .stDownloadButton button { border-radius:14px; font-weight:700; transition:all .2s ease; }
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background:linear-gradient(135deg,var(--amber),var(--orange)); border:0; color:#2B1608; }
.stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover { box-shadow:0 0 24px rgba(245,165,36,.35); }
.stButton button:not([kind="primary"]), .stDownloadButton button:not([kind="primary"]) { background:rgba(255,255,255,.08); border:1px solid rgba(245,165,36,.55); color:var(--text); border-radius:14px; font-weight:600; }
.stButton button:not([kind="primary"]):hover, .stDownloadButton button:not([kind="primary"]):hover { background:linear-gradient(135deg,rgba(245,165,36,.20),rgba(255,122,24,.20)); border-color:var(--amber); color:var(--text); transform:translateY(-1px); box-shadow:0 0 18px rgba(245,165,36,.22); }
[class*="st-key-tournament_close_"] button { background:rgba(248,113,113,.12) !important; border-color:rgba(248,113,113,.6) !important; color:#FCA5A5 !important; }
[class*="st-key-tournament_close_"] button span, [class*="st-key-tournament_close_"] button svg { color:#FCA5A5 !important; fill:#FCA5A5 !important; }
[class*="st-key-tournament_close_"] button:hover { background:rgba(248,113,113,.24) !important; border-color:#F87171 !important; box-shadow:0 0 18px rgba(248,113,113,.28) !important; }
[class*="st-key-tournament_upgrade_"] button { border-color:rgba(245,165,36,.7) !important; box-shadow:0 0 10px rgba(245,165,36,.16); }
[class*="st-key-tournament_upgrade_"] button:hover { box-shadow:0 0 18px rgba(245,165,36,.3); }
[data-testid="stNumberInputContainer"], [data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stTextInput"] [data-baseweb="base-input"], [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInputContainer"], [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] [data-baseweb="base-input"], [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] [data-baseweb="select"] > div { background:rgba(0,0,0,.28) !important; border:1px solid rgba(255,255,255,.14) !important; border-radius:12px !important; box-shadow:none !important; background-image:none !important; -webkit-backdrop-filter:none !important; backdrop-filter:none !important; }
[data-testid="stNumberInputContainer"]::before, [data-testid="stNumberInputContainer"]::after, [data-testid="stTextInput"] [data-baseweb="input"]::before, [data-testid="stTextInput"] [data-baseweb="input"]::after, [data-testid="stTextInput"] [data-baseweb="base-input"]::before, [data-testid="stTextInput"] [data-baseweb="base-input"]::after, [data-testid="stSelectbox"] [data-baseweb="select"] > div::before, [data-testid="stSelectbox"] [data-baseweb="select"] > div::after { content:none !important; display:none !important; }
[data-testid="stNumberInput"] [data-baseweb="input"]::after, [data-testid="stNumberInput"] [data-baseweb="input"]::before, [data-testid="stNumberInput"] [data-baseweb="base-input"]::after, [data-testid="stNumberInput"] [data-baseweb="base-input"]::before, [data-testid="stNumberInput"] [class*="Instructions"], [data-testid="stNumberInput"] [class*="Progress"], [data-testid="stNumberInput"] [class*="Underline"], [data-testid="stNumberInput"] [class*="Highlight"], [data-testid="stTextInput"] [data-baseweb="input"]::after, [data-testid="stTextInput"] [data-baseweb="input"]::before, [data-testid="stTextInput"] [data-baseweb="base-input"]::after, [data-testid="stTextInput"] [data-baseweb="base-input"]::before, [data-testid="stTextInput"] [class*="Instructions"], [data-testid="stTextInput"] [class*="Progress"], [data-testid="stTextInput"] [class*="Underline"], [data-testid="stTextInput"] [class*="Highlight"], [data-testid="stSelectbox"] [data-baseweb="input"]::after, [data-testid="stSelectbox"] [data-baseweb="input"]::before, [data-testid="stSelectbox"] [data-baseweb="base-input"]::after, [data-testid="stSelectbox"] [data-baseweb="base-input"]::before, [data-testid="stSelectbox"] [class*="Instructions"], [data-testid="stSelectbox"] [class*="Progress"], [data-testid="stSelectbox"] [class*="Underline"], [data-testid="stSelectbox"] [class*="Highlight"] { display:none !important; content:none !important; border-bottom:0 !important; box-shadow:none; background:none; height:0; }
[data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="base-input"], [data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stTextInput"] [data-baseweb="base-input"], [data-testid="stSelectbox"] [data-baseweb="input"], [data-testid="stSelectbox"] [data-baseweb="base-input"] { background-image:none !important; }
[data-testid="stNumberInput"] .react-aria-TextField::before, [data-testid="stNumberInput"] .react-aria-TextField::after, [data-testid="stNumberInputContainer"]::before, [data-testid="stNumberInputContainer"]::after, [data-testid="stNumberInput"] *::before, [data-testid="stNumberInput"] *::after, [data-testid="stTextInput"] .react-aria-TextField::before, [data-testid="stTextInput"] .react-aria-TextField::after, [data-testid="stTextInput"] *::before, [data-testid="stTextInput"] *::after, [data-testid="stSelectbox"] *::before, [data-testid="stSelectbox"] *::after { content:none !important; display:none !important; }
.react-aria-TextField, [data-testid="stNumberInputContainer"], [data-testid="stNumberInputField"], [data-testid="stTextInput"] .react-aria-TextField, [data-testid="stSelectbox"] [data-baseweb="select"] { border-bottom:0; background-image:none !important; outline:none !important; }
[data-testid="stNumberInput"] .react-aria-TextField ~ *, [data-testid="stTextInput"] .react-aria-TextField ~ * { display:none !important; }
[data-testid="stNumberInputContainer"]:focus-within { border-color:rgba(245,165,36,.7) !important; box-shadow:0 0 0 1px rgba(245,165,36,.25),0 0 12px rgba(245,165,36,.25) !important; }
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within, [data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within { border-color:rgba(245,165,36,.7) !important; box-shadow:0 0 0 1px rgba(245,165,36,.25),0 0 12px rgba(245,165,36,.25) !important; }
[data-testid="stNumberInput"]:focus-within > div, [data-testid="stNumberInput"]:focus-within .react-aria-TextField, [data-testid="stNumberInput"]:focus-within [data-testid="stNumberInputField"], [data-testid="stTextInput"]:focus-within > div, [data-testid="stTextInput"]:focus-within .react-aria-TextField, [data-testid="stSelectbox"]:focus-within [data-baseweb="select"] { box-shadow:none !important; }
[data-baseweb="select"] input, [data-baseweb="input"] input, [data-baseweb="base-input"] input, [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input, [data-baseweb="input"] > div, [data-baseweb="base-input"] > div, [data-testid="stNumberInput"] button { background:transparent !important; border:0 !important; box-shadow:none !important; }
[data-baseweb="select"]:focus-within > div, [data-baseweb="input"]:focus-within, [data-baseweb="base-input"]:focus-within { border-color:rgba(245,165,36,.7) !important; box-shadow:0 0 0 1px rgba(245,165,36,.25),0 0 14px rgba(245,165,36,.18) !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background:rgba(40,25,18,.92) !important; border-radius:14px !important; }
[data-baseweb="popover"] [role="option"]:hover, [data-baseweb="menu"] [role="option"]:hover { background:rgba(245,165,36,.2) !important; }
[class*="st-key-action_"] { min-height:27rem; padding-bottom:1.25rem !important; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-tournament_name),
[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-tournament_join_code) { padding-bottom:1.25rem !important; }
[class*="st-key-action_"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child,
[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-tournament_name) [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child,
[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-tournament_join_code) [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child,
[class*="st-key-upgrade_tournament_"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child { margin-bottom:0 !important; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary, [data-testid="stExpander"] [data-testid="stExpanderDetails"] { border:none !important; background:transparent !important; box-shadow:none !important; border-radius:inherit !important; outline:none !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] { border-top:0 !important; }
[data-testid="stTabs"], [data-testid="stTabs"] > *, [data-testid="stTabs"] [role="tablist"], [data-testid="stTabs"] [role="tablist"] > *, [data-testid="stTabs"] [role="tablist"] > * > * { border:0 !important; border-bottom:0 !important; box-shadow:none !important; background:transparent !important; }
[data-testid="stTabs"]:has([role="tablist"]), *:has(> [data-testid="stTabs"]) { border-bottom:0 !important; box-shadow:none !important; background:transparent !important; }
[data-testid="stTabs"]::before, [data-testid="stTabs"]::after, [data-testid="stTabs"] > *::before, [data-testid="stTabs"] > *::after, [data-testid="stTabs"] [role="tablist"]::before, [data-testid="stTabs"] [role="tablist"]::after, [data-testid="stTabs"] [role="tablist"] > *::before, [data-testid="stTabs"] [role="tablist"] > *::after { content:none !important; display:none !important; }
[data-testid="stTabs"]:has([role="tablist"])::before, [data-testid="stTabs"]:has([role="tablist"])::after, *:has(> [data-testid="stTabs"])::before, *:has(> [data-testid="stTabs"])::after { content:none !important; display:none !important; }
[data-baseweb="tab-border"], [data-baseweb="tab-highlight"], [class*="TabBorder"], [class*="TabHighlight"], [class*="SelectionIndicator"] { display:none !important; height:0 !important; }
[data-testid="stTabs"] [role="tablist"] { gap:10px; }
[data-testid="stTab"] { border-radius:999px !important; padding:8px 20px !important; background:var(--card) !important; border:1px solid transparent !important; border-bottom:0 !important; box-shadow:none !important; }
[data-testid="stTab"][aria-selected="true"] { background:linear-gradient(135deg,var(--amber),var(--orange)) !important; color:#2B1608 !important; }
[data-testid="stMetricValue"] { color:var(--text); font-weight:800; }
[data-testid="stMetricLabel"] { color:var(--muted); }
.hero { background:linear-gradient(135deg,rgba(245,165,36,.30),rgba(255,122,24,.10)); -webkit-backdrop-filter:blur(18px) saturate(140%); backdrop-filter:blur(18px) saturate(140%); border:1px solid rgba(245,165,36,.45); border-radius:22px; padding:32px 40px; margin-bottom:12px; box-shadow:inset 0 1px 0 rgba(255,255,255,.28),inset 0 -1px 0 rgba(255,255,255,.04),0 12px 32px rgba(0,0,0,.30); text-align:center; }
.hero h1 { background:linear-gradient(90deg,var(--amber),var(--orange)); background-clip:text; -webkit-background-clip:text; color:transparent; font-size:3rem; font-weight:800; margin:0; }
.hero p { color:var(--muted); font-size:1.1rem; margin:4px 0 0; }
.hero .app-icon { vertical-align:baseline; }
.hero .app-icon { width:44px !important; height:44px !important; }
.st-key-signed_in_row [data-testid="stButton"] button { white-space:nowrap; }
.section-heading { color:var(--amber); font-size:1.35rem; font-weight:800; margin:.8rem 0 .5rem; }
[class*="st-key-product_card_"] { box-sizing:border-box; min-height:230px; padding-bottom:18px !important; height:auto !important; overflow:visible !important; }
[class*="st-key-tournament_product_card_"] { box-sizing:border-box; min-height:9.5rem; padding-bottom:18px !important; height:auto !important; overflow:visible !important; }
[class*="st-key-product_card_"] .stat-grid .stat-box:last-child, [class*="st-key-tournament_product_card_"] .stat-grid .stat-box:last-child { margin-bottom:0; }
[class*="st-key-tournament_card_"] { padding-bottom:1.25rem; height:auto !important; overflow:visible !important; }
[class*="st-key-upgrade_tournament_"] { box-sizing:border-box; padding:10px 16px 1.25rem !important; margin:8px 0; background:rgba(255,255,255,.06) !important; border:1px solid rgba(255,255,255,.12) !important; border-radius:16px !important; }
.tournament-upgrade-content { display:flex; align-items:center; gap:12px; min-width:0; height:2.75rem; margin:0; padding:0; line-height:1; white-space:nowrap; }
.tournament-upgrade-content > * { margin:0; padding:0; line-height:1; vertical-align:middle; }
.tournament-upgrade-name { font-weight:800; white-space:nowrap; }
.tournament-upgrade-description { color:var(--muted); font-size:.85rem; overflow:hidden; text-overflow:ellipsis; }
.tournament-upgrade-owned { display:flex; align-items:center; justify-content:center; gap:12px; height:2.75rem; margin:0; padding:0; line-height:1; }
.tournament-upgrade-owned > * { margin:0; padding:0; line-height:1; vertical-align:middle; }
.tournament-owned { display:inline-flex; align-items:center; gap:5px; padding:5px 10px; margin:0; border-radius:999px; background:rgba(74,222,128,.16); color:var(--good); font-weight:700; line-height:1; white-space:nowrap; }
[class*="st-key-upgrade_"] [data-testid="stMarkdownContainer"], [class*="st-key-upgrade_"] [data-testid="stMarkdownContainer"] p, [class*="st-key-upgrade_"] [data-testid="stElementContainer"] { margin:0 !important; padding:0 !important; }
[class*="st-key-upgrade_"] [data-testid="stColumn"] { display:flex; flex-direction:column; justify-content:center; }
[class*="st-key-upgrade_"] [data-testid="stHorizontalBlock"] { align-items:center !important; }
[class*="st-key-upgrade_"] .tournament-upgrade-content svg, [class*="st-key-upgrade_"] .tournament-upgrade-content .tournament-upgrade-name, [class*="st-key-upgrade_"] .tournament-upgrade-content .tournament-upgrade-description, [class*="st-key-upgrade_"] .tournament-upgrade-owned svg, [class*="st-key-upgrade_"] .tournament-owned { margin:0; vertical-align:middle; }
.tournament-player-row, .tournament-ranking-row { display:flex; align-items:center; gap:12px; padding:12px 16px; margin:8px 0; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); border-radius:14px; }
.tournament-player-row { justify-content:space-between; }
.tournament-player-row > span:last-child { margin:2px 4px; }
.stat-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin-top:12px; }
.stat-box { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); border-radius:12px; padding:8px 10px; }
.stat-label { color:var(--muted); font-size:.75rem; }
.stat-value { color:var(--text); font-size:1.2rem; font-weight:800; }
.weather-chip, .code-badge { display:inline-flex; gap:6px; align-items:center; padding:4px 10px; border-radius:999px; background:var(--card); border:1px solid var(--card-border); color:var(--muted); font-size:.8rem; }
.mini-card { text-align:center; padding:12px 8px; background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(255,255,255,.05)); -webkit-backdrop-filter:blur(18px) saturate(140%); backdrop-filter:blur(18px) saturate(140%); border:1px solid rgba(255,255,255,.18); border-radius:22px; box-shadow:inset 0 1px 0 rgba(255,255,255,.28),inset 0 -1px 0 rgba(255,255,255,.04),0 12px 32px rgba(0,0,0,.30); transition:transform .2s ease,background .2s ease,border-color .2s ease; }
.mini-card:hover { transform:translateY(-2px); background:linear-gradient(135deg,rgba(255,255,255,.21),rgba(255,255,255,.08)); border-color:rgba(245,165,36,.45); }
.app-icon { display:inline-flex; color:var(--amber); vertical-align:middle; flex:none; }
.app-icon svg { width:100%; height:100%; }
.notice { display:flex; align-items:center; gap:12px; margin:12px 0 18px 0; padding:12px 16px; background:rgba(20,12,8,.45); border:1px solid; border-radius:14px; color:var(--text); font-size:.95rem; line-height:1.35; }
.notice-success { --notice-color:#4ADE80; --notice-icon-bg:rgba(74,222,128,.18); background:linear-gradient(rgba(74,222,128,.08),transparent),rgba(20,12,8,.45); border-color:rgba(74,222,128,.28); }
.notice-error { --notice-color:#F87171; --notice-icon-bg:rgba(248,113,113,.18); background:linear-gradient(rgba(248,113,113,.08),transparent),rgba(20,12,8,.45); border-color:rgba(248,113,113,.28); }
.notice-info { --notice-color:#F5A524; --notice-icon-bg:rgba(245,165,36,.18); background:linear-gradient(rgba(245,165,36,.08),transparent),rgba(20,12,8,.45); border-color:rgba(245,165,36,.28); }
.notice-warning { --notice-color:#FF7A18; --notice-icon-bg:rgba(255,122,24,.18); background:linear-gradient(rgba(255,122,24,.08),transparent),rgba(20,12,8,.45); border-color:rgba(255,122,24,.28); }
.notice-icon { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; flex:none; border-radius:50%; background:var(--notice-icon-bg); color:var(--notice-color); }
.notice-icon .app-icon { color:var(--notice-color); }
.notice-icon svg { width:20px; height:20px; }
[data-testid="stDataFrame"], [data-testid="stTable"] { color:var(--text); }
[data-testid="stTable"] table { background:transparent !important; border-collapse:separate; border-spacing:0; border-radius:14px; overflow:hidden; }
[data-testid="stTable"] th, [data-testid="stTable"] td { background:transparent !important; border-left:none !important; border-right:none !important; border-top:none !important; border-bottom:1px solid rgba(255,255,255,.12) !important; padding:10px 14px !important; color:var(--text); }
[data-testid="stTable"] th { color:var(--amber) !important; text-transform:uppercase; letter-spacing:.06em; font-size:.72rem; }
[data-testid="stTable"] tr:last-child td { font-weight:800; }
[data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] .vega-embed, [data-testid="stVegaLiteChart"] canvas, [data-testid="stVegaLiteChart"] svg, [data-testid="stVegaLiteChart"] .marks { background:transparent !important; }
[data-testid="stVegaLiteChart"] .role-axis text { fill:var(--muted) !important; }
[data-testid="stVegaLiteChart"] .role-axis-grid line { stroke:var(--muted) !important; stroke-opacity:.16 !important; }
@supports not (backdrop-filter:blur(1px)) { [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stExpander"], .hero, .mini-card { background:rgba(58,38,28,.88); } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition:none !important; scroll-behavior:auto !important; } [data-testid="stMetric"]:hover, [data-testid="stVerticalBlockBorderWrapper"]:hover, [data-testid="stExpander"]:hover, .mini-card:hover { transform:none !important; } }
</style>""", unsafe_allow_html=True)


inject_css()


def show_hero():
    st.markdown(f'<div class="hero"><h1>{icon("coffee", 44)} Campus Tycoon</h1><p>Run a small campus shop for five days.</p></div>', unsafe_allow_html=True)

def show_signed_in_banner():
    st.markdown(f'<div class="hero"><h1>{icon("coffee", 44)} Campus Tycoon</h1><p>Run a small campus shop for five days.</p></div>', unsafe_allow_html=True)

# Before signing in: only a short welcome and the sign-in button, no game data.
if not st.user.is_logged_in:
    st.markdown('<div style="height:10vh"></div>', unsafe_allow_html=True)
    _, sign_in_column, _ = st.columns([1, 2, 1])
    with sign_in_column:
        show_hero()
        st.markdown('<div style="text-align:center">Welcome! Run a small campus shop for five days. Sign in to play.</div>', unsafe_allow_html=True)
        if st.button("Sign in with Google", key="sign_in_button", type="primary", icon=":material/login:", use_container_width=True):
            st.login()
        mini_columns = st.columns(3)
        for mini_column, glyph, caption in zip(mini_columns, ("cart", "trending-up", "trophy"), ("Buy stock", "Set prices", "Beat the market")):
            with mini_column:
                st.markdown(f'<div class="mini-card">{icon(glyph)}<br>{caption}</div>', unsafe_allow_html=True)
    st.stop()

# The player is always the signed-in Google email, never typed in.
try:
    PLAYER = logic.player_from_user(st.user)
except ValueError as error:
    notice("error", friendly_error(error))
    if st.button("Sign out", key="sign_out_error_button", icon=":material/logout:"):
        st.logout()
    st.stop()

show_signed_in_banner()
col1, col2 = st.columns([5, 1], vertical_alignment="center")
with col1:
    st.caption(f"Signed in as {PLAYER}")
with col2:
    if st.button("Sign out", key="sign_out_button", icon=":material/logout:", use_container_width=True):
        st.logout()



def forget_practice_prices():
    # The price fields remember what was typed; after a new run they must show the new prices.
    for name in logic.PRODUCTS:
        st.session_state.pop(f"practice_price_{name}", None)


# The Practice screen is a fragment: its buttons rerun only this screen, not the whole app.
@st.fragment
def practice_screen():
    show_flash("practice")
    try:
        game = logic.load_game(DB_PATH, PLAYER)
    except db.DatabaseUnavailable as error:
        notice("error", friendly_error(error))
        return
    run_complete = logic.is_run_complete(game)

    col1, col2, col3 = st.columns(3)
    col1.metric("Cash", f"€{game['cash']:.2f}")
    if run_complete:
        col2.metric("Progress", "Run complete")
    else:
        col2.metric("Progress", f"Day {game['day']} of {logic.RUN_DAYS}")
    col3.metric("Loan to repay", f"€{game['debt']:.2f}")
    st.caption(f"Level: {logic.level_name(game)} (started with €{game['start_cash']:.2f})")

    if run_complete:
        final = logic.final_result(game)
        st.subheader("Final result")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final cash", f"€{final['final_cash']:.2f}")
        col2.metric("Remaining stock at cost", f"€{final['stock_at_cost']:.2f}")
        col3.metric("Loan to repay", f"€{game['debt']:.2f}")
        col4.metric("Overall gain or loss", f"€{final['gain']:.2f}")
        email_status = st.session_state.pop("email_status", None)
        if email_status == "sent":
            notice("success", f"Your result was emailed to {PLAYER}.")
        elif email_status == "skipped":
            notice("info", "Result email is not configured, so no email was sent.")
        elif email_status == "failed":
            notice("warning", "We could not send the email, but your result is saved.")

    if not run_complete:
        with st.expander("AI business advisor"):
            if st.button("Ask the advisor", key="practice_advisor_button", icon=":material/psychology:"):
                api_key = st.secrets.get("OPENROUTER_API_KEY", "")
                advice = logic.get_advice(
                    game,
                    lambda prompt: advisor.ask_openrouter(prompt, api_key),
                )
                label = "AI suggestion" if advice["source"] == "ai" else "Basic tip (AI not available)"
                st.write(label)
                st.table(
                    [
                        {
                            "Product": product,
                            "Price": f"€{line['price']:.2f}",
                            "Reason": line["reason"],
                        }
                        for product, line in advice["prices"].items()
                    ]
                )

    with st.expander("New run", expanded=run_complete):
        new_level = st.selectbox(
            "Difficulty",
            list(logic.DIFFICULTY_LEVELS),
            index=list(logic.DIFFICULTY_LEVELS).index("Normal"),
            format_func=lambda name: f"{name} (€{logic.DIFFICULTY_LEVELS[name]:.0f} to start)",
            key="new_run_level",
        )
        if not st.session_state.get("confirm_new_run"):
            if st.button("Start a new run", key="practice_new_run_button", icon=":material/restart_alt:"):
                st.session_state["confirm_new_run"] = True
                st.rerun(scope="fragment")
        else:
            notice("warning", f"Start a new {new_level} run? The current run and its history will be lost.")
            col1, col2 = st.columns(2)
            if col1.button("Yes, start a new run", key="practice_confirm_new_run_button", icon=":material/check:"):
                try:
                    logic.new_run(DB_PATH, PLAYER, new_level)
                    st.session_state["confirm_new_run"] = False
                    forget_practice_prices()
                    st.rerun(scope="fragment")
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
            if col2.button("Cancel", key="practice_cancel_new_run_button", icon=":material/close:"):
                st.session_state["confirm_new_run"] = False
                st.rerun(scope="fragment")

    section_heading("cart", "Products")
    if not run_complete:
        preview = logic.demand_preview(game)

    product_columns = st.columns(3)
    for index, (name, details) in enumerate(logic.PRODUCTS.items()):
        with product_columns[index % 3]:
            stat_items = [("Stock", game['stock'][name]), ("Price", f"€{game['price'][name]:.2f}")]
            if not run_complete:
                stat_items.extend([("Demand", preview[name]['demand']), ("Will sell", preview[name]['will_sell'])])
            product_card(
                name, stat_items,
                f"Unit cost: €{details['unit_cost']:.2f} · Reference price: €{details['reference_price']:.2f}",
            )
    st.caption(
        "Demand per product per day: 10 units at or below its reference price, "
        "5 units up to twice the reference price, 0 units above that."
    )

    action_columns = st.columns(3)
    with action_columns[0]:
        with st.container(border=True, key="action_price"):
            section_heading("trending-up", "Selling prices")
            # A form: typing a price reruns nothing until the button is pressed.
            with st.form("practice_price_form", border=False):
                new_prices = {}
                for name in logic.PRODUCTS:
                    new_prices[name] = st.number_input(
                        f"{name} (€)", min_value=0.01, max_value=logic.MAX_PRICE, step=0.01,
                        value=game["price"][name], format="%.2f", key=f"practice_price_{name}",
                    )
                prices_submitted = st.form_submit_button(
                    "Set prices", icon=":material/sell:", disabled=run_complete, use_container_width=True,
                )
            if prices_submitted:
                changed = {
                    name: round(float(value), 2)
                    for name, value in new_prices.items()
                    if round(float(value), 2) != game["price"][name]
                }
                if not changed:
                    notice("info", "No price changed.")
                else:
                    try:
                        logic.set_prices(DB_PATH, PLAYER, changed)
                        flash("practice", "Prices updated.", kind="toast")
                        st.rerun(scope="fragment")
                    except (ValueError, db.DatabaseUnavailable) as error:
                        notice("error", friendly_error(error))

    with action_columns[1]:
        with st.container(border=True, key="action_loan"):
            section_heading("wallet", "Loan")
            st.caption(
                f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with "
                f"{logic.LOAN_INTEREST:.0%} interest: the debt is subtracted from your final gain."
            )
            has_loan = game["debt"] > 0
            loan_amount = st.number_input(
                "Amount (€)", min_value=1, max_value=logic.LOAN_MAX, step=1, value=logic.LOAN_MAX,
                key="loan_amount",
            )
            st.write(f"You will owe €{logic.loan_debt(int(loan_amount)):.2f}")
            if st.button("Take loan", key="practice_loan_button", icon=":material/account_balance_wallet:", disabled=run_complete or has_loan, use_container_width=True):
                try:
                    logic.take_loan(DB_PATH, PLAYER, int(loan_amount))
                    flash("practice", "Loan taken.", kind="toast")
                    st.rerun(scope="fragment")
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))

    with action_columns[2]:
        with st.container(border=True, key="action_buy"):
            section_heading("cart", "Buy stock")
            # clear_on_submit puts every quantity back to 0 after buying.
            with st.form("practice_buy_form", border=False, clear_on_submit=True):
                quantities = {}
                for name, details in logic.PRODUCTS.items():
                    quantities[name] = st.number_input(
                        f"{name} (€{details['unit_cost']:.2f} each)", min_value=0, step=1, value=0,
                        key=f"practice_buy_{name}",
                    )
                buy_submitted = st.form_submit_button(
                    "Buy", icon=":material/shopping_cart:", disabled=run_complete, use_container_width=True,
                )
            if buy_submitted:
                order = {name: int(value) for name, value in quantities.items()}
                try:
                    logic.buy_many(DB_PATH, PLAYER, order)
                    flash("practice", f"Stock bought for €{logic.order_cost({n: q for n, q in order.items() if q > 0}):.2f}.", kind="toast")
                    st.rerun(scope="fragment")
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))

    if st.button("Trade one day", key="practice_trade_day_button", disabled=run_complete, type="primary", use_container_width=True, icon=":material/play_arrow:"):
        try:
            logic.trade_day(DB_PATH, PLAYER)
            game = logic.load_game(DB_PATH, PLAYER)
            if logic.is_run_complete(game):
                with st.spinner("Sending your result by email..."):
                    st.session_state["email_status"] = mailer.send_result_email(
                        PLAYER, logic.final_result(game)
                    )
            st.rerun(scope="fragment")
        except (ValueError, db.DatabaseUnavailable) as error:
            notice("error", friendly_error(error))

    section_heading("trending-up", "Results")
    try:
        results = logic.get_results(DB_PATH, PLAYER)
    except db.DatabaseUnavailable as error:
        notice("error", friendly_error(error))
        results = []

    # History charts: built only from this player's own saved results.
    chart_data = logic.profit_chart_data(results)
    if chart_data["Day"]:
        chart_data["Day"] = [f"Day {day}" for day in chart_data["Day"]]
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            with st.container(border=True):
                st.write("Gross profit per day by product")
                st.bar_chart(
                    chart_data, x="Day", y=list(logic.PRODUCTS), stack=False,
                    color=["#F5A524", "#FF7A18", "#5EEAD4"],
                    x_label="Day", y_label="Gross profit (€)",
                )
        with chart_col2:
            with st.container(border=True):
                st.write("Total gross profit per day")
                st.bar_chart(
                    chart_data, x="Day", y="Total", color="#F5A524",
                    x_label="Day", y_label="Gross profit (€)",
                )
    else:
        notice("info", "Trade a day to see your charts.")

    for result in reversed(results):
        with st.container(border=True, key=f"practice_result_day_{result['day']}"):
            st.markdown(f'### Day {result["day"]}')
            rows = []
            for name, line in list(result["by_product"].items()) + [("Total", result["total"])]:
                rows.append(
                    {
                        "Product": name,
                        "Units sold": line["units_sold"],
                        "Revenue": f"€{line['revenue']:.2f}",
                        "COGS": f"€{line['cogs']:.2f}",
                        "Gross profit": f"€{line['gross_profit']:.2f}",
                    }
                )
            st.table(rows)

    if run_complete:
        st.download_button(
            "Download run report (CSV)",
            data=logic.build_run_report_csv(results).encode("utf-8-sig"),
            file_name="run_report.csv",
            mime="text/csv",
            type="primary",
            icon=":material/download:",
        )


def show_closed_day(closed_day, player, scope):
    with st.container(border=True, key=f"{scope}_closed_day"):
        notice("success", f"Day {closed_day['day']} closed.")
        own_sales = closed_day.get("by_player", {}).get(player)
        if own_sales is not None:
            st.table(
                [
                    {
                        "Product": product,
                        "Units sold": line["units_sold"],
                        "Revenue": f"€{line['revenue']:.2f}",
                    }
                    for product, line in own_sales.items()
                ]
            )


def market_rows(day, player):
    # One row per stand: price and units sold of each product (no cash or stock of others).
    rows = []
    for stand in day["stands"]:
        row = {"Player": stand["name"] + (" (you)" if stand["player"] == player else "")}
        for product in logic.PRODUCTS:
            row[f"{product} price"] = f"€{stand['price'][product]:.2f}"
            row[f"{product} sold"] = stand["units_sold"][product]
        rows.append(row)
    return rows


# Each tournament card is a fragment: its buttons rerun only this card.
@st.fragment
def tournament_card(tournament_id, player):
    try:
        screen = logic.tournament_screen(DB_PATH, player, tournament_id, weather.fetch_lisbon_weather)
    except (ValueError, db.DatabaseUnavailable) as error:
        notice("error", friendly_error(error))
        return
    today_weather = screen["weather"]
    if today_weather["rain"]:
        weather_name = "rain"
    elif today_weather["hot"]:
        weather_name = "hot"
    else:
        weather_name = "normal"
    weather_icon, weather_label = {"rain": ("cloud-rain", "Rain"), "hot": ("sun", "Hot"), "normal": ("cloud-sun", "Normal")}[weather_name]

    products = list(logic.PRODUCTS)
    own = screen["stand"]
    is_ready = own["ready"]
    playing = screen["day"] <= logic.RUN_DAYS
    can_act = playing and not is_ready
    owned = screen["upgrades"]

    with st.container(border=True, key=f"tournament_card_{tournament_id}"):
        header_left, header_code, header_refresh = st.columns([4, 1, 1], vertical_alignment="center")
        with header_left:
            st.markdown(f'<div style="font-size:1.55rem;font-weight:800">{html.escape(str(screen["name"]))}</div>', unsafe_allow_html=True)
        with header_code:
            st.markdown(f'<div style="text-align:right"><span class="code-badge">{html.escape(str(screen["code"]))}</span></div>', unsafe_allow_html=True)
        with header_refresh:
            # The brief asks for a Refresh button instead of live updates: it reloads only this card.
            if st.button("Refresh", key=f"t{tournament_id}_refresh_button", icon=":material/refresh:", use_container_width=True):
                st.rerun(scope="fragment")

        weather_tints = {
            "rain": ("rgba(96,165,250,0.30)", "rgba(30,64,175,0.15)"),
            "hot": ("rgba(255,122,24,0.40)", "rgba(239,68,68,0.20)"),
            "normal": ("rgba(255,236,210,0.18)", "rgba(245,165,36,0.12)"),
        }
        tint_start, tint_end = weather_tints[weather_name]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:20px;padding:18px 22px;margin:12px 0;'
            f'background:linear-gradient(120deg,{tint_start},{tint_end});border:1px solid rgba(255,255,255,.18);'
            f'border-radius:20px;backdrop-filter:blur(18px)">{icon(weather_icon, 48)}'
            f'<div style="font-size:1.35rem;font-weight:800">Today in Lisbon: {html.escape(weather_label)}</div></div>',
            unsafe_allow_html=True,
        )

        metric_columns = st.columns(3)
        metric_columns[0].metric("Day", f"Day {screen['day']} of {logic.RUN_DAYS}" if playing else "Complete")
        metric_columns[1].metric("Cash", f"€{own['cash']:.2f}")
        metric_columns[2].metric("Players ready", f"{sum(1 for row in screen['players'] if row['ready'])}/{len(screen['players'])}")

        section_heading("cart", "Products")
        product_columns = st.columns(3)
        for index, product in enumerate(products):
            with product_columns[index]:
                product_card(
                    product,
                    [("Stock", own["stock"][product]), ("Price", f"€{own['price'][product]:.2f}")],
                    "",
                    key=f"tournament_product_card_{tournament_id}_{product}",
                )

        action_columns = st.columns(2)
        with action_columns[0]:
            with st.container(border=True, key=f"action_t{tournament_id}_buy"):
                section_heading("cart", "Buy stock")
                if can_act:
                    with st.form(f"t{tournament_id}_buy_form", border=False, clear_on_submit=True):
                        quantities = {}
                        for product in products:
                            quantities[product] = st.number_input(
                                f"{product} (€{logic.PRODUCTS[product]['unit_cost']:.2f} each)",
                                min_value=0, step=1, value=0, key=f"t{tournament_id}_buy_{product}",
                            )
                        buy_submitted = st.form_submit_button("Buy", icon=":material/shopping_cart:", use_container_width=True)
                    if buy_submitted:
                        try:
                            bought = logic.buy_tournament_stock_many(
                                DB_PATH, player, tournament_id,
                                {product: int(value) for product, value in quantities.items()},
                            )
                            flash(f"t{tournament_id}_buy", f"Stock purchased for €{bought['cost']:.2f}.")
                            st.rerun(scope="fragment")
                        except (ValueError, db.DatabaseUnavailable) as error:
                            notice("error", friendly_error(error))
                    show_flash(f"t{tournament_id}_buy")

        with action_columns[1]:
            with st.container(border=True, key=f"action_t{tournament_id}_price"):
                section_heading("trending-up", "Set prices")
                if can_act:
                    with st.form(f"t{tournament_id}_price_form", border=False):
                        new_prices = {}
                        for product in products:
                            new_prices[product] = st.number_input(
                                f"{product} (€)", min_value=0.01, max_value=logic.MAX_PRICE, step=0.01,
                                value=float(own["price"][product]), format="%.2f",
                                key=f"t{tournament_id}_price_{product}",
                            )
                        price_submitted = st.form_submit_button("Set prices", icon=":material/sell:", use_container_width=True)
                    if price_submitted:
                        changed = {
                            product: round(float(value), 2)
                            for product, value in new_prices.items()
                            if round(float(value), 2) != own["price"][product]
                        }
                        if not changed:
                            notice("info", "No price changed.")
                        else:
                            try:
                                logic.set_tournament_prices(DB_PATH, player, tournament_id, changed)
                                flash(f"t{tournament_id}_price", "Prices updated.")
                                st.rerun(scope="fragment")
                            except (ValueError, db.DatabaseUnavailable) as error:
                                notice("error", friendly_error(error))
                    show_flash(f"t{tournament_id}_price")

        for name, details in logic.UPGRADES.items():
            product_name = html.escape(str(details["product"]))
            reference_price = html.escape(f"€{float(details['reference_price']):.2f}")
            with st.container(border=True, key=f"upgrade_tournament_{tournament_id}_{name}"):
                upgrade_columns = st.columns([5, 2], vertical_alignment="center")
                with upgrade_columns[0]:
                    st.markdown(
                        f'<div class="tournament-upgrade-content">{icon("trending-up", 20)}'
                        f'<span class="tournament-upgrade-name">{html.escape(str(name))}</span>'
                        f'<span class="tournament-upgrade-description">Raises the {product_name} reference price to {reference_price}</span></div>',
                        unsafe_allow_html=True,
                    )
                with upgrade_columns[1]:
                    if name in owned:
                        st.markdown(
                            f'<div class="tournament-upgrade-owned"><span class="tournament-owned">{icon("check", 16)} Owned</span></div>',
                            unsafe_allow_html=True,
                        )
                    elif can_act:
                        if st.button(
                            f"Buy {name} (€{details['cost']:.2f})", icon=":material/upgrade:",
                            key=f"t{tournament_id}_upgrade_{name}_button", use_container_width=True,
                        ):
                            try:
                                logic.buy_tournament_upgrade(DB_PATH, player, tournament_id, name)
                                flash(f"t{tournament_id}_upgrade", "Upgrade purchased.")
                                st.rerun(scope="fragment")
                            except (ValueError, db.DatabaseUnavailable) as error:
                                notice("error", friendly_error(error))
                show_flash(f"t{tournament_id}_upgrade")

        if can_act:
            if st.button("Ready", key=f"t{tournament_id}_ready_button", icon=":material/check:", type="primary", use_container_width=True):
                try:
                    result = logic.ready_tournament(DB_PATH, player, tournament_id)
                    if result["closed_day"]:
                        # Everyone is ready, so this click closed the day: show its result.
                        flash(f"t{tournament_id}_ready", result["closed_day"], kind="closed_day")
                    else:
                        flash(f"t{tournament_id}_ready", "You are Ready.")
                    st.rerun(scope="fragment")
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
        elif is_ready and playing:
            notice("info", "You are Ready. Waiting for the other players.")
        show_flash(f"t{tournament_id}_ready")
        if player == screen["organiser"] and playing and st.button(
            "Close day now", key=f"t{tournament_id}_close_button", icon=":material/lock_clock:",
            use_container_width=True,
        ):
            try:
                closed_day = logic.close_tournament_day(DB_PATH, player, tournament_id)
                flash(f"t{tournament_id}_close", closed_day, kind="closed_day")
                st.rerun(scope="fragment")
            except (ValueError, db.DatabaseUnavailable) as error:
                notice("error", friendly_error(error))
        show_flash(f"t{tournament_id}_close")

        if screen["ranking"] is not None:
            section_heading("trophy", "Ranking")
            for position, row in enumerate(screen["ranking"], start=1):
                position_label = {1: "1st", 2: "2nd", 3: "3rd"}.get(position, str(position))
                tone = {1: "#F5A524", 2: "#C0C8D0", 3: "#CD7F32"}.get(position, "rgba(255,255,255,.12)")
                st.markdown(
                    f'<div class="tournament-ranking-row">'
                    f'<span style="width:42px;height:42px;display:flex;align-items:center;justify-content:center;'
                    f'border-radius:50%;background:{tone};color:#2B1608;font-weight:800">{position_label}</span>'
                    f'<strong style="flex:1">{html.escape(str(logic.player_name(row["player"])))}</strong>'
                    f'<span style="text-align:right;color:var(--muted);font-size:.78rem">Gain<br><b style="color:var(--text)">€{row["gain"]:.2f}</b></span>'
                    f'<span style="text-align:right;color:var(--muted);font-size:.78rem">Final cash<br><b style="color:var(--text)">€{row["final_cash"]:.2f}</b></span>'
                    f'<span style="text-align:right;color:var(--muted);font-size:.78rem">Stock at cost<br><b style="color:var(--text)">€{row["stock_at_cost"]:.2f}</b></span></div>',
                    unsafe_allow_html=True,
                )
        section_heading("users", "Players")
        for row in screen["players"]:
            ready_label = "Ready" if row["ready"] else "Not ready"
            ready_color = "var(--good)" if row["ready"] else "var(--muted)"
            st.markdown(
                f'<div class="tournament-player-row">'
                f'<span>{html.escape(str(logic.player_name(row["player"])))}</span>'
                f'<span style="padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.07);color:{ready_color};font-size:.8rem;font-weight:700">{ready_label}</span></div>',
                unsafe_allow_html=True,
            )

        if screen["days"]:
            section_heading("trending-up", "Market results")
            latest = screen["days"][-1]
            st.caption(f"Day {latest['day']}: every stand's price and units sold.")
            st.table(market_rows(latest, player))
            if len(screen["days"]) > 1:
                with st.expander("Earlier days"):
                    for day in reversed(screen["days"][:-1]):
                        st.write(f"Day {day['day']}")
                        st.table(market_rows(day, player))


def tournaments_screen():
    create_column, join_column = st.columns(2)
    with create_column:
        with st.container(border=True):
            section_heading("trophy", "Create a tournament")
            tournament_name = st.text_input("Tournament name", key="tournament_name")
            if st.button("Create tournament", key="tournament_create_button", type="primary", icon=":material/add_circle:", use_container_width=True):
                try:
                    created = logic.create_tournament(DB_PATH, PLAYER, tournament_name)
                    st.session_state["created_tournament"] = created
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
            created = st.session_state.pop("created_tournament", None)
            if created:
                notice("success", f"Tournament created: {created['name']}")
                st.caption(f"Join code: {created['code']}")

    with join_column:
        with st.container(border=True):
            section_heading("users", "Join a tournament")
            join_code = st.text_input("Join code", key="tournament_join_code")
            if st.button("Join tournament", key="tournament_join_button", icon=":material/login:", use_container_width=True):
                try:
                    joined = logic.join_tournament(DB_PATH, PLAYER, join_code)
                    st.session_state["joined_message"] = (
                        f"Joined {joined['name']} in seat {joined['seat']}."
                    )
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
            joined_message = st.session_state.pop("joined_message", None)
            if joined_message:
                notice("success", joined_message)

    try:
        my_stands = logic.my_tournaments(DB_PATH, PLAYER)
    except (ValueError, db.DatabaseUnavailable) as error:
        notice("error", friendly_error(error))
        my_stands = []

    if my_stands:
        section_heading("trophy", "My tournament stands")
        for stand in my_stands:
            tournament_card(stand["id"], PLAYER)


def help_screen():
    help_content = [
        ("trophy", "Goal", "Finish five days with the highest gain."),
        ("clock", "Each day", "Buy stock, set prices, then trade one day."),
        ("trending-up", "Demand", "Demand per product per day: 10 units at or below its reference price, 5 units up to twice the reference price, 0 units above that."),
        ("wallet", "Loan", f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with {logic.LOAN_INTEREST:.0%} interest, which is subtracted from your final gain."),
    ]
    upgrade_cost = next(details["cost"] for details in logic.UPGRADES.values())
    help_content.append(("users", "Tournaments", "Join with a code to play in a shared market. The cheapest price sells first. Players use Ready and the organiser can Close day. Weather comes from Lisbon. You can buy a Coffee machine upgrade for €" + f"{upgrade_cost:.2f}."))
    help_columns = st.columns(2)
    for index, (glyph, heading, body) in enumerate(help_content):
        target = help_columns[index % 2] if index < 4 else st.container()
        with target:
            with st.container(border=True, key=f"help_section_{heading}"):
                st.markdown(f'<div class="section-heading">{icon(glyph)} {heading}</div>', unsafe_allow_html=True)
                st.write(body)


# on_change="rerun" makes the tabs remember which one is open, so only that one is built.
practice_tab, tournament_tab, help_tab = st.tabs(
    [
        ":material/storefront: Practice",
        ":material/emoji_events: Tournaments",
        ":material/help: How to play",
    ],
    key="main_tab",
    on_change="rerun",
)

if practice_tab.open:
    with practice_tab:
        practice_screen()
if tournament_tab.open:
    with tournament_tab:
        tournaments_screen()
if help_tab.open:
    with help_tab:
        help_screen()
