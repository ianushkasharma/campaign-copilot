from __future__ import annotations

import json
import sys
import time
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from streamlit_app.api_client import CRMClient
from streamlit_app.settings import APP_NAME, default_crm_base_url
from streamlit_app.ui import (
    CHART_COLORS,
    apply_chart_theme,
    apply_theme,
    brand_header,
    card,
    clean_user_copy,
    compact_label,
    customer_charts,
    dataframe_from_items,
    metric_card,
    page_header,
    rate_chart,
    show_error,
    summary_card,
)

st.set_page_config(page_title=APP_NAME, layout="wide")
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False


def theme_mode() -> str:
    return "dark" if st.session_state.get("dark_mode") else "light"


apply_theme(theme_mode())

topbar = st.container()
with topbar:
    _, toggle_col = st.columns([0.84, 0.16])
    with toggle_col:
        st.toggle("Dark mode", key="dark_mode")


@st.cache_data(ttl=20)
def fetch_customers(base_url: str, limit: int = 500, offset: int = 0) -> dict[str, Any]:
    return CRMClient(base_url).list_customers(limit=limit, offset=offset)


@st.cache_data(ttl=20)
def fetch_campaigns(base_url: str, limit: int = 200, offset: int = 0) -> dict[str, Any]:
    return CRMClient(base_url).list_campaigns(limit=limit, offset=offset)


@st.cache_data(ttl=20)
def fetch_segments(base_url: str, limit: int = 200, offset: int = 0) -> dict[str, Any]:
    return CRMClient(base_url).list_segments(limit=limit, offset=offset)


def clear_cache() -> None:
    fetch_customers.clear()
    fetch_campaigns.clear()
    fetch_segments.clear()


def sidebar() -> str:
    brand_header()
    compact_label("Workspace")
    crm_base = st.sidebar.text_input(
        "CRM API",
        value=st.session_state.get("crm_base_url", default_crm_base_url()),
        label_visibility="collapsed",
    )
    st.session_state["crm_base_url"] = crm_base.rstrip("/")

    compact_label("Navigation")
    current_page = st.session_state.get("active_page", "Dashboard")
    option_to_page = {
        "🏠 Dashboard": "Dashboard",
        "👥 Audience Explorer": "Audience Explorer",
        "📂 Segments": "Segments",
        "🤖 Campaign Copilot": "Campaign Copilot",
        "📈 Campaign Monitor": "Campaign Monitor",
        "✨ AI Insights": "AI Insights",
    }
    options = list(option_to_page.keys())
    current_option = next(
        (option for option, label in option_to_page.items() if label == current_page),
        options[0],
    )
    selected_option = st.sidebar.radio(
        "Pages",
        options,
        index=options.index(current_option),
        label_visibility="collapsed",
        key="sidebar_navigation",
    )
    page = option_to_page[selected_option]
    st.session_state["active_page"] = page

    if st.sidebar.button("Refresh data", use_container_width=True):
        clear_cache()
        st.rerun()
    return page

def money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def labelize(value: object) -> str:
    text = str(value).replace("_", " ").title()
    return text.replace("Whatsapp", "WhatsApp").replace("Sms", "SMS")


def display_table(df: pd.DataFrame, key: str, default_rows: int = 12) -> None:
    if df.empty:
        st.info("No records to display.")
        return

    controls = st.columns([2.2, 1, 1])
    search = controls[0].text_input("Search table", key=f"{key}_search", placeholder="Search rows...")
    rows = controls[1].number_input("Rows", min_value=5, max_value=100, value=default_rows, step=5, key=f"{key}_rows")
    page = controls[2].number_input("Page", min_value=1, value=1, step=1, key=f"{key}_page")

    view = df.copy()
    if search:
        mask = view.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        view = view[mask]

    start = (int(page) - 1) * int(rows)
    end = start + int(rows)
    st.caption(f"Showing {min(len(view), start + 1) if len(view) else 0}-{min(end, len(view))} of {len(view)} rows")
    st.dataframe(view.iloc[start:end], use_container_width=True, hide_index=True, height=420)


def notify_success(message: str) -> None:
    if hasattr(st, "toast"):
        st.toast(message)


def client() -> CRMClient:
    return CRMClient(st.session_state.get("crm_base_url"))


def crm_base_url() -> str:
    return st.session_state.get("crm_base_url", default_crm_base_url())


def dashboard() -> None:
    page_header("Dashboard", "Customer, audience, and campaign health at a glance.")
    try:
        customer_response = fetch_customers(crm_base_url())
        customers = customer_response["items"]
        campaigns = fetch_campaigns(crm_base_url())["items"]
        segments = fetch_segments(crm_base_url())["items"]
    except Exception as exc:
        show_error(exc)
        return

    df = dataframe_from_items(customers)
    total_customers = customer_response["total"]
    total_spent = float(df["total_spent"].astype(float).sum()) if not df.empty and "total_spent" in df else 0
    avg_orders = float(df["total_orders"].mean()) if not df.empty and "total_orders" in df else 0
    inactive_count = int((df["loyalty_tier"] == "Inactive").sum()) if not df.empty and "loyalty_tier" in df else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Customers", f"{total_customers:,}", "Seeded CRM audience", "U")
    with c2:
        metric_card("Revenue", money(total_spent), "Historical sample value", "$")
    with c3:
        metric_card("Average Orders", f"{avg_orders:.1f}", "Across loaded customers", "#")
    with c4:
        metric_card("Inactive Customers", f"{inactive_count:,}", "Ready for winback", "!")

    customer_charts(customers, mode=theme_mode())

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Recent customers")
        if df.empty:
            st.info("No customers found. Run `python seed.py` to create demo data.")
        else:
            columns = [
                "customer_id",
                "name",
                "email",
                "city",
                "preferred_channel",
                "total_orders",
                "total_spent",
                "loyalty_tier",
            ]
            display_table(df[[column for column in columns if column in df]], "dashboard_customers", 10)
    with right:
        card("Campaigns", f"{len(campaigns)} campaign records loaded.", "CRM")
        card("Segments", f"{len(segments)} audience segments available.", "CRM")
        card("Audience intelligence", "Audience planning and campaign insights are ready for your demo workflows.", "CRM")

    st.subheader("Customer intelligence")
    try:
        scores = client().customer_scores(limit=100)
        score_df = dataframe_from_items(scores["items"])
        if not score_df.empty:
            score_metrics = st.columns(3)
            score_metrics[0].metric("Avg health score", f"{score_df['customer_health_score'].mean():.1f}")
            score_metrics[1].metric("Avg engagement score", f"{score_df['engagement_score'].mean():.1f}")
            score_metrics[2].metric("Top RFM score", str(score_df["rfm"].apply(lambda value: value["rfm_score"]).max()))
            display_df = score_df.copy()
            display_df["rfm_score"] = display_df["rfm"].apply(lambda value: value["rfm_score"])
            display_table(
                display_df[
                    [
                        "customer_id",
                        "name",
                        "loyalty_tier",
                        "preferred_channel",
                        "rfm_score",
                        "customer_health_score",
                        "engagement_score",
                    ]
                ],
                "customer_intelligence",
                10,
            )
    except Exception as exc:
        st.info("Customer intelligence will appear once customer score data is available.")


def _format_filter_value(value: object) -> str:
    if isinstance(value, float) and value.is_integer():
        return f"{value:,.0f}"
    if isinstance(value, int | float):
        return f"{value:,}"
    return labelize(value)


def audience_filter_chips(filters: dict[str, Any]) -> list[str]:
    chips: list[str] = []
    for key, value in filters.items():
        if value in (None, "", []):
            continue

        if key == "inactive_days_gt":
            chips.append(f"Inactive >{_format_filter_value(value)} Days")
        elif key == "total_spent_gt":
            chips.append(f"Spend >{_format_filter_value(value)}")
        elif key == "total_spent_gte":
            chips.append(f"Spend >={_format_filter_value(value)}")
        elif key == "total_spent_lt":
            chips.append(f"Spend <{_format_filter_value(value)}")
        elif key == "total_orders_gt":
            chips.append(f"Orders >{_format_filter_value(value)}")
        elif key == "total_orders_gte":
            chips.append(f"Orders >={_format_filter_value(value)}")
        elif key == "loyalty_tier_in" and isinstance(value, list):
            chips.append(f"Loyalty Tier: {', '.join(_format_filter_value(item) for item in value)}")
        elif key == "preferred_channel_in" and isinstance(value, list):
            chips.append(f"Channel: {', '.join(_format_filter_value(item) for item in value)}")
        elif key == "city":
            chips.append(f"City: {_format_filter_value(value)}")
        elif key == "gender":
            chips.append(f"Gender: {_format_filter_value(value)}")
        else:
            chips.append(f"{key.replace('_', ' ').title()}: {_format_filter_value(value)}")
    return chips


def applied_filters(filters: dict[str, Any]) -> None:
    chips = audience_filter_chips(filters)
    if not chips:
        return

    chip_html = "".join(f'<span class="cc-pill">{escape(chip)}</span>' for chip in chips)
    st.subheader("Applied Filters")
    st.markdown(f'<div class="cc-filter-row">{chip_html}</div>', unsafe_allow_html=True)


def audience_stats(result: dict[str, Any]) -> tuple[pd.DataFrame, float, float]:
    preview_df = dataframe_from_items(result.get("audience_preview", []))
    if preview_df.empty or "total_spent" not in preview_df:
        return preview_df, 0.0, 0.0

    spend = preview_df["total_spent"].astype(float)
    avg_spend = float(spend.mean()) if not spend.empty else 0.0
    estimated_revenue = avg_spend * int(result.get("audience_size", 0))
    return preview_df, estimated_revenue, avg_spend


def audience_summary_text(result: dict[str, Any], preview_df: pd.DataFrame, estimated_revenue: float) -> str:
    filters = result.get("filters", {})
    size = int(result.get("audience_size", 0))
    inactive_days = filters.get("inactive_days_gt")
    spend_gt = filters.get("total_spent_gt") or filters.get("total_spent_gte")
    audience_phrase = f"This audience contains {size:,} customers"
    if inactive_days:
        audience_phrase = f"This audience contains {size:,} inactive customers"
    if spend_gt:
        audience_phrase += f" who have spent more than ${float(spend_gt):,.0f} historically"
    audience_phrase += "."

    channel_sentence = "Preferred-channel data will become clearer as more audience rows are previewed."
    if not preview_df.empty and "preferred_channel" in preview_df:
        top_channels = preview_df["preferred_channel"].dropna().map(labelize).value_counts().head(2).index.tolist()
        if top_channels:
            channel_sentence = (
                f"Most previewed customers prefer {' and '.join(top_channels)}, "
                "making them suitable for focused re-engagement campaigns."
            )

    return (
        f"{audience_phrase}\n\n"
        f"{channel_sentence}\n\n"
        f"The segment represents approximately {money(estimated_revenue)} in historical revenue."
    )


def audience_insight_charts(preview_df: pd.DataFrame) -> None:
    if preview_df.empty:
        return

    st.subheader("Audience Insights")
    chart_specs = [
        ("loyalty_tier", "Loyalty Tier Distribution", "bar"),
        ("preferred_channel", "Preferred Channel Distribution", "pie"),
        ("city", "Top Cities", "bar"),
        ("gender", "Gender Distribution", "pie"),
    ]
    rows = [st.columns(2), st.columns(2)]
    for index, (column, title, chart_type) in enumerate(chart_specs):
        if column not in preview_df:
            continue
        counts = preview_df[column].fillna("Unknown").astype(str).value_counts().head(8).reset_index()
        counts.columns = [column, "customers"]
        with rows[index // 2][index % 2]:
            if chart_type == "pie":
                fig = px.pie(
                    counts,
                    names=column,
                    values="customers",
                    title=title,
                    hole=0.48,
                    color_discrete_sequence=CHART_COLORS,
                )
            else:
                fig = px.bar(
                    counts,
                    x=column,
                    y="customers",
                    color=column,
                    title=title,
                    color_discrete_sequence=CHART_COLORS,
                )
                fig.update_layout(showlegend=False)
            apply_chart_theme(fig, theme_mode())
            fig.update_layout(height=330, margin=dict(l=10, r=10, t=48, b=20))
            st.plotly_chart(fig, use_container_width=True)


def audience_explorer() -> None:
    page_header("Audience Explorer", "Describe an audience and generate precise customer filters.")
    query = st.text_area(
        "Audience request",
        value="Find inactive customers who spent more than 5000",
        height=100,
    )
    preview_limit = st.slider("Preview rows", min_value=5, max_value=50, value=10)

    if st.button("Find audience", type="primary"):
        try:
            result = client().query_audience(query=query, preview_limit=preview_limit)
            st.session_state["audience_result"] = result
        except Exception as exc:
            show_error(exc)

    result = st.session_state.get("audience_result")
    if not result:
        return

    preview_df, estimated_revenue, avg_spend = audience_stats(result)
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Audience Size", f"{result['audience_size']:,}", "Generated successfully", "A")
    with c2:
        metric_card("Estimated Revenue", money(estimated_revenue), "Based on preview spend", "$")
    with c3:
        metric_card("Avg Spend", money(avg_spend), "Previewed customer value", "~")

    summary_card(
        "AI Summary",
        audience_summary_text(result, preview_df, estimated_revenue),
        "Audience generated successfully",
    )

    applied_filters(result.get("filters", {}))
    audience_insight_charts(preview_df)

    st.subheader("Audience preview")
    display_columns = [
        "customer_id",
        "name",
        "email",
        "city",
        "gender",
        "preferred_channel",
        "total_orders",
        "total_spent",
        "loyalty_tier",
    ]
    if preview_df.empty:
        st.info("No audience preview rows returned.")
    else:
        display_table(preview_df[[column for column in display_columns if column in preview_df]], "audience_preview", 10)

    with st.container():
        card("Save Segment", "Store this audience as a reusable segment for future campaigns.", "Segment library")
        segment_name = st.text_input("Segment name", value="Generated Audience Segment")
        segment_description = st.text_area("Description", value=clean_user_copy(result["reasoning"]))
        if st.button("Create segment"):
            try:
                created = client().create_segment(
                    {
                        "name": segment_name,
                        "description": segment_description,
                        "criteria_json": json.dumps(result["filters"]),
                    }
                )
                clear_cache()
                st.success(f"Created segment #{created['segment_id']}")
                notify_success("Segment created successfully.")
            except Exception as exc:
                show_error(exc)


def campaign_copilot() -> None:
    page_header("Campaign Copilot", "Generate a complete campaign plan from a plain-language goal.")
    goal = st.text_area("Campaign goal", value="Bring back inactive customers.", height=100)
    preview_limit = st.slider("Audience preview limit", min_value=1, max_value=25, value=5)

    if st.button("Generate plan", type="primary"):
        try:
            plan = client().plan_campaign(goal=goal, preview_limit=preview_limit)
            st.session_state["campaign_plan"] = plan
        except Exception as exc:
            show_error(exc)

    plan = st.session_state.get("campaign_plan")
    if not plan:
        return

    st.subheader("Generated Campaign Plan")
    summary_card("Campaign Objective", plan["goal_understanding"], "Objective")

    col1, col2, col3 = st.columns(3)
    audience = plan["recommended_audience"]
    channel = plan["recommended_channel"]
    offer = plan["recommended_offer"]
    with col1:
        metric_card("Audience", f"{audience['size']:,}", "Recommended reach", "A")
    with col2:
        metric_card("Channel", labelize(channel["channel"]), "Best fit for goal", "C")
    with col3:
        metric_card("Offer", offer["offer_value"], "Suggested incentive", "%")

    left, right = st.columns(2)
    with left:
        card(audience["name"], audience["description"], "Generated Audience")
        applied_filters(audience.get("filters", {}))
        card(labelize(channel["channel"]), channel["rationale"], "Channel Strategy")
    with right:
        message = plan["personalized_message"]
        card(offer["offer_type"].replace("_", " ").title(), offer["rationale"], "Offer Strategy")
        card(message["subject"], message["body"], "Generated Message")

    performance = plan["expected_performance"]
    rates = {
        "open_rate": performance["estimated_open_rate"],
        "click_rate": performance["estimated_click_rate"],
        "purchase_rate": performance["estimated_purchase_rate"],
    }
    rate_chart(rates, "Expected performance", mode=theme_mode())
    p1, p2 = st.columns(2)
    with p1:
        metric_card("Estimated purchases", f"{performance['estimated_purchases']:,}", "Projected conversions", "P")
    with p2:
        metric_card("Estimated revenue", money(float(performance["estimated_revenue"])), "Projected revenue", "$")
    card("Performance rationale", performance["rationale"], "Performance model")
    summary_card(
        "Campaign Preview",
        (
            f"Send a {labelize(channel['channel'])} campaign to {audience['size']:,} customers "
            f"with the offer '{offer['offer_value']}'. Expected open rate is "
            f"{performance['estimated_open_rate']:.1%}, with projected revenue of "
            f"{money(float(performance['estimated_revenue']))}."
        ),
        "Launch preview",
    )

    with st.expander("Create campaign from plan"):
        campaign_name = st.text_input("Campaign name", value=audience["name"])
        start_date = st.date_input("Start date", value=date.today())
        if st.button("Create campaign"):
            try:
                created = client().create_campaign(
                    {
                        "name": campaign_name,
                        "channel": channel["channel"],
                        "status": "draft",
                        "start_date": start_date.isoformat(),
                        "end_date": None,
                        "objective": plan["goal_understanding"],
                    }
                )
                clear_cache()
                st.success(f"Created campaign #{created['campaign_id']}")
            except Exception as exc:
                show_error(exc)


def segments_page() -> None:
    page_header("Segments", "Saved audiences and reusable campaign targeting rules.")
    try:
        segments = fetch_segments(crm_base_url())["items"]
    except Exception as exc:
        show_error(exc)
        return

    segment_df = dataframe_from_items(segments)
    c1, c2 = st.columns([1, 2])
    with c1:
        metric_card("Saved Segments", f"{len(segments):,}", "Reusable audiences", "◇")
    with c2:
        card("Segment Library", "Use saved segments to launch repeatable campaigns and compare performance over time.", "Audiences")

    if segment_df.empty:
        st.info("No segments saved yet. Create one from Audience Explorer.")
    else:
        display_table(segment_df, "segments_library", 10)


def campaign_monitor() -> None:
    page_header("Campaign Monitor", "Live delivery, engagement, and purchase funnel from campaign events.")
    try:
        campaigns = fetch_campaigns(crm_base_url())["items"]
        segments = fetch_segments(crm_base_url())["items"]
    except Exception as exc:
        show_error(exc)
        return

    if not campaigns:
        st.info("No campaigns yet. Create one from Campaign Copilot to begin monitoring.")
        return

    campaign_options = {"All campaigns": None}
    campaign_options.update({f"{item['campaign_id']} - {item['name']}": item["campaign_id"] for item in campaigns})
    selected_monitor_campaign = st.selectbox("Monitor campaign", list(campaign_options.keys()))
    selected_campaign_id = campaign_options[selected_monitor_campaign]

    control_cols = st.columns([1, 1, 2])
    live_refresh = control_cols[0].toggle("Live refresh", value=False)
    refresh_seconds = control_cols[1].number_input("Refresh seconds", min_value=5, max_value=120, value=10, step=5)
    event_limit = control_cols[2].slider("Timeline events", min_value=25, max_value=500, value=100, step=25)

    try:
        monitor = client().campaign_monitor(campaign_id=selected_campaign_id, limit=event_limit)
        success = client().campaign_success(campaign_id=selected_campaign_id)
    except Exception as exc:
        show_error(exc)
        return

    summary = monitor["summary"]
    sent = max(summary["messages_sent"], 1)

    metric_cols = st.columns(5)
    with metric_cols[0]:
        metric_card("Messages Sent", f"{summary['messages_sent']:,}", "Total outreach", "S")
    with metric_cols[1]:
        metric_card("Delivered", f"{summary['delivered']:,}", f"{summary['delivered'] / sent:.1%} delivery", "D")
    with metric_cols[2]:
        metric_card("Opened", f"{summary['opened']:,}", f"{summary['opened'] / sent:.1%} open rate", "O")
    with metric_cols[3]:
        metric_card("Clicked", f"{summary['clicked']:,}", f"{summary['clicked'] / sent:.1%} click rate", "K")
    with metric_cols[4]:
        metric_card("Failed", f"{summary['failed']:,}", f"{summary['failed'] / sent:.1%} failed", "!")
    metric_card("Campaign Success Score", f"{success['campaign_success_score']:.1f}/100", "Composite performance score", "*")

    st.subheader("Engagement Rates")
    rate_cols = st.columns(2)
    with rate_cols[0]:
        rate_chart({"open_rate": summary["opened"] / sent}, "Open Rate", mode=theme_mode())
    with rate_cols[1]:
        rate_chart({"click_rate": summary["clicked"] / sent}, "Click Rate", mode=theme_mode())

    st.subheader("Delivery Funnel")
    if summary["messages_sent"] == 0:
        st.info("Delivery funnel will populate after messages are sent.")
    else:
        funnel = go.Figure(
            go.Funnel(
                y=["Sent", "Delivered", "Opened", "Clicked", "Purchased"],
                x=[
                    summary["messages_sent"],
                    summary["delivered"],
                    summary["opened"],
                    summary["clicked"],
                    summary["purchased"],
                ],
                textinfo="value+percent initial",
                marker=dict(color=["#3157d5", "#13a987", "#f59e0b", "#8b5cf6", "#ef4444"]),
            )
        )
        apply_chart_theme(funnel, theme_mode())
        funnel.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(funnel, use_container_width=True)

    st.subheader("Funnel progress")
    progress_cols = st.columns(3)
    progress_items = [
        ("Delivered", summary["delivered"], progress_cols[0]),
        ("Opened", summary["opened"], progress_cols[1]),
        ("Clicked", summary["clicked"], progress_cols[2]),
        ("Purchased", summary["purchased"], progress_cols[0]),
        ("Failed", summary["failed"], progress_cols[1]),
    ]
    for label, value, container in progress_items:
        rate = min(value / sent, 1.0)
        container.caption(f"{label}: {rate:.1%}")
        container.progress(rate)

    events = monitor.get("timeline", [])
    events_df = dataframe_from_items(events)
    st.subheader("Event timeline")
    if events_df.empty:
        st.info("No campaign events yet. Send a campaign or wait for channel callbacks.")
    else:
        events_df["event_time"] = pd.to_datetime(events_df["event_time"])
        timeline_chart_df = events_df.sort_values("event_time")
        fig = px.scatter(
            timeline_chart_df,
            x="event_time",
            y="event_type",
            color="event_type",
            hover_data=["event_id", "campaign_id", "customer_id"],
            title="Campaign event timeline",
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_traces(marker=dict(size=10))
        apply_chart_theme(fig, theme_mode())
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=45, b=10), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        counts_df = (
            events_df["event_type"]
            .value_counts()
            .rename_axis("event_type")
            .reset_index(name="events")
        )
        bar = px.bar(
            counts_df,
            x="event_type",
            y="events",
            color="event_type",
            title="Events by type",
            color_discrete_sequence=CHART_COLORS,
        )
        apply_chart_theme(bar, theme_mode())
        bar.update_layout(height=320, showlegend=False, margin=dict(l=10, r=10, t=45, b=10))
        st.plotly_chart(bar, use_container_width=True)

        st.subheader("Latest events")
        event_columns = ["event_id", "campaign_id", "customer_id", "event_type", "event_time"]
        display_table(events_df[[column for column in event_columns if column in events_df]], "campaign_events", 10)

    st.divider()
    df = dataframe_from_items(campaigns)
    st.subheader("Campaigns")
    display_table(df, "campaigns_monitor", 10)

    st.subheader("Send campaign")
    send_campaign_options = {f"{item['campaign_id']} - {item['name']}": item["campaign_id"] for item in campaigns}
    segment_options = {"All matching customers": None}
    segment_options.update({f"{item['segment_id']} - {item['name']}": item["segment_id"] for item in segments})

    selected_campaign = st.selectbox("Campaign", list(send_campaign_options.keys()))
    selected_segment = st.selectbox("Segment", list(segment_options.keys()))
    subject = st.text_input("Subject", value="A special offer for you")
    message = st.text_area("Message", value="We saved an exclusive offer for your next order.")
    if st.button("Send campaign", type="primary"):
        payload = {
            "campaign_id": send_campaign_options[selected_campaign],
            "segment_id": segment_options[selected_segment],
            "customer_ids": None,
            "subject": subject,
            "message": message,
        }
        try:
            result = client().send_campaign(payload)
            st.success(f"Sent to {result['recipients']:,} recipients.")
            notify_success("Campaign queued successfully.")
        except Exception as exc:
            show_error(exc)

    if live_refresh:
        time.sleep(refresh_seconds)
        clear_cache()
        st.rerun()


def ai_insights() -> None:
    page_header("AI Insights", "Predict future performance and analyze completed campaigns.")
    try:
        leaderboard_preview = client().audience_leaderboard().get("items", [])
    except Exception:
        leaderboard_preview = []

    top_audience = leaderboard_preview[0] if leaderboard_preview else {}
    executive_cols = st.columns(4)
    with executive_cols[0]:
        metric_card(
            "Best Performing Audience",
            str(top_audience.get("ai_segment_name") or "Pending data"),
            "Based on campaign success",
            "A",
        )
    with executive_cols[1]:
        metric_card("Best Channel", "WhatsApp", "Strong re-engagement fit", "C")
    with executive_cols[2]:
        metric_card("Predicted Reach", "1.2K", "Typical demo audience", "R")
    with executive_cols[3]:
        metric_card("Next Campaign", "Winback", "Recommended focus", "N")

    tab_predict, tab_analyze = st.tabs(["Prediction Lab", "Post-campaign Analysis"])

    with tab_analyze:
        try:
            campaigns = fetch_campaigns(crm_base_url())["items"]
        except Exception as exc:
            show_error(exc)
            campaigns = []

        if campaigns:
            campaign_options = {f"{item['campaign_id']} - {item['name']}": item["campaign_id"] for item in campaigns}
            selected_campaign = st.selectbox("Completed campaign", list(campaign_options.keys()))
            if st.button("Analyze campaign", type="primary"):
                try:
                    insights = client().analyze_campaign(campaign_options[selected_campaign])
                    st.session_state["campaign_insights"] = insights
                except Exception as exc:
                    show_error(exc)
        else:
            st.info("No campaigns available for analysis.")

        insights = st.session_state.get("campaign_insights")
        if insights:
            metrics = insights["metrics"]
            metric_cols = st.columns(5)
            with metric_cols[0]:
                metric_card("Sent", f"{metrics.get('messages_sent', 0):,}", "Campaign volume", "S")
            with metric_cols[1]:
                metric_card("Delivered", f"{metrics.get('delivered', 0):,}", "Reached inboxes", "D")
            with metric_cols[2]:
                metric_card("Opened", f"{metrics.get('opened', 0):,}", "Engaged users", "O")
            with metric_cols[3]:
                metric_card("Clicked", f"{metrics.get('clicked', 0):,}", "High intent", "K")
            with metric_cols[4]:
                metric_card("Revenue", money(float(insights["revenue_generated"])), "Generated value", "$")

            insight_left, insight_right = st.columns(2)
            with insight_left:
                summary_card("What happened", insights["what_happened"], "Executive summary")
            with insight_right:
                summary_card("Why it happened", insights["why_it_happened"], "Drivers")

            cols = st.columns(3)
            with cols[0]:
                card(insights["best_segment"]["name"], insights["best_segment"]["reason"], "Best performing audience")
            with cols[1]:
                card(insights["worst_segment"]["name"], insights["worst_segment"]["reason"], "Worst segment")
            with cols[2]:
                card(insights["best_channel"]["name"], insights["best_channel"]["reason"], "Best channel")

            summary_card("Recommended next campaign", insights["recommended_next_action"], "Next step")

        st.subheader("Best performing audience leaderboard")
        try:
            leaderboard = client().audience_leaderboard()
            leaderboard_df = dataframe_from_items(leaderboard.get("items", []))
            if leaderboard_df.empty:
                st.info("No audience performance data yet.")
            else:
                fig = px.bar(
                    leaderboard_df,
                    x="ai_segment_name",
                    y="campaign_success_score",
                    color="conversion_rate",
                    title="Audience success score",
                    hover_data=["segment_key", "messages_sent", "purchased", "revenue_generated"],
                    color_continuous_scale=["#dbeafe", "#3157d5"],
                )
                apply_chart_theme(fig, theme_mode())
                fig.update_layout(height=360, margin=dict(l=10, r=10, t=45, b=80), xaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        except Exception as exc:
            st.info("Audience leaderboard will appear once campaign performance data is available.")

    with tab_predict:
        prediction_lab()


def prediction_lab() -> None:
    col1, col2, col3 = st.columns(3)
    audience_size = col1.number_input("Audience size", min_value=0, value=1250, step=50)
    avg_spent = col2.number_input("Average total spent", min_value=0.0, value=6200.0, step=100.0)
    avg_orders = col3.number_input("Average total orders", min_value=0.0, value=4.5, step=0.5)

    col4, col5, col6 = st.columns(3)
    inactive_days = col4.number_input("Inactive days", min_value=0, value=180, step=30)
    channel = col5.selectbox("Channel", ["whatsapp", "email", "sms", "push", "phone"])
    offer_type = col6.selectbox("Offer type", ["limited_time_discount", "free_shipping", "cashback", "loyalty_points"])
    offer_value = st.text_input("Offer value", value="15% off the next order")

    if st.button("Predict performance", type="primary"):
        payload = {
            "audience": {
                "audience_size": int(audience_size),
                "avg_total_spent": float(avg_spent),
                "avg_total_orders": float(avg_orders),
                "inactive_days_gt": int(inactive_days),
                "filters": {"inactive_days_gt": int(inactive_days)},
            },
            "channel": channel,
            "offer": {"offer_type": offer_type, "offer_value": offer_value},
        }
        try:
            prediction = client().predict_campaign(payload)
            st.session_state["prediction"] = prediction
        except Exception as exc:
            show_error(exc)

    prediction = st.session_state.get("prediction")
    if not prediction:
        return

    rates = {
        "open_rate": prediction["predicted_open_rate"],
        "click_rate": prediction["predicted_click_rate"],
        "conversion_rate": prediction["predicted_conversion_rate"],
    }
    rate_chart(rates, "Predicted rates", mode=theme_mode())
    metric_card("Predicted Revenue", money(float(prediction["predicted_revenue"])), "Rule-calibrated forecast", "$")
    st.subheader("Assumptions")
    card("Forecast assumptions", "<br>".join(clean_user_copy(item) for item in prediction["assumptions"]), "Model notes")


page_name = sidebar()

if page_name not in {
    "Dashboard",
    "Audience Explorer",
    "Segments",
    "Campaign Copilot",
    "Campaign Monitor",
    "AI Insights",
}:
    page_name = "Dashboard"
    st.session_state["active_page"] = "Dashboard"

if page_name == "Dashboard":
    dashboard()
elif page_name == "Audience Explorer":
    audience_explorer()
elif page_name == "Segments":
    segments_page()
elif page_name == "Campaign Copilot":
    campaign_copilot()
elif page_name == "Campaign Monitor":
    campaign_monitor()
elif page_name == "AI Insights":
    ai_insights()


