import streamlit as st

import db
import html
import logic
import mailer
import reloader

# After a merge Streamlit Cloud keeps the old db.py and logic.py in memory: reload them when their
# files changed, so the new screens never call functions the old modules do not have.
reloader.reload_changed([db, logic, mailer])

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
:root { --bg1:#2A1A12; --glow1:#7A3B16; --glow2:#C2410C; --amber:#F5A524; --orange:#FF7A18; --teal:#5EEAD4; --text:#F6EBDD; --muted:#C9B8A6; --card:rgba(255,255,255,0.06); --card-border:rgba(255,255,255,0.10); --good:#4ADE80; --bad:#F87171; }
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
[class*="st-key-home_card_"] { box-sizing:border-box; padding:24px 22px 22px !important; }
[class*="st-key-home_card_"] [data-testid="stElementContainer"], [class*="st-key-home_card_"] [data-testid="stMarkdownContainer"] { width:100% !important; }
[class*="st-key-home_card_"] [data-testid="stElementContainer"]:last-child { margin-bottom:0 !important; }
.home-card-body { display:flex; flex-direction:column; align-items:center; text-align:center; width:100%; margin-bottom:1rem; }
.home-card-icon { display:flex; align-items:center; justify-content:center; width:64px; height:64px; border-radius:50%; background:rgba(245,165,36,.16); border:1px solid rgba(245,165,36,.35); }
.home-card-title { color:var(--amber); font-size:1.5rem; font-weight:800; margin:.6rem 0 .2rem; }
.home-card-text { color:var(--muted); font-size:1rem; line-height:1.4; min-height:2.8em; }
@media (max-width:640px) { .home-card-text { min-height:0; } }
[data-testid="stMetricValue"] { color:var(--text); font-weight:800; }
[data-testid="stMetricLabel"] { color:var(--muted); }
.hero { background:linear-gradient(135deg,rgba(245,165,36,.30),rgba(255,122,24,.10)); -webkit-backdrop-filter:blur(18px) saturate(140%); backdrop-filter:blur(18px) saturate(140%); border:1px solid rgba(245,165,36,.45); border-radius:22px; padding:32px 40px; margin-bottom:12px; box-shadow:inset 0 1px 0 rgba(255,255,255,.28),inset 0 -1px 0 rgba(255,255,255,.04),0 12px 32px rgba(0,0,0,.30); text-align:center; }
.hero h1 { background:linear-gradient(90deg,var(--amber),var(--orange)); background-clip:text; -webkit-background-clip:text; color:transparent; font-size:3rem; font-weight:800; margin:0; }
.hero p { color:var(--muted); font-size:1.1rem; margin:4px 0 0; }
.hero .app-icon { vertical-align:baseline; }
.hero .app-icon { width:44px !important; height:44px !important; }
.st-key-signed_in_row [data-testid="stButton"] button { white-space:nowrap; }
.part-heading { display:flex; align-items:center; gap:10px; color:var(--amber); font-size:1.35rem; font-weight:800; margin:.1rem 0 .4rem; }
.part-heading b { display:inline-flex; align-items:center; justify-content:center; width:1.8rem; height:1.8rem; border-radius:50%; background:linear-gradient(135deg,var(--amber),var(--orange)); color:#2B1608; font-size:.95rem; }
[class*="st-key-practice_part_"] { box-sizing:border-box; padding:20px 22px 22px !important; height:auto !important; overflow:visible !important; }
[class*="st-key-practice_part_"]:hover { transform:none !important; }
.st-key-practice_part_money [data-testid="stHorizontalBlock"] { align-items:stretch !important; }
.st-key-practice_part_money [data-testid="stColumn"] > [data-testid="stVerticalBlock"], .st-key-practice_part_money [data-testid="stColumn"] > div { height:100%; }
[class*="st-key-practice_box_"] { box-sizing:border-box; height:100% !important; min-height:12.5rem; padding:16px !important; }
.money-label { color:var(--muted); font-size:.85rem; }
.money-value { color:var(--text); font-size:1.7rem; font-weight:800; line-height:1.2; margin:.3rem 0; }
.money-note { color:var(--muted); font-size:.85rem; }
.plan-heading { font-size:1.05rem; font-weight:800; padding:6px 12px; border-radius:10px; }
.plan-heading-buy { color:var(--teal); background:rgba(94,234,212,.10); border:1px solid rgba(94,234,212,.35); }
.plan-heading-sell { color:var(--amber); background:rgba(245,165,36,.10); border:1px solid rgba(245,165,36,.35); }
.st-key-practice_plan_headings :is([data-testid="stElementContainer"], [data-testid="stMarkdown"], [data-testid="stMarkdownContainer"]) { margin:0 !important; }
.st-key-practice_plan_headings [data-testid="stMarkdownContainer"] :is(p, div) { margin:0 !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) { box-sizing:border-box; height:calc(4.3rem + 22px) !important; padding:10px 12px !important; border-radius:14px !important; overflow:hidden; }
[class*="st-key-practice_buy_side_"] { background:rgba(94,234,212,.06) !important; border:1px solid rgba(94,234,212,.25) !important; }
[class*="st-key-practice_sell_side_"] { background:rgba(245,165,36,.06) !important; border:1px solid rgba(245,165,36,.25) !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) :is([data-testid="stElementContainer"], [data-testid="stMarkdown"], [data-testid="stMarkdownContainer"], [data-testid="stNumberInput"]) { margin:0 !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) [data-testid="stMarkdownContainer"] :is(p, div) { margin:0 !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { gap:.4rem !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] { display:none !important; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) :is([data-testid="stNumberInput"], [data-testid="stNumberInputContainer"]) { height:2.5rem !important; min-height:2.5rem; }
:is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"]) [data-testid="stElementContainer"]:has(.plan-label) { height:1.4rem; }
.plan-product { display:flex; align-items:center; gap:8px; height:4.3rem; }
.plan-product-name { font-weight:800; font-size:1.05rem; line-height:1.2; }
.plan-product-stock { color:var(--muted); font-size:.85rem; line-height:1.2; }
.plan-label { display:flex; align-items:center; height:1.4rem; color:var(--muted); font-size:.8rem; font-weight:600; line-height:1; white-space:nowrap; }
.plan-text { display:flex; align-items:center; height:2.5rem; padding:0 2px; font-size:1.05rem; font-weight:800; line-height:1; }
[class*="st-key-practice_buy_side_"] .plan-text { color:var(--teal); }
[class*="st-key-practice_sell_side_"] .plan-text { color:var(--amber); }
[class*="st-key-practice_sell_side_"] .plan-text-plain { color:var(--text); }
.plan-rule { color:var(--muted); font-size:.95rem; line-height:1.4; margin:0; }
.plan-rule b { color:var(--text); font-weight:800; }
.plan-rule-icon { margin-right:.3rem; }
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] .plan-rule), [data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] .plan-rule) :is([data-testid="stMarkdown"], [data-testid="stMarkdownContainer"]) { margin:0 !important; }
.plan-arrow { display:flex; align-items:center; justify-content:center; height:2.5rem; color:var(--muted); font-size:1.5rem; font-weight:800; }
.st-key-practice_buy_button button { border-color:rgba(94,234,212,.6) !important; }
.st-key-practice_buy_button button:hover { background:rgba(94,234,212,.16) !important; border-color:var(--teal) !important; box-shadow:0 0 18px rgba(94,234,212,.22) !important; }
.st-key-practice_buy_button button span, .st-key-practice_buy_button button svg { color:var(--teal) !important; fill:var(--teal) !important; }
.st-key-practice_part_trade { border:2px solid var(--orange) !important; box-shadow:0 0 0 4px rgba(255,122,24,.12),0 0 40px rgba(255,122,24,.40),0 12px 32px rgba(0,0,0,.30) !important; }
.st-key-practice_part_trade:hover { border-color:var(--orange) !important; }
.st-key-practice_part_trade .part-heading { color:var(--orange); }
.trade-stats { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:.2rem 0 .6rem; }
.st-key-practice_trade_day_button button { min-height:3.75rem; box-shadow:0 0 26px rgba(255,122,24,.45); }
.st-key-practice_trade_day_button button p { font-size:1.3rem !important; font-weight:800 !important; }
[class*="st-key-tournament_part_"] { box-sizing:border-box; padding:20px 22px 22px !important; height:auto !important; overflow:visible !important; margin-bottom:.4rem; }
[class*="st-key-tournament_part_"]:hover { transform:none !important; }
[class*="st-key-tournament_part_money_"] [data-testid="stHorizontalBlock"] { align-items:stretch !important; }
[class*="st-key-tournament_part_money_"] [data-testid="stColumn"] > [data-testid="stVerticalBlock"], [class*="st-key-tournament_part_money_"] [data-testid="stColumn"] > div { height:100%; }
[class*="st-key-tournament_box_"] { box-sizing:border-box; height:100% !important; min-height:9rem; padding:16px !important; }
[class*="st-key-tournament_plan_headings_"] :is([data-testid="stElementContainer"], [data-testid="stMarkdown"], [data-testid="stMarkdownContainer"]) { margin:0 !important; }
[class*="st-key-tournament_plan_headings_"] [data-testid="stMarkdownContainer"] :is(p, div) { margin:0 !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) { box-sizing:border-box; height:calc(4.3rem + 22px) !important; padding:10px 12px !important; border-radius:14px !important; overflow:hidden; }
[class*="st-key-tournament_buy_side_"] { background:rgba(94,234,212,.06) !important; border:1px solid rgba(94,234,212,.25) !important; }
[class*="st-key-tournament_sell_side_"] { background:rgba(245,165,36,.06) !important; border:1px solid rgba(245,165,36,.25) !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) :is([data-testid="stElementContainer"], [data-testid="stMarkdown"], [data-testid="stMarkdownContainer"], [data-testid="stNumberInput"]) { margin:0 !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) [data-testid="stMarkdownContainer"] :is(p, div) { margin:0 !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { gap:.4rem !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] { display:none !important; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) :is([data-testid="stNumberInput"], [data-testid="stNumberInputContainer"]) { height:2.5rem !important; min-height:2.5rem; }
:is([class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) [data-testid="stElementContainer"]:has(.plan-label) { height:1.4rem; }
[class*="st-key-tournament_buy_side_"] .plan-text { color:var(--teal); }
[class*="st-key-tournament_sell_side_"] .plan-text { color:var(--amber); }
[class*="st-key-tournament_sell_side_"] .plan-text-plain { color:var(--text); }
[class*="st-key-t"][class*="_buy_button"] button { border-color:rgba(94,234,212,.6) !important; }
[class*="st-key-t"][class*="_buy_button"] button:hover { background:rgba(94,234,212,.16) !important; border-color:var(--teal) !important; box-shadow:0 0 18px rgba(94,234,212,.22) !important; }
[class*="st-key-t"][class*="_buy_button"] button span, [class*="st-key-t"][class*="_buy_button"] button svg { color:var(--teal) !important; fill:var(--teal) !important; }
[class*="st-key-tournament_part_trade_"] { border:2px solid var(--orange) !important; box-shadow:0 0 0 4px rgba(255,122,24,.12),0 0 40px rgba(255,122,24,.40),0 12px 32px rgba(0,0,0,.30) !important; }
[class*="st-key-tournament_part_trade_"]:hover { border-color:var(--orange) !important; }
[class*="st-key-tournament_part_trade_"] .part-heading { color:var(--orange); }
[class*="st-key-t"][class*="_ready_button"] button { min-height:3.75rem; box-shadow:0 0 26px rgba(255,122,24,.45); }
[class*="st-key-t"][class*="_ready_button"] button p { font-size:1.3rem !important; font-weight:800 !important; }
.part-caption { color:var(--muted); font-size:.9rem; margin:0 0 .6rem; }
[class*="st-key-tournament_row_"] { box-sizing:border-box; padding:14px 18px !important; margin-bottom:.2rem; }
[class*="st-key-tournament_row_"]:hover { transform:none !important; }
.tournament-row { display:flex; align-items:center; flex-wrap:wrap; gap:12px; }
.tournament-row-name { font-size:1.2rem; font-weight:800; color:var(--text); }
.tournament-row-meta { color:var(--muted); font-size:.95rem; }
.order-total { display:flex; align-items:center; min-height:2.2rem; margin:0 0 .75rem; padding:6px 12px; border-radius:10px; font-weight:700; font-size:.95rem; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); }
.order-total-muted { color:var(--muted); font-weight:600; }
.order-total-good { color:var(--teal); border-color:rgba(94,234,212,.35); background:rgba(94,234,212,.06); }
.order-total-bad { color:var(--bad); border-color:rgba(248,113,113,.45); background:rgba(248,113,113,.08); }
.result-product { display:flex; align-items:center; gap:6px; color:var(--amber); font-weight:800; margin:.4rem 0 .2rem; }
@media (max-width:640px) {
  .trade-stats { grid-template-columns:1fr; }
  .st-key-practice_plan_headings, [class*="st-key-tournament_plan_headings_"], .plan-arrow { display:none; }
  [class*="st-key-practice_box_"], [class*="st-key-tournament_box_"] { min-height:0; }
  :is([class*="st-key-practice_buy_side_"], [class*="st-key-practice_sell_side_"], [class*="st-key-tournament_buy_side_"], [class*="st-key-tournament_sell_side_"]) { height:auto !important; overflow:visible; }
  .plan-product { height:auto; }
  :is([class*="st-key-practice_buy_side_"], [class*="st-key-tournament_buy_side_"])::before { content:"Buy from the supplier"; color:var(--teal); font-weight:800; }
  :is([class*="st-key-practice_sell_side_"], [class*="st-key-tournament_sell_side_"])::before { content:"Sell to customers"; color:var(--amber); font-weight:800; }
}
.hero-compact { padding:14px 24px; text-align:left; display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }
.hero-compact h1 { font-size:1.9rem; }
.hero-compact .app-icon { width:30px !important; height:30px !important; }
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
[class*="st-key-practice_result_day_"] [data-testid="stTable"] tr:last-child td { font-weight:800; }
[data-testid="stTable"] th, [data-testid="stTable"] td { text-align:left !important; }
.join-code-big { display:inline-block; margin-top:6px; padding:6px 16px; border-radius:12px; background:rgba(245,165,36,.16); border:1px solid rgba(245,165,36,.55); color:var(--amber); font-size:1.6rem; font-weight:800; letter-spacing:.18em; }
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
    # Smaller than the signed-out banner, so the game starts higher on the screen.
    st.markdown(f'<div class="hero hero-compact"><h1>{icon("coffee", 30)} Campus Tycoon</h1><p>Run a small campus shop for five days.</p></div>', unsafe_allow_html=True)

# Before signing in: only a short welcome and the sign-in button, no game data.
if not st.user.is_logged_in:
    st.markdown('<div style="height:10vh"></div>', unsafe_allow_html=True)
    _, sign_in_column, _ = st.columns([1, 2, 1])
    with sign_in_column:
        show_hero()
        st.markdown('<div style="text-align:center">Welcome! Run a small campus shop for five days. Sign in to play.</div>', unsafe_allow_html=True)
        if st.button("Sign in with Google", key="sign_in_button", type="primary", icon=":material/login:", use_container_width=True):
            # Right after signing in, the player starts on the home page.
            st.query_params.clear()
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



def euros(amount):
    # A loss shows as -€5.00, not €-5.00.
    return f"-€{abs(amount):.2f}" if amount < 0 else f"€{amount:.2f}"


def money_box(label, value, note):
    st.markdown(
        f'<div class="money-label">{html.escape(label)}</div>'
        f'<div class="money-value">{html.escape(str(value))}</div>'
        f'<div class="money-note">{html.escape(note)}</div>',
        unsafe_allow_html=True,
    )


def plan_label(text, help=None):
    # The same small label above every value in a product line, so all labels sit on one row.
    st.markdown(f'<div class="plan-label">{html.escape(text)}</div>', unsafe_allow_html=True, help=help, width="content")


def plan_value(value, plain=False):
    # Plain text as tall as a number input, so it lines up with the fields but does not look editable.
    # plain=True: the normal text colour instead of the side's colour (teal or amber).
    css_class = "plan-text plan-text-plain" if plain else "plan-text"
    st.markdown(f'<div class="{css_class}">{html.escape(str(value))}</div>', unsafe_allow_html=True)


def changed_prices(typed, saved):
    # The typed selling prices that differ from the saved ones, rounded to cents.
    return {
        name: round(float(value), 2)
        for name, value in typed.items()
        if round(float(value), 2) != saved[name]
    }


def part_heading(number, text):
    st.markdown(
        f'<div class="part-heading"><b>{number}</b> {html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def show_practice_day(result):
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


# Part 2 column widths: buy side | arrow | sell side. Headings, lines and buttons use the same widths.
PLAN_SIDES = [3.3, 0.35, 3]


def order_total(quantities, cash, key):
    # Live total of the typed order (specs/feature-live-order-total.md): no need to multiply by hand.
    order = {name: int(value) for name, value in quantities.items() if int(value or 0) > 0}
    if not order:
        text, tone = "Type how many to see the total cost.", "muted"
    else:
        cost = logic.order_cost(order)
        if cost > cash:
            text, tone = f"Total €{cost:.2f}: more than your cash (€{cash:.2f}).", "bad"
        else:
            text, tone = f"Total €{cost:.2f} · cash after buying €{round(cash - cost, 2):.2f}", "good"
    st.markdown(f'<div class="order-total order-total-{tone}" id="{key}">{html.escape(text)}</div>', unsafe_allow_html=True)


@st.fragment
def practice_plan(game, preview, run_complete, buy_round, price_round, day_text):
    with st.container(border=True, key="practice_part_plan"):
        part_heading(2, f"Plan {day_text}")
        # The demand rule stays visible (brief CT03), so players can choose a price with it.
        st.markdown(
            f'<div class="plan-rule"><span class="plan-rule-icon">{icon("info", 16)}</span>Customers per day: '
            "<b>10</b> at or below the reference price · <b>5</b> up to twice it · <b>0</b> above that.</div>",
            unsafe_allow_html=True,
        )
        with st.container(key="practice_plan_headings"):
            buy_heading, _, sell_heading = st.columns(PLAN_SIDES)
            buy_heading.markdown('<div class="plan-heading plan-heading-buy">Buy from the supplier</div>', unsafe_allow_html=True)
            sell_heading.markdown('<div class="plan-heading plan-heading-sell">Sell to customers</div>', unsafe_allow_html=True)
        quantities = {}
        new_prices = {}
        for name, details in logic.PRODUCTS.items():
            reference = details["reference_price"]
            with st.container(key=f"practice_line_{name}"):
                buy_side, arrow, sell_side = st.columns(PLAN_SIDES, vertical_alignment="center")
                with buy_side:
                    with st.container(key=f"practice_buy_side_{name}"):
                        name_column, cost_column, quantity_column = st.columns([1.3, 1, 1], vertical_alignment="top")
                        name_column.markdown(
                            f'<div class="plan-product">{icon(PRODUCT_ICONS.get(name, "box"))}'
                            f'<div><div class="plan-product-name">{html.escape(name)}</div>'
                            f'<div class="plan-product-stock">{game["stock"][name]} in stock</div></div></div>',
                            unsafe_allow_html=True,
                        )
                        with cost_column:
                            plan_label("Supplier price")
                            plan_value(f"€{details['unit_cost']:.2f}")
                        with quantity_column:
                            plan_label("How many")
                            quantities[name] = st.number_input(
                                f"How many {name}", min_value=0, step=1, value=0,
                                key=f"practice_buy_{name}_{buy_round}", disabled=run_complete,
                                label_visibility="collapsed",
                            )
                arrow.markdown('<div class="plan-arrow">→</div>', unsafe_allow_html=True)
                with sell_side:
                    with st.container(key=f"practice_sell_side_{name}"):
                        reference_column, price_column, sells_column = st.columns(3, vertical_alignment="top")
                        with reference_column:
                            plan_label("Reference price")
                            plan_value(f"€{reference:.2f}", plain=True)
                        with price_column:
                            plan_label(
                                "Your selling price (€)",
                                help=(
                                    f"Up to €{reference:.2f}: 10 customers a day. Up to €{2 * reference:.2f}: 5. "
                                    "Above that: none."
                                ),
                            )
                            new_prices[name] = st.number_input(
                                f"Your selling price for {name} (€)",
                                # No min or max here: logic.check_price refuses with a clear message.
                                step=0.01, value=game["price"][name], format="%.2f", key=f"practice_price_{name}_{price_round}",
                                disabled=run_complete, label_visibility="collapsed",
                            )
                        with sells_column:
                            plan_label("Will sell")
                            plan_value(preview[name]["will_sell"])
        total_column, _, save_note_column = st.columns(PLAN_SIDES)
        with total_column:
            order_total(quantities, game["cash"], "practice_order_total")
        with save_note_column:
            changed = changed_prices(new_prices, game["price"])
            note = "Prices changed: press Save selling prices." if changed else "Prices are saved."
            st.markdown(f'<div class="order-total order-total-muted">{note}</div>', unsafe_allow_html=True)
        buy_button_column, _, save_button_column = st.columns(PLAN_SIDES)
        with buy_button_column:
            buy_clicked = st.button(
                "Buy stock", key="practice_buy_button", icon=":material/shopping_cart:",
                disabled=run_complete, use_container_width=True,
            )
        with save_button_column:
            save_clicked = st.button(
                "Save selling prices", key="practice_save_prices_button", icon=":material/sell:",
                disabled=run_complete, use_container_width=True,
            )

        # Each button does only its own job. After it, the whole Practice screen reruns (cash and stock change).
        if buy_clicked:
            order = {name: int(value) for name, value in quantities.items()}
            try:
                logic.buy_many(DB_PATH, PLAYER, order)
                flash("practice", f"Stock bought for €{logic.order_cost({n: q for n, q in order.items() if q > 0}):.2f}.", kind="toast")
                st.session_state["practice_buy_round"] = buy_round + 1
                st.rerun()
            except (ValueError, db.DatabaseUnavailable) as error:
                notice("error", friendly_error(error))
        if save_clicked:
            if not changed:
                notice("info", "No price changed.")
            else:
                try:
                    logic.set_prices(DB_PATH, PLAYER, changed)
                    flash("practice", "Prices updated.", kind="toast")
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))


# The Practice screen is a fragment: typing reruns only this screen; buttons rerun the whole page (no stale boxes).
# Top to bottom (specs/feature-practice-layout.md): New run bar, 1 money, final result, 2 plan, 3 trade, results.
@st.fragment
def practice_screen():
    # Removing a form widget's key does not reset it: the browser sends the old value again.
    # A new round number gives the widget a new key, so it really starts again from its value.
    # buy round: +1 after every successful buy, trade and new run (How many back to 0).
    # price round: +1 after a new run (selling prices back to the new run's prices).
    buy_round = st.session_state.get("practice_buy_round", 0)
    price_round = st.session_state.get("practice_price_round", 0)
    show_flash("practice")
    try:
        game = logic.load_game(DB_PATH, PLAYER)
    except db.DatabaseUnavailable as error:
        notice("error", friendly_error(error))
        return
    run_complete = logic.is_run_complete(game)
    day_text = "(run complete)" if run_complete else f"day {game['day']}"
    preview = logic.demand_preview(game)

    # 0. New run bar
    with st.container(border=True, key="practice_new_run_bar"):
        level_column, button_column = st.columns([2, 3], vertical_alignment="bottom")
        with level_column:
            new_level = st.selectbox(
                "Difficulty",
                list(logic.DIFFICULTY_LEVELS),
                index=list(logic.DIFFICULTY_LEVELS).index("Normal"),
                format_func=lambda name: f"{name} (€{logic.DIFFICULTY_LEVELS[name]:.0f} to start)",
                key="new_run_level",
            )
        with button_column:
            if not st.session_state.get("confirm_new_run"):
                if st.button("Start a new run", key="practice_new_run_button", icon=":material/restart_alt:"):
                    st.session_state["confirm_new_run"] = True
                    st.rerun()
        if st.session_state.get("confirm_new_run"):
            notice("warning", f"Start a new {new_level} run? The current run and its history will be lost.")
            col1, col2 = st.columns(2)
            if col1.button("Yes, start a new run", key="practice_confirm_new_run_button", icon=":material/check:"):
                try:
                    logic.new_run(DB_PATH, PLAYER, new_level)
                    st.session_state["confirm_new_run"] = False
                    # New keys for the price and How many fields, so they show the new run's prices and 0.
                    st.session_state["practice_price_round"] = price_round + 1
                    st.session_state["practice_buy_round"] = buy_round + 1
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
            if col2.button("Cancel", key="practice_cancel_new_run_button", icon=":material/close:"):
                st.session_state["confirm_new_run"] = False
                st.rerun()

    # 1. Your day and money: four boxes of the same size.
    with st.container(border=True, key="practice_part_money"):
        part_heading(1, "Your day and money")
        cash_column, progress_column, debt_column, loan_column = st.columns(4)
        with cash_column:
            with st.container(border=True, key="practice_box_cash"):
                money_box("Cash", f"€{game['cash']:.2f}", f"Started with €{game['start_cash']:.2f}")
        with progress_column:
            with st.container(border=True, key="practice_box_progress"):
                progress = "Run complete" if run_complete else f"Day {game['day']} of {logic.RUN_DAYS}"
                money_box("Progress", progress, f"Level: {logic.level_name(game)}")
        with debt_column:
            with st.container(border=True, key="practice_box_debt"):
                money_box(
                    "Loan to repay", f"€{game['debt']:.2f}",
                    "Paid back from your final gain" if game["debt"] > 0 else "No loan taken",
                )
        with loan_column:
            with st.container(border=True, key="practice_box_loan"):
                has_loan = game["debt"] > 0
                loan_amount = st.number_input(
                    "Take a loan (€)", min_value=1, max_value=logic.LOAN_MAX, step=1, value=logic.LOAN_MAX,
                    key="loan_amount",
                    help=(
                        f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with "
                        f"{logic.LOAN_INTEREST:.0%} interest: the debt is subtracted from your final gain."
                    ),
                )
                st.caption(f"You will owe €{logic.loan_debt(int(loan_amount)):.2f}")
                if st.button("Take loan", key="practice_loan_button", icon=":material/account_balance_wallet:", disabled=run_complete or has_loan, use_container_width=True):
                    try:
                        logic.take_loan(DB_PATH, PLAYER, int(loan_amount))
                        flash("practice", "Loan taken.", kind="toast")
                        st.rerun()
                    except (ValueError, db.DatabaseUnavailable) as error:
                        notice("error", friendly_error(error))

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

    # 2. Plan the day: its own small fragment, so typing a quantity or a price reruns only this part
    # (no database read) and the total cost of the order shows at once.
    practice_plan(game, preview, run_complete, buy_round, price_round, day_text)

    # 3. Trade the day: the most visible part.
    with st.container(border=True, key="practice_part_trade"):
        part_heading(3, f"Trade {day_text}")
        will_sell = sum(line["will_sell"] for line in preview.values())
        profit = logic.expected_profit(game)["total"]
        days_left = 0 if run_complete else logic.RUN_DAYS - game["day"]
        st.markdown(
            '<div class="trade-stats">'
            f'<div class="stat-box"><div class="stat-label">Will sell</div><div class="stat-value">{will_sell} units</div></div>'
            f'<div class="stat-box"><div class="stat-label">Expected profit</div><div class="stat-value">{euros(profit)}</div></div>'
            f'<div class="stat-box"><div class="stat-label">Days left after this day</div><div class="stat-value">{days_left}</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if not run_complete:
            # Hints only: the player can still trade (specs/feature-easier-screens.md).
            for warning in logic.trade_warnings(game["stock"], game["price"]):
                notice("warning", warning)
        trade_label = "Run complete" if run_complete else f"Trade day {game['day']}"
        if st.button(
            trade_label, key="practice_trade_day_button", type="primary", icon=":material/play_arrow:",
            disabled=run_complete, use_container_width=True,
        ):
            # Typed but not bought or saved: the day is not traded, so nothing is lost by surprise.
            # The fields keep their values in session state (their keys include the round).
            typed_quantities = any(
                int(st.session_state.get(f"practice_buy_{name}_{buy_round}", 0) or 0) > 0 for name in logic.PRODUCTS
            )
            typed_prices = {
                name: st.session_state.get(f"practice_price_{name}_{price_round}", game["price"][name])
                for name in logic.PRODUCTS
            }
            unsaved_prices = bool(changed_prices(typed_prices, game["price"]))
            if typed_quantities:
                notice("warning", "You typed quantities but did not buy them. Press Buy stock first, or set How many to 0.")
            if unsaved_prices:
                notice("warning", "Your new selling prices are not saved yet. Press Save selling prices first.")
            if not typed_quantities and not unsaved_prices:
                try:
                    logic.trade_day(DB_PATH, PLAYER)
                    game = logic.load_game(DB_PATH, PLAYER)
                    if logic.is_run_complete(game):
                        with st.spinner("Sending your result by email..."):
                            st.session_state["email_status"] = mailer.send_result_email(
                                PLAYER, logic.final_result(game)
                            )
                    st.session_state["practice_buy_round"] = buy_round + 1
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))

    # 4. Results: the latest day stays visible, the rest folds away.
    section_heading("trending-up", "Results")
    try:
        results = logic.get_results(DB_PATH, PLAYER)
    except db.DatabaseUnavailable as error:
        notice("error", friendly_error(error))
        results = []

    if not results:
        notice("info", "Trade a day to see your results.")
    else:
        show_practice_day(results[-1])
        with st.expander("Charts and all days"):
            # History charts: built only from this player's own saved results.
            chart_data = logic.profit_chart_data(results)
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
            for result in reversed(results[:-1]):
                show_practice_day(result)

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
    # The full results are shown in the card; here only a short line with the player's own sales.
    own_sales = closed_day.get("by_player", {}).get(player)
    message = f"Day {closed_day['day']} closed."
    if own_sales is not None:
        units = sum(line["units_sold"] for line in own_sales.values())
        revenue = round(sum(line["revenue"] for line in own_sales.values()), 2)
        message += f" You sold {units} units for €{revenue:.2f}."
    notice("success", message)


def show_players(screen):
    for row in screen["players"]:
        ready_label = "Ready" if row["ready"] else "Not ready"
        ready_color = "var(--good)" if row["ready"] else "var(--muted)"
        st.markdown(
            f'<div class="tournament-player-row">'
            f'<span>{html.escape(str(logic.player_name(row["player"])))}</span>'
            f'<span style="padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.07);color:{ready_color};font-size:.8rem;font-weight:700">{ready_label}</span></div>',
            unsafe_allow_html=True,
        )


def show_day_tables(day, player):
    # One small table per product: every stand's price and units sold (no cash or stock of others).
    columns = st.columns(len(logic.PRODUCTS))
    for column, product in zip(columns, logic.PRODUCTS):
        with column:
            st.markdown(
                f'<div class="result-product">{icon(PRODUCT_ICONS.get(product, "box"), 18)} {html.escape(product)}</div>',
                unsafe_allow_html=True,
            )
            st.table([
                {
                    "Player": stand["name"] + (" (you)" if stand["player"] == player else ""),
                    "Price": f"€{stand['price'][product]:.2f}",
                    "Sold": stand["units_sold"][product],
                }
                for stand in day["stands"]
            ])


def show_tournament_charts(screen, player):
    # Like the Practice charts, from the saved tournament results.
    days = screen["days"]
    labels = [f"Day {day['day']}" for day in days]
    own = logic.tournament_chart_data(days, player)
    own["Day"] = labels
    everyone = logic.tournament_players_chart_data(days)
    everyone["Day"] = labels
    # Chart field names cannot contain dots (they mean "inside" for the chart library).
    everyone = {key.replace(".", " "): values for key, values in everyone.items()}
    player_names = [key for key in everyone if key != "Day"]
    chart_left, chart_right = st.columns(2)
    if own["Day"] and screen["stand"] is not None:
        with chart_left:
            with st.container(border=True):
                st.write("Your gross profit per day by product")
                st.bar_chart(
                    own, x="Day", y=list(logic.PRODUCTS), stack=False,
                    color=["#F5A524", "#FF7A18", "#5EEAD4"], x_label="Day", y_label="Gross profit (€)",
                )
    with chart_right if screen["stand"] is not None else chart_left:
        with st.container(border=True):
            st.write("Gross profit per day: every player")
            palette = ["#F5A524", "#5EEAD4", "#FF7A18", "#A78BFA", "#F472B6", "#60A5FA", "#34D399", "#FBBF24"]
            st.bar_chart(
                everyone, x="Day", y=player_names, stack=False,
                color=[palette[index % len(palette)] for index in range(len(player_names))],
                x_label="Day", y_label="Gross profit (€)",
            )


def show_results(screen, player, charts_open):
    # The last closed day first; older days and the charts below (open at the end of the tournament).
    days = screen["days"]
    if not days:
        notice("info", "Results appear here when the first day closes.")
        return
    latest = days[-1]
    st.markdown(f'<div class="part-caption">Day {latest["day"]}: every stand\'s price and units sold.</div>', unsafe_allow_html=True)
    show_day_tables(latest, player)
    if charts_open:
        show_tournament_charts(screen, player)
        for day in reversed(days[:-1]):
            with st.expander(f"Day {day['day']}"):
                show_day_tables(day, player)
    else:
        with st.expander("Charts and all days"):
            show_tournament_charts(screen, player)
            for day in reversed(days[:-1]):
                st.markdown(f'<div class="result-product">Day {day["day"]}</div>', unsafe_allow_html=True)
                show_day_tables(day, player)


@st.fragment
def tournament_plan(tournament_id, player, own, references, can_act):
    # Typing a quantity or a price reruns only this part (no database read), so the total shows at once.
    # The round in the How many keys goes up after a buy, so the fields start again from 0.
    # Drawn inside the part 2 box of the card (heading and rule are in tournament_card).
    buy_round = st.session_state.get(f"t{tournament_id}_buy_round", 0)
    with st.container(key=f"tournament_plan_headings_{tournament_id}"):
        buy_heading, _, sell_heading = st.columns(PLAN_SIDES)
        buy_heading.markdown('<div class="plan-heading plan-heading-buy">Buy from the supplier</div>', unsafe_allow_html=True)
        sell_heading.markdown('<div class="plan-heading plan-heading-sell">Sell to customers</div>', unsafe_allow_html=True)
    quantities, new_prices = {}, {}
    for name, details in logic.PRODUCTS.items():
        with st.container(key=f"tournament_line_{tournament_id}_{name}"):
            buy_side, arrow, sell_side = st.columns(PLAN_SIDES, vertical_alignment="center")
            with buy_side:
                with st.container(border=True, key=f"tournament_buy_side_{tournament_id}_{name}"):
                    name_column, cost_column, quantity_column = st.columns([1.3, 1, 1], vertical_alignment="top")
                    name_column.markdown(
                        f'<div class="plan-product">{icon(PRODUCT_ICONS.get(name, "box"))}<div><div class="plan-product-name">{html.escape(name)}</div><div class="plan-product-stock">{own["stock"][name]} in stock</div></div></div>',
                        unsafe_allow_html=True,
                    )
                    with cost_column:
                        plan_label("Supplier price")
                        plan_value(f"€{details['unit_cost']:.2f}")
                    with quantity_column:
                        plan_label("How many")
                        quantities[name] = st.number_input(f"How many tournament {name}", min_value=0, step=1, value=0, key=f"t{tournament_id}_buy_{name}_{buy_round}", disabled=not can_act, label_visibility="collapsed")
            arrow.markdown('<div class="plan-arrow">→</div>', unsafe_allow_html=True)
            with sell_side:
                with st.container(border=True, key=f"tournament_sell_side_{tournament_id}_{name}"):
                    reference_column, price_column = st.columns(2, vertical_alignment="top")
                    reference = references[name]
                    with reference_column:
                        plan_label("Reference price")
                        plan_value(f"€{reference:.2f}", plain=True)
                    with price_column:
                        plan_label(
                            "Your selling price (€)",
                            help=(
                                f"Half of the customers pay up to €{reference:.2f}, the other half up to "
                                f"€{2 * reference:.2f}. Above €{2 * reference:.2f} nobody buys. "
                                "The cheapest stand sells first."
                            ),
                        )
                        new_prices[name] = st.number_input(f"Tournament selling price for {name} (€)", step=0.01, value=own["price"][name], format="%.2f", key=f"t{tournament_id}_price_{name}", disabled=not can_act, label_visibility="collapsed")
    changed = {product: round(float(value), 2) for product, value in new_prices.items() if round(float(value), 2) != own["price"][product]}
    total_column, _, save_note_column = st.columns(PLAN_SIDES)
    with total_column:
        order_total(quantities, own["cash"], f"t{tournament_id}_order_total")
    with save_note_column:
        note = "Prices changed: press Save selling prices." if changed else "Prices are saved."
        st.markdown(f'<div class="order-total order-total-muted">{note}</div>', unsafe_allow_html=True)
    buy_button_column, _, save_button_column = st.columns(PLAN_SIDES)
    with buy_button_column:
        buy_clicked = st.button("Buy stock", key=f"t{tournament_id}_buy_button", icon=":material/shopping_cart:", disabled=not can_act, use_container_width=True)
    with save_button_column:
        save_clicked = st.button("Save selling prices", key=f"t{tournament_id}_save_prices_button", icon=":material/sell:", disabled=not can_act, use_container_width=True)
    # After a buy or a save the whole page reruns, so cash, stock and the other parts are current.
    if buy_clicked:
        try:
            bought = logic.buy_tournament_stock_many(DB_PATH, player, tournament_id, {product: int(value) for product, value in quantities.items()})
            flash(f"t{tournament_id}_buy", f"Stock purchased for €{bought['cost']:.2f}.", kind="toast")
            st.session_state[f"t{tournament_id}_buy_round"] = buy_round + 1
            st.rerun()
        except (ValueError, db.DatabaseUnavailable) as error:
            notice("error", friendly_error(error))
    if save_clicked:
        if not changed:
            notice("info", "No price changed.")
        else:
            try:
                logic.set_tournament_prices(DB_PATH, player, tournament_id, changed)
                flash(f"t{tournament_id}_price", "Prices updated.", kind="toast")
                st.rerun()
            except (ValueError, db.DatabaseUnavailable) as error:
                notice("error", friendly_error(error))



# Each tournament card is a fragment: its buttons rerun only this card.
@st.fragment
def tournament_card(tournament_id, player):
    try:
        # Simulated weather per tournament day (specs/feature-tournament-clarity.md).
        screen = logic.tournament_screen(DB_PATH, player, tournament_id)
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
    own = screen["stand"]  # None for an organiser who does not play
    is_ready = bool(own and own["ready"])
    playing = screen["day"] <= logic.RUN_DAYS
    can_act = own is not None and playing and not is_ready
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
                st.rerun()

        weather_tints = {
            "rain": ("rgba(96,165,250,0.30)", "rgba(30,64,175,0.15)"),
            "hot": ("rgba(255,122,24,0.40)", "rgba(239,68,68,0.20)"),
            "normal": ("rgba(255,236,210,0.18)", "rgba(245,165,36,0.12)"),
        }
        tint_start, tint_end = weather_tints[weather_name]
        effect = {
            "rain": "Café reference €5.00 today",
            "hot": "Water reference €1.50 today",
            "normal": "no change to the reference prices",
        }[weather_name]
        if own is not None and playing:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:20px;padding:18px 22px;margin:12px 0;'
                f'background:linear-gradient(120deg,{tint_start},{tint_end});border:1px solid rgba(255,255,255,.18);'
                f'border-radius:20px;backdrop-filter:blur(18px)">{icon(weather_icon, 48)}'
                f'<div><div style="font-size:1.35rem;font-weight:800">Day {screen["day"]} weather: {html.escape(weather_label)}</div>'
                f'<div style="color:var(--muted)">{html.escape(effect)}</div></div></div>',
                unsafe_allow_html=True,
            )

        show_flash(f"t{tournament_id}_buy")
        show_flash(f"t{tournament_id}_price")
        show_flash(f"t{tournament_id}_upgrade")
        show_flash(f"t{tournament_id}_ready")
        show_flash(f"t{tournament_id}_close")
        show_flash(f"t{tournament_id}_join")

        if own is None:
            # An organiser who has not joined: no weather and no parts 1-3, only a way to join.
            st.markdown(
                f'<div class="part-caption">You created this tournament. Share the code '
                f'<b>{html.escape(screen["code"])}</b> with the players, or join it yourself to play.</div>',
                unsafe_allow_html=True,
            )
            if playing and st.button("Join this tournament", key=f"t{tournament_id}_join_button", icon=":material/login:", type="primary"):
                try:
                    joined = logic.join_tournament(DB_PATH, player, screen["code"])
                    flash(f"t{tournament_id}_join", f"You joined {joined['name']} in seat {joined['seat']}.")
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))
        elif playing:
            if screen["days"]:
                # Results first: what happened on the last closed day.
                with st.container(border=True, key=f"tournament_part_latest_{tournament_id}"):
                    st.markdown(f'<div class="part-heading">Day {screen["days"][-1]["day"]} results</div>', unsafe_allow_html=True)
                    show_results(screen, player, charts_open=False)
            references = logic.stand_references(today_weather, owned)
            with st.container(border=True, key=f"tournament_part_money_{tournament_id}"):
                part_heading(1, "Your day and money")
                cash_column, progress_column, players_column, upgrade_column = st.columns(4)
                with cash_column:
                    with st.container(border=True, key=f"tournament_box_cash_{tournament_id}"):
                        money_box("Cash", f"€{own['cash']:.2f}", "Tournament cash")
                with progress_column:
                    with st.container(border=True, key=f"tournament_box_progress_{tournament_id}"):
                        money_box("Progress", f"Day {screen['day']} of {logic.RUN_DAYS}" if playing else "Complete", "Tournament day")
                with players_column:
                    with st.container(border=True, key=f"tournament_box_players_{tournament_id}"):
                        ready_count = sum(1 for row in screen["players"] if row["ready"])
                        money_box("Players ready", f"{ready_count}/{len(screen['players'])}", "Ready to close the day")
                with upgrade_column:
                    with st.container(border=True, key=f"tournament_box_upgrade_{tournament_id}"):
                        machine = next(iter(logic.UPGRADES))
                        details = logic.UPGRADES[machine]
                        money_box(
                            "Coffee machine", "Owned" if machine in owned else f"€{details['cost']:.2f}",
                            f"One time: your Café reference becomes €{details['reference_price']:.2f} for the rest of the "
                            f"tournament (customers pay up to €{details['reference_price']:.2f} / €{2 * details['reference_price']:.2f}).",
                        )
                        if machine not in owned and can_act and st.button(f"Buy {machine}", key=f"t{tournament_id}_upgrade_button", icon=":material/upgrade:", use_container_width=True):
                            try:
                                logic.buy_tournament_upgrade(DB_PATH, player, tournament_id, machine)
                                flash(f"t{tournament_id}_upgrade", "Upgrade purchased.")
                                st.rerun()
                            except (ValueError, db.DatabaseUnavailable) as error:
                                notice("error", friendly_error(error))

            # 2. Plan the day. Its fields are a small fragment, so the total cost shows while typing.
            with st.container(border=True, key=f"tournament_part_plan_{tournament_id}"):
                part_heading(2, f"Plan day {screen['day']}")
                st.markdown(
                    f'<div class="plan-rule"><span class="plan-rule-icon">{icon("info", 16)}</span>Customers per day: '
                    "<b>10</b> per player and product · half pay up to the reference price, half up to twice it · "
                    "the cheapest stand sells first.</div>",
                    unsafe_allow_html=True,
                )
                tournament_plan(tournament_id, player, own, references, can_act)
            # 3. Ready and Close day now are one small form: pressing one never sends the other.
            with st.form(f"t{tournament_id}_trade_form", border=False, enter_to_submit=False):
                with st.container(border=True, key=f"tournament_part_trade_{tournament_id}"):
                    part_heading(3, f"Trade day {screen['day']}")
                    st.markdown('<div class="part-caption">Press Ready when your stock and prices are set. The day closes when every player is Ready (or the organiser closes it), then the shared market decides the sales.</div>', unsafe_allow_html=True)
                    if can_act:
                        for warning in logic.trade_warnings(own["stock"], own["price"], references):
                            notice("warning", warning)
                        ready_submitted = st.form_submit_button("Ready", key=f"t{tournament_id}_ready_button", icon=":material/check:", type="primary", use_container_width=True)
                    else:
                        ready_submitted = False
                    if ready_submitted:
                        try:
                            result = logic.ready_tournament(DB_PATH, player, tournament_id)
                            if result["closed_day"]:
                                flash(f"t{tournament_id}_ready", result["closed_day"], kind="closed_day")
                            else:
                                flash(f"t{tournament_id}_ready", "You are Ready.")
                            st.rerun()
                        except (ValueError, db.DatabaseUnavailable) as error:
                            notice("error", friendly_error(error))
                    elif is_ready and playing:
                        notice("info", "You are Ready. Waiting for the other players.")
                    show_players(screen)
                    if player == screen["organiser"] and playing:
                        close_submitted = st.form_submit_button("Close day now", key=f"t{tournament_id}_close_button", icon=":material/lock_clock:", use_container_width=True)
                        if close_submitted:
                            try:
                                closed_day = logic.close_tournament_day(DB_PATH, player, tournament_id)
                                flash(f"t{tournament_id}_close", closed_day, kind="closed_day")
                                st.rerun()
                            except (ValueError, db.DatabaseUnavailable) as error:
                                notice("error", friendly_error(error))
        if own is None:
            # 3. The organiser who does not play: who is ready, and Close day now.
            with st.container(border=True, key=f"tournament_part_trade_{tournament_id}"):
                part_heading(3, f"Day {screen['day']}" if playing else "Tournament complete")
                st.markdown('<div class="part-caption">The day closes when every player is Ready, or when you close it now.</div>', unsafe_allow_html=True)
                show_players(screen)
                if playing and st.button("Close day now", key=f"t{tournament_id}_close_button", icon=":material/lock_clock:", use_container_width=True):
                    try:
                        closed_day = logic.close_tournament_day(DB_PATH, player, tournament_id)
                        flash(f"t{tournament_id}_close", closed_day, kind="closed_day")
                        st.rerun()
                    except (ValueError, db.DatabaseUnavailable) as error:
                        notice("error", friendly_error(error))

        # 4. Results: at the end of the tournament (ranking first), or for the organiser who does not play.
        if not playing or own is None:
            with st.container(border=True, key=f"tournament_part_results_{tournament_id}"):
                part_heading(4, "Final results" if not playing else "Results")
                show_ranking(screen)
                show_results(screen, player, charts_open=not playing)


def show_ranking(screen):
    # Podium order: gain first (CT R4), then seat.
    if screen["ranking"] is not None:
        st.markdown('<div class="section-heading">Ranking</div>', unsafe_allow_html=True)
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


def open_tournament(tournament_id):
    # The open tournament lives in the address (?page=tournaments&tournament=<id>), so a reload stays on it.
    st.query_params["page"] = "tournaments"
    if tournament_id is None:
        st.query_params.pop("tournament", None)
    else:
        st.query_params["tournament"] = str(tournament_id)


def tournament_row(row):
    # One running tournament in the list: name, code, day, the player's role, and Open.
    if row["playing"]:
        status = "Playing · Ready" if row.get("ready") else "Playing · Not ready"
    else:
        status = "Organiser"
    with st.container(border=True, key=f"tournament_row_{row['id']}"):
        text_column, open_column = st.columns([5, 1], vertical_alignment="center")
        with text_column:
            st.markdown(
                f'<div class="tournament-row"><span class="tournament-row-name">{html.escape(str(row["name"]))}</span>'
                f'<span class="code-badge">{html.escape(str(row["code"]))}</span>'
                f'<span class="tournament-row-meta">Day {row["day"]} of {logic.RUN_DAYS} · {status}</span></div>',
                unsafe_allow_html=True,
            )
        with open_column:
            st.button("Open", key=f"tournament_open_{row['id']}", icon=":material/arrow_forward:", type="primary",
                      use_container_width=True, on_click=open_tournament, args=(row["id"],))


def tournaments_screen():
    try:
        # Joined and organised tournaments: an organiser who does not play still sees theirs.
        my_stands = logic.tournament_list(DB_PATH, PLAYER)
    except (ValueError, db.DatabaseUnavailable) as error:
        notice("error", friendly_error(error))
        my_stands = []

    # One tournament open: only its card, and a way back to the list.
    opened = logic.find_tournament(my_stands, st.query_params.get("tournament"))
    if opened is not None:
        st.button("All tournaments", key="tournaments_back_button", icon=":material/arrow_back:",
                  on_click=open_tournament, args=(None,))
        message = st.session_state.pop("tournament_message", None)
        if message:
            notice("success", message)
        tournament_card(opened["id"], PLAYER)
        return

    create_column, join_column = st.columns(2)
    with create_column:
        with st.container(border=True):
            section_heading("trophy", "Create a tournament")
            tournament_name = st.text_input("Tournament name", key="tournament_name")
            if st.button("Create tournament", key="tournament_create_button", type="primary", icon=":material/add_circle:", use_container_width=True):
                try:
                    created = logic.create_tournament(DB_PATH, PLAYER, tournament_name)
                    st.session_state["tournament_message"] = (
                        f"Tournament created: {created['name']}. Share the code {created['code']} with the players."
                    )
                    open_tournament(created["id"])
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))

    with join_column:
        with st.container(border=True):
            section_heading("users", "Join a tournament")
            join_code = st.text_input("Join code", key="tournament_join_code")
            if st.button("Join tournament", key="tournament_join_button", icon=":material/login:", use_container_width=True):
                try:
                    joined = logic.join_tournament(DB_PATH, PLAYER, join_code)
                    st.session_state["tournament_message"] = f"Joined {joined['name']} in seat {joined['seat']}."
                    open_tournament(joined["id"])
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    notice("error", friendly_error(error))

    active, finished = logic.split_tournaments(my_stands)
    if not my_stands:
        notice("info", "You have no tournaments yet. Create one or join one with a code.")
    if active:
        section_heading("trophy", "Tournaments in progress")
        for row in logic.newest_first(active):
            tournament_row(row)
    if finished:
        with st.expander(f"Finished tournaments ({len(finished)})"):
            for stand in logic.newest_first(finished):
                tournament_card(stand["id"], PLAYER)


def help_screen():
    help_content = [
        ("trophy", "Goal", "Finish five days with the highest gain."),
        ("clock", "Each day", "Buy stock, set prices, then trade one day."),
        ("trending-up", "Demand", "Demand per product per day: 10 units at or below its reference price, 5 units up to twice the reference price, 0 units above that."),
        ("wallet", "Loan", f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with {logic.LOAN_INTEREST:.0%} interest, which is subtracted from your final gain."),
    ]
    upgrade_cost = next(details["cost"] for details in logic.UPGRADES.values())
    help_content.append(("users", "Tournaments", "Create a tournament and share its join code, or join one with a code. All players share the same customers: 10 per player and product each day, half budget (they pay up to the reference price) and half premium (up to twice it). The cheapest stand sells first."))
    help_content.append(("cloud-sun", "A tournament day", "Buy stock and set prices, then press Ready. The day closes when everyone is Ready or the organiser presses Close day now. Press Refresh to see who is ready. After each day, Market results show every stand's price and units sold. Rain raises the Café reference to €5.00, heat raises Water to €1.50, and the Coffee machine (€" + f"{upgrade_cost:.2f}" + ") raises your Café reference to €5.00: each card shows your reference today."))
    levels = ", ".join(f"{name} €{cash:.0f}" for name, cash in logic.DIFFICULTY_LEVELS.items())
    help_content.append(("trophy", "Final gain", "After day 5: final cash + leftover stock valued at its unit cost − the cash you started with − the loan to repay. The ranking of a tournament uses the same gain (tournaments have no loans)."))
    help_content.append(("box", "Difficulty", f"Practice runs start with different cash: {levels}. The rules are the same; less cash means fewer units you can buy on day 1."))
    # Row by row (two cards per row), so on a phone the cards keep the reading order.
    for row_start in range(0, len(help_content), 2):
        help_columns = st.columns(2)
        for column, (glyph, heading, body) in zip(help_columns, help_content[row_start:row_start + 2]):
            with column:
                with st.container(border=True, key=f"help_section_{heading}"):
                    st.markdown(f'<div class="section-heading">{icon(glyph)} {heading}</div>', unsafe_allow_html=True)
                    st.write(body)


# The home page cards: page value, icon, title, sentence, button icon.
HOME_CARDS = [
    ("practice", "coffee", "Practice", "Play a five-day run on your own", ":material/storefront:"),
    ("tournaments", "trophy", "Tournaments", "Compete for the same customers with other players", ":material/emoji_events:"),
    ("help", "info", "How to play", "The rules in two minutes", ":material/help:"),
]
PAGES = [card[0] for card in HOME_CARDS]


def open_page(page):
    # The open screen lives in the address (?page=...), so a reload stays on it.
    st.query_params.pop("tournament", None)
    if page in PAGES:
        st.query_params["page"] = page
    else:
        st.query_params.pop("page", None)


def current_page():
    # No value or an unknown value means the home page.
    page = st.query_params.get("page", "home")
    return page if page in PAGES else "home"


def home_screen():
    columns = st.columns(3)
    for column, (page, glyph, title, text, button_icon) in zip(columns, HOME_CARDS):
        with column:
            with st.container(border=True, key=f"home_card_{page}"):
                st.markdown(
                    f'<div class="home-card-body"><div class="home-card-icon">{icon(glyph, 34)}</div>'
                    f'<div class="home-card-title">{title}</div>'
                    f'<div class="home-card-text">{text}</div></div>',
                    unsafe_allow_html=True,
                )
                st.button(f"Open {title}", key=f"home_open_{page}", type="primary", icon=button_icon,
                          use_container_width=True, on_click=open_page, args=(page,))


def home_button():
    st.button("Home", key="home_button", icon=":material/home:", on_click=open_page, args=("home",))


# Only the open screen is built.
page = current_page()
if page == "practice":
    home_button()
    practice_screen()
elif page == "tournaments":
    home_button()
    tournaments_screen()
elif page == "help":
    home_button()
    help_screen()
else:
    home_screen()
