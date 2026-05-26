import pandas as pd
import streamlit as st

from api_client import (
    API_BASE_URL,
    get_audit_runs,
    get_cancellations_by_airport,
    get_delay_summary,
    get_latest_metrics_snapshot,
    get_metrics_snapshots,
    get_passenger_impact_summary,
    get_top_delayed_routes,
)


st.set_page_config(
    page_title="AeroOps Control Tower",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #d8dee8;
        border-radius: 6px;
        padding: 0.8rem 0.9rem;
        background: #fbfcfe;
    }
    div[data-testid="stMetricLabel"] {
        color: #445064;
        font-size: 0.78rem;
    }
    div[data-testid="stMetricValue"] {
        color: #172033;
        font-size: 1.55rem;
    }
    .ops-caption {
        color: #5d6b82;
        font-size: 0.9rem;
        margin-top: -0.5rem;
    }
    .section-rule {
        border-top: 1px solid #e5eaf1;
        margin: 0.75rem 0 1.25rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def as_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows or [])


def pct(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def metric_value(value, suffix: str = "") -> str:
    if value is None:
        value = 0
    if isinstance(value, float):
        return f"{value:,.2f}{suffix}"
    return f"{value:,}{suffix}"


with st.sidebar:
    st.header("Controls")
    data_mode = st.radio(
        "Data mode",
        options=["Live", "Snapshot"],
        horizontal=True,
    )
    route_limit = st.slider("Routes shown", min_value=5, max_value=50, value=15, step=5)
    route_min_flights = st.slider(
        "Route minimum flights",
        min_value=1,
        max_value=200,
        value=10,
        step=1,
    )
    airport_limit = st.slider("Airports shown", min_value=5, max_value=75, value=20, step=5)
    airport_min_flights = st.slider(
        "Airport minimum flights",
        min_value=1,
        max_value=500,
        value=50,
        step=5,
    )
    st.caption(f"API: {API_BASE_URL}")


st.title("AeroOps Control Tower")
st.markdown(
    "<div class='ops-caption'>Operational analytics for delay, route, airport, "
    "passenger-impact, and audit monitoring.</div>",
    unsafe_allow_html=True,
)


try:
    audit_payload = get_audit_runs(limit=20)

    if data_mode == "Live":
        delay_summary = get_delay_summary()
        route_payload = get_top_delayed_routes(
            limit=route_limit,
            min_flights=route_min_flights,
        )
        airport_payload = get_cancellations_by_airport(
            limit=airport_limit,
            min_flights=airport_min_flights,
        )
        impact_summary = get_passenger_impact_summary()
        snapshot_meta = None
        snapshots_payload = None
    else:
        latest_snapshot_payload = get_latest_metrics_snapshot()
        snapshot_document = latest_snapshot_payload.get("result")

        if not snapshot_document:
            st.warning("No snapshot found. Run `python -m scripts.build_analytics_snapshots` and reload.")
            st.stop()

        snapshot_meta = {
            "snapshot_id": snapshot_document.get("snapshot_id"),
            "created_at": snapshot_document.get("created_at"),
        }
        snapshots_payload = get_metrics_snapshots(limit=20)

        delay_summary = {
            "total_flights": snapshot_document.get("metrics", {}).get("total_flights", 0),
            "delayed_flights": snapshot_document.get("metrics", {}).get("delayed_flights", 0),
            "cancelled_flights": snapshot_document.get("metrics", {}).get("cancelled_flights", 0),
            "average_departure_delay": snapshot_document.get("metrics", {}).get("average_departure_delay", 0),
            "average_arrival_delay": snapshot_document.get("metrics", {}).get("average_arrival_delay", 0),
            "max_departure_delay": snapshot_document.get("metrics", {}).get("max_departure_delay", 0),
        }
        route_payload = {
            "results": snapshot_document.get("top_delayed_routes", [])[:route_limit]
        }
        airport_payload = {
            "results": snapshot_document.get("cancellations_by_airport", [])[:airport_limit]
        }
        impact_summary = snapshot_document.get("passenger_impact_summary", {})
except Exception as exc:
    st.error(f"Dashboard data load failed: {exc}")
    st.stop()


total_flights = delay_summary.get("total_flights", 0)
delayed_flights = delay_summary.get("delayed_flights", 0)
cancelled_flights = delay_summary.get("cancelled_flights", 0)

route_df = as_df(route_payload.get("results", []))
airport_df = as_df(airport_payload.get("results", []))
impact_df = as_df(impact_summary.get("top_impacted_flights", []))
audit_df = as_df(audit_payload.get("results", []))


st.markdown("<div class='section-rule'></div>", unsafe_allow_html=True)
kpi_1, kpi_2, kpi_3, kpi_4, kpi_5, kpi_6 = st.columns(6)
kpi_1.metric("Total flights", metric_value(total_flights))
kpi_2.metric("Delayed flights", metric_value(delayed_flights))
kpi_3.metric("Delay rate", metric_value(pct(delayed_flights, total_flights), "%"))
kpi_4.metric("Cancelled flights", metric_value(cancelled_flights))
kpi_5.metric("Cancellation rate", metric_value(pct(cancelled_flights, total_flights), "%"))
kpi_6.metric(
    "Avg dep delay",
    metric_value(delay_summary.get("average_departure_delay", 0), " min"),
)

if data_mode == "Snapshot" and snapshot_meta:
    st.caption(
        f"Snapshot source: {snapshot_meta.get('snapshot_id')} | Created at: {snapshot_meta.get('created_at')}"
    )


tab_ops, tab_routes, tab_airports, tab_passengers, tab_audit = st.tabs(
    [
        "Ops Summary",
        "Route Analysis",
        "Airport Analysis",
        "Passenger Impact",
        "Audit Runs",
    ]
)


with tab_ops:
    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        st.subheader("Delay and cancellation posture")
        status_df = pd.DataFrame(
            [
                {"status": "Delayed", "flights": delayed_flights},
                {"status": "Cancelled", "flights": cancelled_flights},
                {
                    "status": "Other",
                    "flights": max(total_flights - delayed_flights - cancelled_flights, 0),
                },
            ]
        ).set_index("status")
        st.bar_chart(status_df, y="flights", use_container_width=True)

    with c2:
        st.subheader("Operational thresholds")
        st.metric("Max departure delay", metric_value(delay_summary.get("max_departure_delay", 0), " min"))
        st.metric("Average arrival delay", metric_value(delay_summary.get("average_arrival_delay", 0), " min"))
        st.metric("Passenger impact rate", metric_value(impact_summary.get("impact_rate_pct", 0), "%"))


with tab_routes:
    st.subheader("Highest delay-rate routes")
    if route_df.empty:
        st.info("No route rows match the selected filters.")
    else:
        route_df["route"] = route_df["origin"] + " -> " + route_df["destination"]
        chart_df = route_df.set_index("route")[["delay_rate_pct", "avg_departure_delay"]]
        st.bar_chart(chart_df, use_container_width=True)
        st.dataframe(
            route_df[
                [
                    "route",
                    "total_flights",
                    "delayed_flights",
                    "delay_rate_pct",
                    "avg_departure_delay",
                    "max_departure_delay",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "delay_rate_pct": st.column_config.NumberColumn("Delay rate %", format="%.2f"),
                "avg_departure_delay": st.column_config.NumberColumn("Avg delay min", format="%.2f"),
            },
        )


with tab_airports:
    st.subheader("Airport cancellation pressure")
    if airport_df.empty:
        st.info("No airport rows match the selected filters.")
    else:
        chart_df = airport_df.set_index("origin")[["cancellation_rate_pct", "cancelled_flights"]]
        st.bar_chart(chart_df, use_container_width=True)
        st.dataframe(
            airport_df[
                [
                    "origin",
                    "total_flights",
                    "cancelled_flights",
                    "cancellation_rate_pct",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "cancellation_rate_pct": st.column_config.NumberColumn(
                    "Cancellation rate %",
                    format="%.2f",
                ),
            },
        )


with tab_passengers:
    st.subheader("Passenger disruption exposure")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total itineraries", metric_value(impact_summary.get("total_itineraries", 0)))
    c2.metric("Impacted itineraries", metric_value(impact_summary.get("impacted_itineraries", 0)))
    c3.metric("Impact rate", metric_value(impact_summary.get("impact_rate_pct", 0), "%"))
    c4.metric("Connection risk", metric_value(impact_summary.get("connection_risk_count", 0)))

    if impact_df.empty:
        st.info("No passenger impact rows available.")
    else:
        impact_chart = impact_df.set_index("flight_id")[["impacted_itineraries"]]
        st.bar_chart(impact_chart, use_container_width=True)
        st.dataframe(impact_df, use_container_width=True, hide_index=True)


with tab_audit:
    st.subheader("Pipeline audit runs")
    if audit_df.empty:
        st.info("No audit runs available.")
    else:
        visible_columns = [
            column
            for column in [
                "process_name",
                "status",
                "started_at",
                "finished_at",
                "records_processed",
                "records_inserted",
            ]
            if column in audit_df.columns
        ]
        st.dataframe(
            audit_df[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

    if data_mode == "Snapshot":
        st.subheader("Snapshot history")
        snapshots_df = as_df((snapshots_payload or {}).get("results", []))
        if snapshots_df.empty:
            st.info("No snapshots available.")
        else:
            snapshot_columns = [
                column
                for column in ["snapshot_id", "created_at", "source"]
                if column in snapshots_df.columns
            ]
            st.dataframe(
                snapshots_df[snapshot_columns],
                use_container_width=True,
                hide_index=True,
            )
