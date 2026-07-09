"""
ui.py  —  Shared look & feel for the UberThinking dashboard
-----------------------------------------------------------
One place for the color palette, global CSS, icon set, header, KPI cards,
chart styling, tables, and the sidebar. Every page imports this so the three
pages stay consistent.

Nothing here touches the data pipeline — it's presentation only.
"""

from __future__ import annotations

import html
from contextlib import contextmanager

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- Palette (neutral SaaS base, refined taxi-amber accent) ----------------
NAVY = "#161A2B"        # headings / strong text
SLATE = "#64748B"       # muted / secondary text
SLATE_LIGHT = "#94A3B8"
CARD = "#FFFFFF"
PAGE_BG = "#F7F8FA"
SOFT_BG = "#F3F5F9"
BORDER = "#E6E9F0"
GRID = "#EEF1F6"        # very light chart gridlines

AMBER = "#DE9A0E"       # primary accent — refined taxi amber
AMBER_BRIGHT = "#EBAE3A"  # chart fills (a touch brighter so bars read well)
AMBER_DEEP = "#9A6A05"   # amber text that still passes contrast
AMBER_SOFT = "#FBF3DE"   # very soft pale yellow — icon chips, active nav, tints

GREEN = "#16A34A"       # live / positive status only
TEAL = "#14B8A6"
CORAL = "#F4785A"
PURPLE = "#8B7CF6"

# Categorical order — amber leads as the brand accent, rest are neutral/varied.
CHART_COLORS = [AMBER_BRIGHT, NAVY, TEAL, SLATE_LIGHT, CORAL, PURPLE]


def _register_plotly_template() -> None:
    """A shared Plotly template so all charts feel like one product."""
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        font=dict(family="Inter, Segoe UI, system-ui, sans-serif",
                  color=NAVY, size=13),
        colorway=CHART_COLORS,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=14, r=18, t=20, b=14),
        title=dict(font=dict(size=14, color=NAVY, family="Inter, sans-serif"),
                  x=0.0, xanchor="left"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=SLATE, size=12)),
        xaxis=dict(gridcolor="#F4F6FA", zerolinecolor="#F4F6FA", gridwidth=1,
                   showgrid=False, linecolor="rgba(0,0,0,0)",
                   tickfont=dict(color=SLATE_LIGHT),
                   title=dict(font=dict(color=SLATE, size=12))),
        yaxis=dict(gridcolor="#F4F6FA", zerolinecolor="#F4F6FA", gridwidth=1,
                   linecolor="rgba(0,0,0,0)", tickfont=dict(color=SLATE_LIGHT),
                   title=dict(font=dict(color=SLATE, size=12))),
        hoverlabel=dict(bgcolor="white", bordercolor=BORDER,
                        font=dict(color=NAVY, family="Inter, sans-serif")),
    )
    pio.templates["uber"] = tpl


def style_fig(fig, height: int | None = None, showlegend: bool | None = None):
    """Applies the shared template to any Plotly figure and returns it."""
    fig.update_layout(template="uber")
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        autosize=True,
        margin=dict(l=60, r=55, t=45, b=60),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)

    if height is not None:
        fig.update_layout(height=height)

    if showlegend is not None:
        fig.update_layout(showlegend=showlegend)

    return fig


def chart(fig, height: int | None = None, showlegend: bool | None = None) -> None:
    """Render a styled Plotly figure inside a card, with the toolbar visible."""
    st.plotly_chart(
        style_fig(fig, height, showlegend),
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "responsive": True,
        },
    )


# --- Icon set (thin-stroke line icons, Lucide/Feather style, one color family) ---
_ICONS: dict[str, str] = {
    "grid": '<rect x="3" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6"/>',
    "bar-chart": '<path d="M4 20h16"/><rect x="6" y="11" width="3" height="7" rx="0.6" fill="currentColor" stroke="none"/><rect x="10.5" y="6" width="3" height="12" rx="0.6" fill="currentColor" stroke="none"/><rect x="15" y="13.5" width="3" height="4.5" rx="0.6" fill="currentColor" stroke="none"/>',
    "zap": '<path d="M12.7 2 4 13.2h6.2L10.4 22 20 9.8h-6.4L12.7 2Z" fill="currentColor" stroke="none"/>',
    "car": '<path d="M4.5 16 6 10.8c.35-1.15 1.4-1.95 2.6-1.95h6.8c1.2 0 2.25.8 2.6 1.95L19.5 16"/><rect x="3" y="16" width="18" height="4" rx="1.4"/><circle cx="7.6" cy="20" r="1.5" fill="currentColor" stroke="none"/><circle cx="16.4" cy="20" r="1.5" fill="currentColor" stroke="none"/>',
    "wallet": '<rect x="3" y="6.5" width="18" height="12" rx="2"/><path d="M3 10.5h13.5a3 3 0 0 1 3 3v1"/><circle cx="16.7" cy="14" r="1.1" fill="currentColor" stroke="none"/>',
    "receipt": '<path d="M6 3h12v18l-2.2-1.4L13.8 21l-1.8-1.4L10.2 21 8.4 19.6 6 21V3Z"/><path d="M9 8.2h6M9 12h6M9 15.8h4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.7V12l3 2"/>',
    "map-pin": '<path d="M12 21s-6.5-5.7-6.5-11.2A6.5 6.5 0 0 1 18.5 9.8C18.5 15.3 12 21 12 21Z"/><circle cx="12" cy="9.7" r="2.2"/>',
    "route": '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h6.5A3 3 0 0 0 17.5 16v-1a3 3 0 0 0-3-3H9a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3h1"/>',
    "activity": '<path d="M3 12h4l2 7 4-14 2 7h6"/>',
    "refresh": '<path d="M4.5 12a7.5 7.5 0 0 1 13-5.1M19.5 12a7.5 7.5 0 0 1-13 5.1"/><path d="M17.2 3.4v4h-4"/><path d="M6.8 20.6v-4h4"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 8.2h.01"/><path d="M11 11.2h1.2v5.3"/>',
    "dollar": '<path d="M12 2.5v19"/><path d="M16.6 7.1c0-1.9-2.1-3.1-4.6-3.1s-4.6 1.2-4.6 3 2.1 2.6 4.6 3 4.6 1.3 4.6 3.1-2.1 3.1-4.6 3.1-4.6-1.2-4.6-3.1"/>',
    "users": '<circle cx="9" cy="8" r="3.1"/><path d="M3.2 20c0-3.3 2.6-6 5.8-6s5.8 2.7 5.8 6"/><circle cx="17.3" cy="9" r="2.3"/><path d="M15.8 14.2a5 5 0 0 1 4.5 6"/>',
    "cpu": '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/><path d="M9.5 3v3M14.5 3v3M9.5 18v3M14.5 18v3M3 9.5h3M3 14.5h3M18 9.5h3M18 14.5h3"/><rect x="10" y="10" width="4" height="4" rx="0.6" fill="currentColor" stroke="none"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M8 12.4l2.6 2.6 5.4-6.2"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor",
         stroke_width: float = 1.7) -> str:
    """Inline SVG for one of the line icons above."""
    body = _ICONS.get(name, "")
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" '
            f'stroke-linejoin="round" style="display:block;flex-shrink:0">{body}</svg>')


# --- Global CSS ------------------------------------------------------------
_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --uk-navy: {NAVY};
  --uk-slate: {SLATE};
  --uk-border: {BORDER};
  --uk-soft: {SOFT_BG};
  --uk-amber: {AMBER};
}}

html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }}
.stApp {{ background: {PAGE_BG}; }}

/* Roomier but bounded main container. Top padding clears the fixed header
   so the first section is never tucked under it / clipped. */
.block-container {{
  padding-top: 2.9rem; padding-bottom: 2.6rem;
  max-width: 1120px;
}}

/* Hide Streamlit's default multipage nav + chrome we replace */
[data-testid="stSidebarNav"] {{ display: none; }}
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
/* Transparent top bar so nothing is masked or clipped at the very top */
[data-testid="stHeader"] {{ background: transparent; }}

/* Consistent, breathable spacing between stacked sections */
[data-testid="stVerticalBlock"] {{ gap: 1.25rem; }}

h1, h2, h3 {{ color: var(--uk-navy); font-weight: 700; letter-spacing: -0.01em; }}

/* --- Header block (icon + title + subtitle), lives inside a card --- */
.uk-head {{ display: flex; align-items: center; gap: .85rem; }}
.uk-head-icon {{
  width: 42px; height: 42px; border-radius: 11px;
  background: {AMBER_SOFT}; color: {AMBER};
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.uk-head-title {{ color: {NAVY}; font-size: 1.4rem; font-weight: 750; line-height: 1.15; }}
.uk-head-sub {{ color: {SLATE}; font-size: .88rem; margin-top: .15rem; }}

/* Right-side header cluster (status + last updated) */
.uk-toolbar {{
  display: flex; align-items: center; justify-content: flex-end;
  flex-wrap: wrap; gap: .5rem; margin-bottom: .55rem;
}}
.uk-chip {{
  display: inline-flex; align-items: center; gap: .4rem;
  padding: .3rem .65rem; background: {SOFT_BG}; color: {NAVY};
  font-weight: 600; font-size: .75rem; border-radius: 999px;
  border: 1px solid var(--uk-border); white-space: nowrap;
}}
.uk-chip.live {{ color: {GREEN}; background: {GREEN}12; border-color: {GREEN}33; }}
.uk-chip.amber {{ color: {AMBER_DEEP}; background: {AMBER_SOFT}; border-color: {AMBER}44; }}
.uk-chip.ghost {{ background: transparent; border-color: transparent; color: {SLATE}; padding-left: .2rem; }}
.uk-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.uk-dot.live {{ background: {GREEN}; box-shadow: 0 0 0 3px {GREEN}22; }}
.uk-dot.idle {{ background: {SLATE_LIGHT}; box-shadow: 0 0 0 3px {SLATE_LIGHT}22; }}

/* --- KPI cards (small versions of the chart cards) --- */
.uk-kpi {{
  background: #FFFFFF; border: 1px solid #DDE3EC;
  border-radius: 12px; padding: .9rem 1rem;
  box-shadow: 0 1px 2px rgba(22,26,43,0.04);
  height: 100%; min-height: 138px; box-sizing: border-box;
  display: flex; flex-direction: column;
  transition: box-shadow .15s ease, border-color .15s ease;
}}
.uk-kpi:hover {{ box-shadow: 0 4px 14px rgba(22,26,43,0.08); border-color: #CDD5E2; }}
.uk-kpi .uk-ico {{
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: .5rem; background: {AMBER_SOFT}; color: {AMBER};
}}
.uk-kpi .uk-label {{
  color: var(--uk-slate); font-size: .7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .05em;
}}
.uk-kpi .uk-value {{
  color: var(--uk-navy); font-size: 1.45rem; font-weight: 700;
  line-height: 1.2; margin-top: .1rem; font-feature-settings: "tnum";
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.uk-kpi .uk-sub {{ color: var(--uk-slate); font-size: .75rem; margin-top: .2rem; }}
.uk-kpi .uk-sub.pos {{ color: {GREEN}; font-weight: 600; }}

/* Section title (inside cards) */
.uk-section {{
  display: flex; align-items: center; gap: .45rem;
  font-size: .92rem; font-weight: 650; color: var(--uk-navy);
  margin: 0 0 .6rem;
}}
.uk-section .uk-ico {{ color: {SLATE}; display: flex; }}

/* Pure-HTML card (used for content that is already HTML: tables, results) */
.uk-card {{
  background: {CARD}; border: 1px solid var(--uk-border);
  border-radius: 12px; box-shadow: 0 1px 2px rgba(22,26,43,0.04);
  padding: 1.05rem 1.15rem;
}}

/* Form card — specific + safe (forms only) */
div[data-testid="stForm"] {{
  background: {CARD}; border: 1px solid var(--uk-border);
  border-radius: 12px; box-shadow: 0 1px 2px rgba(22,26,43,0.04);
  padding: 1.15rem 1.25rem;
}}

/* Keep Plotly charts sized to their container (no overflow, no clipping) */
[data-testid="stPlotlyChart"] {{
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  padding: 0.25rem 0.25rem 0;
}}
[data-testid="stPlotlyChart"] > div {{
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}}

/* Buttons — controlled: primary navy, secondary outline w/ amber hover */
.stButton > button, .stFormSubmitButton > button {{
  border-radius: 8px; font-weight: 600; padding: .45rem 1rem;
  border: 1px solid var(--uk-border); background: {CARD}; color: {NAVY};
  box-shadow: none; transition: border-color .15s ease, color .15s ease, background .15s ease;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{
  border-color: {AMBER}; color: {AMBER_DEEP}; background: {AMBER_SOFT};
}}
button[kind="primary"], button[kind="primaryFormSubmit"] {{
  background: {NAVY} !important; color: #fff !important; border: 1px solid {NAVY} !important;
}}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {{
  background: #262C48 !important; border-color: #262C48 !important; color: #fff !important;
}}

/* Inputs — flatten default chrome, amber focus */
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input,
.stSelectbox > div > div, [data-baseweb="select"] > div {{
  border-radius: 8px !important; border-color: var(--uk-border) !important;
}}
[data-testid="stSlider"] [role="slider"] {{ background: {AMBER}; }}

/* --- Custom recent-rides table --- */
.uk-table {{ width: 100%; border-collapse: collapse; font-size: .84rem; }}
.uk-table thead th {{
  text-align: left; color: {SLATE}; font-weight: 600; font-size: .7rem;
  text-transform: uppercase; letter-spacing: .05em;
  padding: 0 .6rem .55rem; border-bottom: 1px solid var(--uk-border);
}}
.uk-table thead th.num, .uk-table td.num {{ text-align: right; font-feature-settings: "tnum"; }}
.uk-table tbody td {{
  padding: .5rem .6rem; color: {NAVY};
  border-bottom: 1px solid {GRID};
}}
.uk-table tbody tr:last-child td {{ border-bottom: none; }}
.uk-table tbody tr:hover td {{ background: {SOFT_BG}; }}
.uk-table .muted {{ color: {SLATE}; }}

/* --- Prediction result (single card; amber block is a tint, not a frame) --- */
.uk-result {{ display: flex; gap: 1.1rem; flex-wrap: wrap; align-items: stretch; }}
.uk-result-main {{
  flex: 1 1 200px; background: {AMBER_SOFT};
  border-radius: 10px;
  padding: 1rem 1.15rem; display: flex; flex-direction: column; justify-content: center;
}}
.uk-result-main .lbl {{
  color: {AMBER_DEEP}; font-size: .72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .06em;
}}
.uk-result-main .val {{
  color: {NAVY}; font-size: 2.5rem; font-weight: 800; line-height: 1.05;
  margin: .2rem 0 .4rem; font-feature-settings: "tnum";
}}
.uk-result-main .route {{
  display: inline-flex; align-items: center; gap: .4rem;
  color: {NAVY}; font-size: .9rem; font-weight: 600;
}}
.uk-result-main .route svg {{ color: {AMBER}; }}
.uk-result-grid {{
  flex: 1 1 300px; display: grid; grid-template-columns: 1fr 1fr;
  gap: .1rem .4rem; align-content: center;
}}
.uk-detail {{
  display: flex; justify-content: space-between; align-items: center;
  padding: .5rem .2rem; border-bottom: 1px solid {GRID};
}}
.uk-detail .k {{ color: {SLATE}; font-size: .8rem; }}
.uk-detail .v {{ color: {NAVY}; font-size: .86rem; font-weight: 600; font-feature-settings: "tnum"; }}
.uk-result-note {{ color: {SLATE_LIGHT}; font-size: .76rem; margin-top: .85rem; }}

/* Empty-state hint */
.uk-hint {{
  display: flex; align-items: center; gap: .6rem;
  color: {SLATE}; font-size: .88rem; padding: 1.4rem 1.25rem;
  background: {CARD}; border: 1px dashed {BORDER}; border-radius: 12px;
}}
.uk-hint .ic {{ color: {AMBER}; display: flex; }}

/* --- Sidebar --- */
[data-testid="stSidebar"] {{ background: {CARD}; border-right: 1px solid var(--uk-border); }}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 1.1rem; }}
.uk-brand {{ display:flex; align-items:center; gap:.6rem; padding: 0 .2rem .9rem; }}
.uk-brand .logo {{
  width: 34px; height: 34px; border-radius: 9px; background: {AMBER};
  display:flex; align-items:center; justify-content:center; color: #fff; flex-shrink: 0;
}}
.uk-brand .name {{ font-weight: 700; font-size: 1.02rem; color: {NAVY}; line-height:1.2; }}
.uk-brand .tag {{ font-size: .72rem; color: {SLATE}; }}

.uk-nav {{ display: flex; flex-direction: column; gap: .12rem; padding: 0 .1rem; }}
.uk-nav a.uk-nav-item {{
  display: flex; align-items: center; gap: .6rem;
  padding: .48rem .6rem; border-radius: 8px;
  color: {SLATE}; font-weight: 550; font-size: .88rem;
  text-decoration: none; border-left: 2px solid transparent;
}}
.uk-nav a.uk-nav-item:hover {{ background: {SOFT_BG}; color: {NAVY}; }}
.uk-nav a.uk-nav-item.active {{
  background: {AMBER_SOFT}; color: {NAVY}; border-left: 2px solid {AMBER}; font-weight: 650;
}}
.uk-nav a.uk-nav-item.active .uk-ico {{ color: {AMBER}; }}
.uk-nav a.uk-nav-item .uk-ico {{ display: flex; }}

.uk-sb-label {{
  color: {SLATE_LIGHT}; font-size: .68rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .07em; padding: 1.1rem .6rem .4rem;
}}
.uk-status {{
  display:flex; align-items:center; gap:.55rem; font-size:.79rem;
  color:{SLATE}; font-weight: 550; padding:.55rem .7rem; background:{SOFT_BG};
  border:1px solid var(--uk-border); border-radius:9px; margin: .1rem .1rem 0;
}}
.uk-status .val {{ color: {NAVY}; font-weight: 700; }}

/* Footer */
.uk-footer {{
  color: {SLATE_LIGHT}; font-size: .76rem; text-align:center;
  padding: 1.1rem 0 .1rem; margin-top: 1.2rem; border-top: 1px solid var(--uk-border);
}}
</style>
"""


def setup(active: str = "") -> None:
    """Call once at the top of every page: inject CSS, template, sidebar."""
    _register_plotly_template()
    st.markdown(_CSS, unsafe_allow_html=True)
    _sidebar(active)


def _nav_item(href: str, label: str, ico: str, active: bool) -> str:
    cls = "uk-nav-item active" if active else "uk-nav-item"
    return (f'<a class="{cls}" href="{href}" target="_self">'
            f'<span class="uk-ico">{icon(ico, 17)}</span><span>{label}</span></a>')


def _sidebar(active: str) -> None:
    with st.sidebar:
        st.markdown(
            '<div class="uk-brand">'
            f'<div class="logo">{icon("car", 17, color="#fff", stroke_width=1.9)}</div>'
            '<div><div class="name">UberThinking</div>'
            '<div class="tag">Real-time taxi analytics</div></div></div>'
            '<div class="uk-sb-label">Menu</div>'
            '<div class="uk-nav">'
            + _nav_item("/", "Dashboard", "grid", active == "dashboard")
            + _nav_item("/Analytics", "Analytics", "bar-chart", active == "analytics")
            + _nav_item("/Prediction", "Fare Prediction", "zap", active == "prediction")
            + "</div>",
            unsafe_allow_html=True,
        )


def _head_html(title: str, subtitle: str, icon_name: str) -> str:
    return (f'<div class="uk-head"><div class="uk-head-icon">{icon(icon_name, 20)}</div>'
            f'<div><div class="uk-head-title">{title}</div>'
            f'<div class="uk-head-sub">{subtitle}</div></div></div>')


def header(title: str, subtitle: str, icon_name: str = "grid",
           badge: str | None = None, live: bool = False,
           updated: str | None = None, refresh: bool = False) -> bool:
    """Page header inside a card. Optionally hosts a Refresh button on the
    right, next to the Live badge and a 'Last updated' timestamp.
    Returns True if Refresh was clicked."""
    clicked = False
    with card():
        cols = st.columns([6, 4], vertical_alignment="center")
        with cols[0]:
            st.markdown(_head_html(title, subtitle, icon_name), unsafe_allow_html=True)
        with cols[1]:
            chips = ""
            if live:
                chips += '<span class="uk-chip live"><span class="uk-dot live"></span>Live</span>'
            if updated:
                chips += f'<span class="uk-chip ghost">Last updated: {updated}</span>'
            if badge:
                chips += f'<span class="uk-chip amber">{badge}</span>'
            if chips:
                st.markdown(f'<div class="uk-toolbar">{chips}</div>', unsafe_allow_html=True)
            if refresh:
                clicked = st.button("Refresh", use_container_width=True)
    return clicked


def kpi_card(label: str, value: str, icon_name: str = "bar-chart", sub: str = "",
             sub_positive: bool = False) -> None:
    sub_cls = "uk-sub pos" if sub_positive else "uk-sub"
    sub_html = f'<div class="{sub_cls}">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="uk-kpi"><div class="uk-ico">{icon(icon_name, 16)}</div>'
        f'<div class="uk-label">{label}</div>'
        f'<div class="uk-value">{value}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section(title: str, icon_name: str | None = None) -> None:
    ico_html = f'<span class="uk-ico">{icon(icon_name, 16)}</span>' if icon_name else ""
    st.markdown(f'<div class="uk-section">{ico_html}<span>{title}</span></div>',
               unsafe_allow_html=True)


@contextmanager
def card():
    """A real bordered card (Streamlit's native container)."""
    with st.container(border=True):
        yield


def _section_html(title: str, icon_name: str | None = None) -> str:
    ico = f'<span class="uk-ico">{icon(icon_name, 16)}</span>' if icon_name else ""
    return f'<div class="uk-section">{ico}<span>{html.escape(title)}</span></div>'


def table_html(df: pd.DataFrame, numeric_cols: tuple[str, ...] = ()) -> str:
    """Build a polished HTML table (not the default grid) as a string."""
    heads = "".join(
        f'<th class="num">{html.escape(str(c))}</th>' if c in numeric_cols
        else f'<th>{html.escape(str(c))}</th>' for c in df.columns
    )
    rows = ""
    for _, r in df.iterrows():
        cells = ""
        for c in df.columns:
            cls = "num" if c in numeric_cols else ""
            cells += f'<td class="{cls}">{html.escape(str(r[c]))}</td>'
        rows += f"<tr>{cells}</tr>"
    return (f'<table class="uk-table"><thead><tr>{heads}</tr></thead>'
            f"<tbody>{rows}</tbody></table>")


def panel(title: str, body_html: str, icon_name: str | None = None) -> None:
    """A single pure-HTML card: title + arbitrary HTML body (no widget nesting)."""
    st.markdown(
        f'<div class="uk-card">{_section_html(title, icon_name)}{body_html}</div>',
        unsafe_allow_html=True,
    )


def result_card(fare: str, route_from: str, route_to: str,
                details: list[tuple[str, str]], note: str = "") -> None:
    """Premium prediction result as ONE self-contained card (no nested frames)."""
    grid = "".join(
        f'<div class="uk-detail"><span class="k">{html.escape(k)}</span>'
        f'<span class="v">{html.escape(v)}</span></div>' for k, v in details
    )
    note_html = f'<div class="uk-result-note">{html.escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="uk-card">'
        f'{_section_html("Prediction result", "check-circle")}'
        f'<div class="uk-result">'
        f'<div class="uk-result-main">'
        f'<div class="lbl">Estimated Fare</div>'
        f'<div class="val">{html.escape(fare)}</div>'
        f'<div class="route">{html.escape(route_from)} {icon("arrow-right", 15)} {html.escape(route_to)}</div>'
        f'</div>'
        f'<div class="uk-result-grid">{grid}</div>'
        f'</div>{note_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def hint(text: str, icon_name: str = "info") -> None:
    st.markdown(
        f'<div class="uk-hint"><span class="ic">{icon(icon_name, 18)}</span>'
        f'<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


def status(is_live: bool, count: int) -> None:
    """Data-freshness indicator, rendered under the sidebar 'Status' label."""
    dot = "live" if is_live else "idle"
    if count:
        body = f'<span class="val">{count:,}</span> rides processed'
    else:
        body = "Waiting for rides…"
    with st.sidebar:
        st.markdown(
            '<div class="uk-sb-label">Status</div>'
            f'<div class="uk-status"><span class="uk-dot {dot}"></span>{body}</div>',
            unsafe_allow_html=True,
        )


def footer() -> None:
    st.markdown(
        '<div class="uk-footer">UberThinking · Apache Spark Structured '
        'Streaming + MLlib</div>',
        unsafe_allow_html=True,
    )
