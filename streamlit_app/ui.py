from __future__ import annotations

from string import Template
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

CHART_COLORS = ["#3157d5", "#13a987", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#64748b"]


LIGHT_THEME = {
    "app_bg": "#f6f8fb",
    "surface": "#ffffff",
    "surface_alt": "#f9fafb",
    "sidebar_bg": "#fbfcfe",
    "border": "#d9e0ea",
    "border_soft": "#e5e7eb",
    "heading": "#111827",
    "body": "#374151",
    "muted": "#4b5563",
    "metric": "#111827",
    "accent": "#3157d5",
    "accent_hover": "#2448bb",
    "accent_soft": "#eef3ff",
    "success": "#047857",
    "warning": "#b45309",
    "chart_bg": "#ffffff",
    "grid": "#e5e7eb",
}

DARK_THEME = {
    "app_bg": "#0f172a",
    "surface": "#111827",
    "surface_alt": "#1f2937",
    "sidebar_bg": "#0b1220",
    "border": "#334155",
    "border_soft": "#1f2937",
    "heading": "#f9fafb",
    "body": "#e5e7eb",
    "muted": "#cbd5e1",
    "metric": "#ffffff",
    "accent": "#60a5fa",
    "accent_hover": "#93c5fd",
    "accent_soft": "#172554",
    "success": "#34d399",
    "warning": "#fbbf24",
    "chart_bg": "#111827",
    "grid": "#334155",
}


def theme_tokens(mode: str = "light") -> dict[str, str]:
    return DARK_THEME if mode == "dark" else LIGHT_THEME


def apply_theme(mode: str = "light") -> None:
    tokens = theme_tokens(mode)
    css = Template(
        """
        <style>
        :root {
            --copilot-bg: $app_bg;
            --copilot-surface: $surface;
            --copilot-surface-alt: $surface_alt;
            --copilot-sidebar: $sidebar_bg;
            --copilot-border: $border;
            --copilot-border-soft: $border_soft;
            --copilot-heading: $heading;
            --copilot-body: $body;
            --copilot-muted: $muted;
            --copilot-metric: $metric;
            --copilot-accent: $accent;
            --copilot-accent-hover: $accent_hover;
            --copilot-accent-soft: $accent_soft;
            --copilot-success: $success;
            --copilot-warning: $warning;
        }
        html, body, [class*="css"] {{
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--copilot-body) !important;
        }}
        .stApp {
            background: var(--copilot-bg);
            color: var(--copilot-body);
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            max-width: 1720px;
            padding-left: 2.4rem;
            padding-right: 2.4rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--copilot-heading) !important;
            font-weight: 750 !important;
            letter-spacing: 0 !important;
        }
        h1 {
            font-size: 2.15rem !important;
            line-height: 1.08 !important;
            margin-bottom: 0.3rem !important;
        }
        h2, h3 {
            margin-top: 1.25rem !important;
        }
        p, span, label, div, small {
            color: var(--copilot-body);
        }
        section[data-testid="stSidebar"] {
            background: var(--copilot-sidebar);
            border-right: 1px solid var(--copilot-border);
            width: 260px !important;
            min-width: 260px !important;
            left: 0 !important;
            transform: translateX(0) !important;
            translate: none !important;
            margin-left: 0 !important;
            opacity: 1 !important;
            visibility: visible !important;
            display: block !important;
            transition: transform 0.24s ease, width 0.24s ease, min-width 0.24s ease, opacity 0.24s ease;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1.25rem;
            padding-left: 1rem;
            padding-right: 1rem;
            width: 260px !important;
            left: 0 !important;
            transform: translateX(0) !important;
            translate: none !important;
            opacity: 1 !important;
            visibility: visible !important;
            transition: transform 0.24s ease, opacity 0.2s ease;
        }
        section[data-testid="stSidebar"] * {
            color: var(--copilot-body) !important;
        }
        section[data-testid="stSidebar"] input {
            background: var(--copilot-surface) !important;
            color: var(--copilot-heading) !important;
            border: 1px solid var(--copilot-border) !important;
            border-radius: 12px !important;
            min-height: 34px !important;
            font-size: 0.78rem !important;
            padding: 0.35rem 0.5rem !important;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: var(--copilot-body) !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label {
            color: var(--copilot-heading) !important;
            font-weight: 700 !important;
            padding: 0.48rem 0.55rem !important;
            margin: 0.18rem 0 !important;
            font-size: 0.9rem !important;
            border-radius: 12px !important;
            transition: background 0.15s ease, color 0.15s ease;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: var(--copilot-accent-soft) !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: var(--copilot-accent-soft) !important;
            border: 1px solid rgba(49, 87, 213, 0.18) !important;
        }
        section[data-testid="stSidebar"] [role="radio"] {
            color: var(--copilot-heading) !important;
        }
        section[data-testid="stSidebar"] button {
            background: var(--copilot-heading) !important;
            border: 1px solid var(--copilot-heading) !important;
            border-radius: 12px !important;
            min-height: 36px !important;
        }
        section[data-testid="stSidebar"] button p,
        section[data-testid="stSidebar"] button span {
            color: var(--copilot-surface) !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetric"] {
            background: var(--copilot-surface);
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] label p {
            color: var(--copilot-muted) !important;
            font-size: 0.86rem !important;
            font-weight: 650 !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] div,
        div[data-testid="stMetricValue"] span {
            color: var(--copilot-metric) !important;
            font-weight: 800 !important;
            opacity: 1 !important;
            font-size: 1.65rem !important;
        }
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            color: var(--copilot-muted) !important;
        }
        .stCaptionContainer,
        .stCaptionContainer p,
        div[data-testid="stCaptionContainer"],
        div[data-testid="stCaptionContainer"] p {
            color: var(--copilot-muted) !important;
            opacity: 1 !important;
        }
        .stMarkdown, .stMarkdown p, .stText, .stText p {
            color: var(--copilot-body) !important;
        }
        div[data-testid="stAlert"] {
            background: var(--copilot-accent-soft) !important;
            border: 1px solid var(--copilot-border) !important;
            color: var(--copilot-heading) !important;
        }
        div[data-testid="stAlert"] * {
            color: var(--copilot-heading) !important;
        }
        input, textarea, select {
            background: var(--copilot-surface) !important;
            color: var(--copilot-heading) !important;
            border: 1px solid var(--copilot-border) !important;
            border-radius: 12px !important;
        }
        input::placeholder, textarea::placeholder {
            color: var(--copilot-muted) !important;
            opacity: 1 !important;
        }
        div[data-baseweb="select"] * {
            color: var(--copilot-heading) !important;
        }
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border: 1px solid var(--copilot-border-soft);
            border-radius: 16px;
            overflow: hidden;
            background: var(--copilot-surface);
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.05);
        }
        div[data-testid="stDataFrame"] * {
            color: var(--copilot-heading) !important;
        }
        button[kind="primary"],
        div.stButton > button[kind="primary"] {
            background: var(--copilot-accent) !important;
            border: 1px solid var(--copilot-accent) !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            font-weight: 750 !important;
        }
        div.stButton > button {
            border-radius: 12px !important;
            font-weight: 700 !important;
            border: 1px solid var(--copilot-border) !important;
        }
        div.stButton > button:hover {
            border-color: var(--copilot-accent-hover) !important;
        }
        .cc-card {
            background: var(--copilot-surface);
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
        }
        .cc-eyebrow {
            color: var(--copilot-muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 4px;
            font-weight: 750;
        }
        .cc-title {
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--copilot-heading);
            margin-bottom: 6px;
        }
        .cc-body {
            color: var(--copilot-body);
            font-size: 0.94rem;
            line-height: 1.45;
        }
        .cc-pill {
            display: inline-block;
            border: 1px solid var(--copilot-border);
            border-radius: 999px;
            padding: 7px 11px;
            margin: 2px 4px 2px 0;
            font-size: 0.82rem;
            font-weight: 700;
            background: var(--copilot-accent-soft);
            color: var(--copilot-heading);
        }
        .cc-filter-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 0.25rem 0 1.2rem 0;
        }
        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.92);
        }
        .cc-topbar {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            margin-bottom: 0.25rem;
        }
        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            section[data-testid="stSidebar"] {
                width: 260px !important;
                min-width: 260px !important;
                box-shadow: 0 20px 48px rgba(15, 23, 42, 0.22);
            }
        }
        .cc-brand {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0.3rem 0 1.1rem 0;
        }
        .cc-logo {
            width: 36px;
            height: 36px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-weight: 900;
            background: linear-gradient(135deg, #3157d5, #13a987);
            box-shadow: 0 12px 26px rgba(49, 87, 213, 0.25);
        }
        .cc-brand-title {
            color: var(--copilot-heading);
            font-weight: 850;
            line-height: 1.1;
        }
        .cc-brand-subtitle {
            color: var(--copilot-muted);
            font-size: 0.78rem;
            margin-top: 2px;
        }
        .cc-compact-label {
            color: var(--copilot-muted);
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .cc-hero-card {
            background: linear-gradient(135deg, rgba(49, 87, 213, 0.1), rgba(19, 169, 135, 0.08)), var(--copilot-surface);
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
            margin-bottom: 18px;
        }
        .cc-kpi {
            background: var(--copilot-surface);
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            padding: 18px 19px;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
            min-height: 128px;
        }
        .cc-kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }
        .cc-kpi-label {
            color: var(--copilot-muted);
            font-size: 0.82rem;
            font-weight: 800;
        }
        .cc-kpi-icon {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: var(--copilot-accent-soft);
            color: var(--copilot-accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
        }
        .cc-kpi-value {
            color: var(--copilot-heading);
            font-size: 1.75rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 8px;
        }
        .cc-kpi-trend {
            color: var(--copilot-success, #047857);
            font-size: 0.82rem;
            font-weight: 800;
        }
        .cc-panel {
            background: var(--copilot-surface);
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
            margin-bottom: 18px;
        }
        .cc-panel-title {
            color: var(--copilot-heading);
            font-weight: 850;
            font-size: 1.05rem;
            margin-bottom: 0.35rem;
        }
        .cc-panel-subtitle {
            color: var(--copilot-muted);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .cc-summary {
            color: var(--copilot-body);
            font-size: 0.98rem;
            line-height: 1.55;
        }
        hr {
            border-color: var(--copilot-border-soft) !important;
        }
        </style>
        """
    ).substitute(tokens)
    st.markdown(
        css,
        unsafe_allow_html=True,
    )



def chart_template(mode: str = "light") -> str:
    return "plotly_dark" if mode == "dark" else "plotly_white"


def apply_chart_theme(fig, mode: str = "light"):
    tokens = theme_tokens(mode)
    fig.update_layout(
        template=chart_template(mode),
        paper_bgcolor=tokens["chart_bg"],
        plot_bgcolor=tokens["chart_bg"],
        font=dict(color=tokens["body"], family="Inter, Segoe UI, sans-serif", size=13),
        title=dict(font=dict(color=tokens["heading"], size=16)),
        xaxis=dict(
            gridcolor=tokens["grid"],
            linecolor=tokens["border"],
            tickfont=dict(color=tokens["body"]),
            title=dict(font=dict(color=tokens["body"])),
        ),
        yaxis=dict(
            gridcolor=tokens["grid"],
            linecolor=tokens["border"],
            tickfont=dict(color=tokens["body"]),
            title=dict(font=dict(color=tokens["body"])),
        ),
        legend=dict(font=dict(color=tokens["body"]), title=dict(font=dict(color=tokens["heading"]))),
    )
    return fig


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def brand_header() -> None:
    text_html = (
        '<div><div class="cc-brand-title">Campaign Copilot</div>'
        '<div class="cc-brand-subtitle">AI-native marketing CRM</div></div>'
    )
    st.sidebar.markdown(
        f"""
        <div class="cc-brand">
            <div class="cc-logo">C</div>
            {text_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def compact_label(text: str) -> None:
    st.sidebar.markdown(f'<div class="cc-compact-label">{text}</div>', unsafe_allow_html=True)


def clean_user_copy(value: object) -> str:
    text = str(value or "")
    hidden_phrases = [
        "AI service unavailable. Using rule-based audience segmentation.",
        "Using rule-based audience segmentation.",
        "Gemini API request failed.",
        "Gemini client initialization failed.",
        "Gemini returned an unusable response.",
        "AudienceAgent Gemini path failed.",
    ]
    for phrase in hidden_phrases:
        text = text.replace(phrase, "")
    return " ".join(text.split()).strip()


def card(title: str, body: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<div class="cc-eyebrow">{eyebrow}</div>' if eyebrow else ""
    body = clean_user_copy(body)
    st.markdown(
        f"""
        <div class="cc-card">
            {eyebrow_html}
            <div class="cc-title">{title}</div>
            <div class="cc-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, trend: str | None = None, icon: str = "+") -> None:
    trend_html = f'<div class="cc-kpi-trend">{trend}</div>' if trend else ""
    st.markdown(
        f"""
        <div class="cc-kpi">
            <div class="cc-kpi-top">
                <div class="cc-kpi-label">{label}</div>
                <div class="cc-kpi-icon">{icon}</div>
            </div>
            <div class="cc-kpi-value">{value}</div>
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="cc-panel-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="cc-panel">
            <div class="cc-panel-title">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def summary_card(title: str, body: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<div class="cc-eyebrow">{eyebrow}</div>' if eyebrow else ""
    st.markdown(
        f"""
        <div class="cc-hero-card">
            {eyebrow_html}
            <div class="cc-title">{title}</div>
            <div class="cc-summary">{clean_user_copy(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataframe_from_items(items: list[dict[str, Any]]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame()
    return pd.DataFrame(items)


def customer_charts(customers: list[dict[str, Any]], mode: str = "light") -> None:
    df = dataframe_from_items(customers)
    if df.empty:
        st.info("No customer data available yet.")
        return

    left, right = st.columns(2)
    with left:
        if "loyalty_tier" in df:
            tier_counts = df["loyalty_tier"].value_counts().reset_index()
            tier_counts.columns = ["loyalty_tier", "customers"]
            fig = px.bar(
                tier_counts,
                x="loyalty_tier",
                y="customers",
                color="loyalty_tier",
                title="Customer Loyalty Mix",
                color_discrete_sequence=CHART_COLORS,
            )
            apply_chart_theme(fig, mode)
            fig.update_layout(showlegend=False, height=350, margin=dict(l=10, r=10, t=52, b=20))
            st.plotly_chart(fig, use_container_width=True)
    with right:
        if "preferred_channel" in df:
            channel_counts = df["preferred_channel"].value_counts().reset_index()
            channel_counts.columns = ["preferred_channel", "customers"]
            fig = px.pie(
                channel_counts,
                names="preferred_channel",
                values="customers",
                title="Preferred Channel Mix",
                hole=0.45,
                color_discrete_sequence=CHART_COLORS,
            )
            apply_chart_theme(fig, mode)
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=52, b=20))
            st.plotly_chart(fig, use_container_width=True)


def rate_chart(rates: dict[str, float], title: str, mode: str = "light") -> None:
    df = pd.DataFrame(
        [{"metric": key.replace("_", " ").title(), "rate": value} for key, value in rates.items()]
    )
    fig = px.bar(df, x="metric", y="rate", text="rate", title=title, color="metric", color_discrete_sequence=CHART_COLORS)
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, max(0.1, min(1.0, df["rate"].max() * 1.25))])
    apply_chart_theme(fig, mode)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=45, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def show_error(error: Exception) -> None:
    message = clean_user_copy(error)
    if "Traceback" in message or "File " in message or "Exception" in message or "Gemini" in message:
        message = "Something went wrong while processing the request. Please try again."
    st.error(message)

