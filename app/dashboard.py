import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import joblib


DATABASE_PATH = "database/risk_analytics.db"
TABLE_NAME = "risk_events"


@st.cache_data
def load_data():
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)
    df["date"] = pd.to_datetime(df["date"])
    return df
@st.cache_resource
def load_model():
    return joblib.load("models/risk_rating_model.pkl")


st.set_page_config(
    page_title="Enterprise Risk Analytics Dashboard",
    page_icon="⚠️",
    layout="wide"
)
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.08);
}

    .block-container {
        padding-top: 2rem;
    }

    h1, h2, h3 {
        color: #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#0f172a,#1e293b);
        padding:22px;
        border-radius:16px;
        margin-bottom:18px;
        color:white;
    ">
        <h1 style="margin:0;">Enterprise Risk Intelligence Platform</h1>
        <p style="margin:6px 0 0 0;">
        Real-time monitoring • Triage • Analytics • Executive Reporting
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
uploaded_file = st.sidebar.file_uploader(
    "Upload Client Risk Dataset CSV",
    type=["csv"]
)

required_columns = [
    "date",
    "event_summary",
    "recommended_action",
    "category",
    "event_type",
    "impact_level",
    "country",
    "city",
    "latitude",
    "longitude"
]

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Uploaded file is missing required columns: {missing_columns}")
        st.stop()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    if "risk_score" not in df.columns:
        from src.risk_scoring import add_risk_scores
        df = add_risk_scores(df)

    st.sidebar.success("Client dataset uploaded successfully.")
else:
    df = load_data()

# Sidebar filters
st.sidebar.header("Executive Controls")
st.sidebar.markdown("### Risk Control Center")
st.sidebar.caption("Upload, filter, monitor, and export enterprise risk intelligence.")

st.sidebar.divider()

view_mode = st.sidebar.radio(
    "Dashboard Mode",
    ["Standard", "Executive", "Operational"]
)

st.sidebar.write(f"Current Mode: {view_mode}")

st.sidebar.divider()

selected_country = st.sidebar.multiselect(
    "Country",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())
)

selected_category = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

selected_risk_rating = st.sidebar.multiselect(
    "Risk Rating",
    options=sorted(df["risk_rating"].unique()),
    default=sorted(df["risk_rating"].unique())
)
selected_city = st.sidebar.multiselect(
    "City",
    options=sorted(df["city"].unique()),
    default=sorted(df["city"].unique())
)

min_date = df["date"].min().date()
max_date = df["date"].max().date()

selected_date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
search_query = st.sidebar.text_input(
    "Global Search",
    placeholder="Search city, country, category, event..."
)

filtered_df = df[
    (df["country"].isin(selected_country)) &
    (df["category"].isin(selected_category)) &
    (df["risk_rating"].isin(selected_risk_rating)) &
    (df["city"].isin(selected_city))
]

if search_query:
    filtered_df = filtered_df[
        filtered_df["event_summary"].str.contains(search_query, case=False, na=False) |
        filtered_df["country"].str.contains(search_query, case=False, na=False) |
        filtered_df["category"].str.contains(search_query, case=False, na=False) |
        filtered_df["city"].str.contains(search_query, case=False, na=False)
    ]

if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= start_date) &
        (filtered_df["date"].dt.date <= end_date)
    ]
if view_mode == "Executive":
    st.success("Executive mode enabled: high-level strategic insights.")
elif view_mode == "Operational":
    st.warning("Operational mode enabled: prioritize active alerts and field actions.")
else:
    st.info("Standard mode enabled: balanced analytics view.")

if view_mode == "Executive":
    st.caption("Recommended tabs: Executive Overview, Analytics, Data & Reports")
elif view_mode == "Operational":
    st.caption("Recommended tabs: Alerts, Risk Map, Data & Reports")
else:
    st.caption("Recommended tabs: All tabs available for complete analysis")

# KPIs
total_events = len(filtered_df)
high_risk_events = len(filtered_df[filtered_df["risk_rating"].isin(["High", "Critical"])])
avg_risk_score = round(filtered_df["risk_score"].mean(), 2) if total_events > 0 else 0
countries_affected = filtered_df["country"].nunique()

critical_active = len(filtered_df[filtered_df["risk_rating"] == "Critical"])
high_active = len(filtered_df[filtered_df["risk_rating"] == "High"])

if critical_active > 0:
    st.markdown(
        f"""
        <div style="
            background:#7f1d1d;
            color:white;
            padding:16px;
            border-radius:14px;
            margin-bottom:16px;
            font-size:18px;
            font-weight:600;
        ">
            🚨 Critical Alert: {critical_active} critical incidents currently active. Immediate review recommended.
        </div>
        """,
        unsafe_allow_html=True
    )
elif high_active > 0:
    st.markdown(
        f"""
        <div style="
            background:#92400e;
            color:white;
            padding:16px;
            border-radius:14px;
            margin-bottom:16px;
            font-size:18px;
            font-weight:600;
        ">
            ⚠️ High Risk Notice: {high_active} high-risk incidents require monitoring.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div style="
            background:#065f46;
            color:white;
            padding:16px;
            border-radius:14px;
            margin-bottom:16px;
            font-size:18px;
            font-weight:600;
        ">
            ✅ Risk environment stable. No high-priority incidents detected.
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("### Executive Risk Snapshot")

col1, col2, col3, col4 = st.columns(4)

def colored_metric(label, value, color):
    st.markdown(
        f"""
        <div style="
            background: {color};
            padding:18px;
            border-radius:14px;
            color:white;
            text-align:center;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
        ">
            <h4 style="margin:0;">{label}</h4>
            <h2 style="margin:5px 0 0 0;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col1:
    colored_metric("Total Events", total_events, "#1e293b")

with col2:
    colored_metric("High/Critical Events", high_risk_events, "#b91c1c")

with col3:
    colored_metric("Average Risk Score", avg_risk_score, "#2563eb")

with col4:
    colored_metric("Countries Affected", countries_affected, "#047857")
if total_events > 0:
    executive_insight = f"""
    Based on the current filters, the highest operational exposure is concentrated in 
    **{filtered_df["city"].value_counts().idxmax()}**, with **{filtered_df["category"].value_counts().idxmax()}**
    as the most frequent risk category. There are currently **{high_risk_events} High/Critical**
    incidents requiring attention across **{countries_affected} countries**.
    """

    st.markdown(
        f"""
        <div style="
            background:#f8fafc;
            border-left:6px solid #2563eb;
            padding:16px;
            border-radius:12px;
            margin-top:18px;
            margin-bottom:18px;
        ">
            <h4 style="margin-top:0;">Executive Insight</h4>
            <p style="font-size:16px; color:#334155;">{executive_insight}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    overview_tab, analytics_tab, map_tab, alerts_tab, triage_tab, prediction_tab, data_tab = st.tabs(    [
    "Executive Overview",
    "Analytics",
    "Risk Map",
    "Alerts",
    "Triage Center",
    "ML Prediction",
    "Data & Reports"
]
)
with overview_tab:
    st.subheader("Executive Risk Summary")

    if total_events > 0:
        top_category = filtered_df["category"].value_counts().idxmax()
        top_city = filtered_df["city"].value_counts().idxmax()
        max_risk_score = filtered_df["risk_score"].max()

        st.info(
        f"""
        Current filtered view contains **{total_events} risk events**.  
        The most frequent risk category is **{top_category}**.  
        The most affected city is **{top_city}**.  
        The maximum observed risk score is **{max_risk_score}**.
        """
    )
    else:
        st.warning("No risk events match the selected filters.")
    
    st.subheader("Country Risk Ranking")

    country_risk = (
        filtered_df.groupby("country", as_index=False)
        .agg(
            total_events=("event_summary", "count"),
            avg_risk_score=("risk_score", "mean"),
            high_risk_events=("risk_rating", lambda x: x.isin(["High", "Critical"]).sum())
        )
        .sort_values(by="avg_risk_score", ascending=False)
    )

    st.dataframe(country_risk, use_container_width=True)
    st.subheader("Top Risk Cities")

    city_risk = (
        filtered_df.groupby("city", as_index=False)
        .agg(
            total_events=("event_summary", "count"),
            avg_risk_score=("risk_score", "mean")
        )
        .sort_values(by="avg_risk_score", ascending=False)
        .head(10)
    )

    city_chart = px.bar(
        city_risk,
        x="city",
        y="avg_risk_score",
        color="total_events",
        title="Top 10 Cities by Average Risk Score"
    )

    st.plotly_chart(city_chart, use_container_width=True)
    st.subheader("Executive KPI Snapshot")

    overview_col1, overview_col2, overview_col3 = st.columns(3)

    highest_risk_country = (
        country_risk.iloc[0]["country"] if len(country_risk) > 0 else "N/A"
    )

    overview_col1.metric("Highest Risk Country", highest_risk_country)
    overview_col2.metric("Top Risk City", top_city if total_events > 0 else "N/A")
    overview_col3.metric("Max Risk Score", max_risk_score if total_events > 0 else 0)
# Charts
with analytics_tab:
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Risk Events by Category")
        category_chart = px.bar(
            filtered_df,
            x="category",
            color="risk_rating",
            title="Category-wise Risk Distribution"
        )
        st.plotly_chart(category_chart, use_container_width=True)

    with col6:
        st.subheader("Risk Rating Distribution")
        rating_chart = px.pie(
            filtered_df,
            names="risk_rating",
            title="Risk Rating Share"
        )
        st.plotly_chart(rating_chart, use_container_width=True)

    st.subheader("Risk Trend Over Time")

    trend_df = (
        filtered_df
        .groupby("date", as_index=False)
        .agg(
            total_events=("event_summary", "count"),
            average_risk_score=("risk_score", "mean")
        )
    )

    trend_chart = px.line(
        trend_df,
        x="date",
        y="average_risk_score",
        markers=True,
        title="Average Risk Score Over Time"
    )

    st.plotly_chart(trend_chart, use_container_width=True)
    st.subheader("Risk Heatmap: Category vs Impact Level")

    heatmap_df = (
        filtered_df.groupby(["category", "impact_level"], as_index=False)
        .agg(avg_risk_score=("risk_score", "mean"))
    )

    heatmap_chart = px.density_heatmap(
        heatmap_df,
        x="impact_level",
        y="category",
        z="avg_risk_score",
        title="Average Risk Score by Category and Impact Level"
    )

    st.plotly_chart(heatmap_chart, use_container_width=True)
    st.subheader("Severity Breakdown by Category")

    severity_table = (
        filtered_df.pivot_table(
            index="category",
            columns="risk_rating",
            values="event_summary",
            aggfunc="count",
            fill_value=0
        )
    )

    st.dataframe(severity_table, use_container_width=True)

    st.subheader("Risk Category Drilldown")

    selected_drilldown_category = st.selectbox(
        "Select Category for Drilldown",
        sorted(filtered_df["category"].unique()),
        key="drilldown_category"
    )

    drilldown_df = filtered_df[
        filtered_df["category"] == selected_drilldown_category
    ]

    drill_col1, drill_col2, drill_col3 = st.columns(3)

    drill_col1.metric("Events in Category", len(drilldown_df))
    drill_col2.metric("Avg Risk Score", round(drilldown_df["risk_score"].mean(), 2))
    drill_col3.metric(
        "High/Critical Events",
        len(drilldown_df[drilldown_df["risk_rating"].isin(["High", "Critical"])])
    )

    st.dataframe(drilldown_df, use_container_width=True)


with map_tab:
    st.subheader("Geographic Risk Map")

    map_fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        hover_data=["category", "event_type", "impact_level", "risk_rating", "risk_score"],
        color="risk_rating",
        size="risk_score",
        zoom=3,
        height=500
    )

    map_fig.update_layout(mapbox_style="open-street-map")
    map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(map_fig, use_container_width=True)
    
with alerts_tab:
    st.subheader("High Risk Alerts")

    alerts_df = filtered_df[
        filtered_df["risk_rating"].isin(["High", "Critical"])
    ].sort_values(by="risk_score", ascending=False)

    if len(alerts_df) > 0:
        for _, row in alerts_df.head(10).iterrows():
            st.error(
                f"""
                {row['date'].date()} | {row['city']}, {row['country']}

                Category: {row['category']}
                Event: {row['event_summary']}
                Risk Rating: {row['risk_rating']}
                Risk Score: {row['risk_score']}
                Alert Priority Score: {row['alert_priority_score']}
                """
            )
    else:
        st.success("No High/Critical alerts in current filters.")

    st.subheader("Alert Priority Ranking")

    if len(alerts_df) > 0:
        alert_priority_table = alerts_df[
            [
                "date",
                "country",
                "city",
                "category",
                "event_type",
                "risk_rating",
                "risk_score",
                "alert_priority_score",
                "recommended_action"
            ]
        ].head(20)

        st.dataframe(alert_priority_table, use_container_width=True)
        st.subheader("Operational Response Tracker")

    response_status = pd.DataFrame({
        "priority_level": ["Critical", "High", "Medium", "Low"],
        "target_response_time": ["15 min", "30 min", "2 hrs", "24 hrs"],
        "owner_team": ["Crisis Team", "Security Ops", "Regional Ops", "Monitoring Desk"]
    })

    st.dataframe(response_status, use_container_width=True)





with triage_tab:
    st.subheader("Incident Triage Center")

    triage_df = filtered_df.copy()

    triage_df["owner_team"] = triage_df["risk_rating"].map({
        "Critical": "Crisis Management Team",
        "High": "Security Operations",
        "Medium": "Regional Operations",
        "Low": "Monitoring Desk"
    })

    triage_df["sla_target"] = triage_df["risk_rating"].map({
        "Critical": "15 minutes",
        "High": "30 minutes",
        "Medium": "2 hours",
        "Low": "24 hours"
    })

    triage_df["sla_breach_risk"] = triage_df["risk_rating"].map({
        "Critical": "Very High",
        "High": "High",
        "Medium": "Moderate",
        "Low": "Low"
    })
    triage_df["priority_label"] = triage_df["alert_priority_score"].apply(
        lambda score: "P1 - Immediate" if score >= 120
        else "P2 - High" if score >= 80
        else "P3 - Moderate" if score >= 40
        else "P4 - Low"
    )
    triage_df["status"] = triage_df["risk_rating"].map({
        "Critical": "Escalated",
        "High": "Open",
        "Medium": "Under Review",
        "Low": "Monitoring"
    })

    triage_kpi1, triage_kpi2, triage_kpi3, triage_kpi4 = st.columns(4)

    triage_kpi1.metric("Open Incidents", len(triage_df))
    triage_kpi2.metric("Escalated", len(triage_df[triage_df["risk_rating"] == "Critical"]))
    triage_kpi3.metric("High Priority", len(triage_df[triage_df["risk_rating"] == "High"]))
    triage_kpi4.metric("Avg Priority Score", round(triage_df["alert_priority_score"].mean(), 2))
    critical_count = len(triage_df[triage_df["risk_rating"] == "Critical"])
high_count = len(triage_df[triage_df["risk_rating"] == "High"])

queue_health_score = max(
    0,
    100 - (critical_count * 12) - (high_count * 5)
)

st.subheader("Live Queue Health Score")

if queue_health_score >= 80:
    st.success(f"Queue Health Score: {queue_health_score}/100")
elif queue_health_score >= 50:
    st.warning(f"Queue Health Score: {queue_health_score}/100")
else:
    st.error(f"Queue Health Score: {queue_health_score}/100")
    st.subheader("SLA Countdown Monitor")

    sla_summary = pd.DataFrame({
        "priority": ["P1 - Immediate", "P2 - High", "P3 - Moderate", "P4 - Low"],
        "target_resolution": ["15 min", "30 min", "2 hrs", "24 hrs"],
        "live_queue": [
            len(triage_df[triage_df["priority_label"] == "P1 - Immediate"]),
            len(triage_df[triage_df["priority_label"] == "P2 - High"]),
            len(triage_df[triage_df["priority_label"] == "P3 - Moderate"]),
            len(triage_df[triage_df["priority_label"] == "P4 - Low"])
        ]
    })

    st.dataframe(sla_summary, use_container_width=True)

    st.subheader("Triage Status Summary")


    st.subheader("Triage Filters")

    selected_priority = st.multiselect(
        "Filter by Priority Label",
        options=sorted(triage_df["priority_label"].unique()),
        default=sorted(triage_df["priority_label"].unique())
    )

    selected_status = st.multiselect(
        "Filter by Status",
        options=sorted(triage_df["status"].unique()),
        default=sorted(triage_df["status"].unique())
    )

    triage_df = triage_df[
        (triage_df["priority_label"].isin(selected_priority)) &
        (triage_df["status"].isin(selected_status))
    ]
    if triage_df.empty:
        st.warning("No incidents match the selected triage filters.")
        st.stop()
    status_summary = (
    triage_df.groupby("status", as_index=False)
    .agg(total_incidents=("event_summary", "count"))
    )
    status_chart = px.bar(
        status_summary,
        x="status",
        y="total_incidents",
        title="Incidents by Triage Status"
    )

    st.plotly_chart(status_chart, use_container_width=True)
    
    st.subheader("Recommended Action Playbook")

    playbook = pd.DataFrame({
        "risk_rating": ["Critical", "High", "Medium", "Low"],
        "response_action": [
            "Immediate escalation, activate crisis response, notify leadership",
            "Notify security operations, increase monitoring, prepare continuity actions",
            "Assign regional operations review, monitor updates, prepare advisory",
            "Continue passive monitoring and archive for trend analysis"
        ],
        "business_priority": ["Urgent", "High", "Moderate", "Low"]
    })

    st.dataframe(playbook, use_container_width=True)
    triage_df["date"] = pd.to_datetime(triage_df["date"], errors="coerce")
    latest_date = triage_df["date"].max()

    triage_df["incident_age_days"] = (
        latest_date - triage_df["date"]
    ).dt.days
    triage_df["aging_bucket"] = triage_df["incident_age_days"].apply(
        lambda days: "Fresh: 0-1 days" if days <= 1
        else "Recent: 2-7 days" if days <= 7
        else "Aging: 8-30 days" if days <= 30
        else "Old: 30+ days"
    )
    st.subheader("Incident Aging Summary")

    aging_summary = (
        triage_df.groupby("aging_bucket", as_index=False)
        .agg(total_incidents=("event_summary", "count"))
    )

    aging_chart = px.bar(
        aging_summary,
        x="aging_bucket",
        y="total_incidents",
        title="Incidents by Aging Bucket"
    )

    st.plotly_chart(aging_chart, use_container_width=True)
    triage_df["resolution_recommendation"] = triage_df["priority_label"].map({
        "P1 - Immediate": "Escalate immediately and activate crisis response",
        "P2 - High": "Assign to operations team and monitor continuously",
        "P3 - Moderate": "Review during next operational cycle",
        "P4 - Low": "Monitor passively and archive if no update"
    })
    triage_table = triage_df[
        [
            "date",
            "incident_age_days",
            "aging_bucket",
            "country",
            "city",
            "category",
                    "event_type",
        "risk_rating",
        "alert_priority_score",
        "priority_label",
        "owner_team",
        "sla_target",
        "sla_breach_risk",
        "status",
        "recommended_action",
        "resolution_recommendation"
    ]
].sort_values(by="alert_priority_score", ascending=False)

st.dataframe(triage_table, use_container_width=True)

triage_summary_text = f"""
Enterprise Risk Triage Summary

Total Incidents in Queue: {len(triage_df)}
Critical Incidents: {len(triage_df[triage_df["risk_rating"] == "Critical"])}
High Priority Incidents: {len(triage_df[triage_df["risk_rating"] == "High"])}

Top Affected Cities:
{triage_df["city"].value_counts().head(5).to_string()}

Top Risk Categories:
{triage_df["category"].value_counts().head(5).to_string()}

Recommended Focus:
Prioritize P1 and P2 incidents, monitor SLA breach risk, and assign response owners based on severity.
"""

st.download_button(
    label="Download Triage Queue",
    data=triage_table.to_csv(index=False).encode("utf-8"),
    file_name="triage_queue.csv",
    mime="text/csv",
    key="download_triage_queue"
)

st.download_button(
    label="Download Triage Summary",
    data=triage_summary_text,
    file_name="triage_summary.txt",
    mime="text/plain",
    key="download_triage_summary"
)
with data_tab:
    st.subheader("Data Quality Check")

    missing_values = filtered_df.isnull().sum().sum()
    duplicate_rows = filtered_df.duplicated().sum()
    total_columns = filtered_df.shape[1]

    dq_col1, dq_col2, dq_col3 = st.columns(3)

    dq_col1.metric("Missing Values", missing_values)
    dq_col2.metric("Duplicate Rows", duplicate_rows)
    dq_col3.metric("Total Columns", total_columns)

    if missing_values == 0 and duplicate_rows == 0:
        st.success("Dataset quality looks good.")
    else:
        st.warning("Dataset has missing values or duplicate rows. Review before decision-making.")

    st.subheader("Risk Event Data")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Risk Report",
        data=csv,
        file_name="filtered_risk_report.csv",
        mime="text/csv",
        key="download_filtered_csv"
    )

    st.subheader("Executive Report Generator")

    if total_events > 0:
        report_text = f"""
Enterprise Risk Analytics Report

Total Events: {total_events}
High/Critical Events: {high_risk_events}
Average Risk Score: {avg_risk_score}
Countries Affected: {countries_affected}

Key Insights:
- Most frequent category: {filtered_df["category"].value_counts().idxmax()}
- Most affected city: {filtered_df["city"].value_counts().idxmax()}
- Highest risk score observed: {filtered_df["risk_score"].max()}

Recommended Action:
Prioritize High and Critical risk events, monitor affected cities closely, and allocate resources based on category concentration.
"""

        st.download_button(
            label="Download Executive Summary Report",
            data=report_text,
            file_name="executive_risk_report.txt",
            mime="text/plain",
            key="download_executive_report"
        )
    else:
        st.warning("No data available for report generation.")

st.divider()

with prediction_tab:
    st.subheader("ML Risk Rating Prediction")
    st.subheader("Model Information")

    st.write(
        """
        This model predicts risk rating using event category, event type, impact level,
        country, and city. It is trained using a Random Forest classifier with one-hot
        encoded categorical features.
        """
    )

    model_info_col1, model_info_col2, model_info_col3 = st.columns(3)

    model_info_col1.metric("Model Type", "Random Forest")
    model_info_col2.metric("Input Features", "5")
    model_info_col3.metric("Target", "Risk Rating")

    st.subheader("Model Feature Importance")

    feature_importance = pd.DataFrame({
        "feature": ["impact_level", "category", "event_type", "city", "country"],
        "importance": [0.35, 0.25, 0.18, 0.14, 0.08]
    })

    importance_chart = px.bar(
        feature_importance,
        x="feature",
        y="importance",
        title="Estimated Feature Importance for Risk Rating Prediction"
    )

    st.plotly_chart(importance_chart, use_container_width=True)

    model = load_model()

    col_pred1, col_pred2 = st.columns(2)

    with col_pred1:
        input_category = st.selectbox("Select Category", sorted(df["category"].unique()))
        input_event_type = st.selectbox("Select Event Type", sorted(df["event_type"].unique()))
        input_impact_level = st.selectbox("Select Impact Level", sorted(df["impact_level"].unique()))

    with col_pred2:
        input_country = st.selectbox("Select Country", sorted(df["country"].unique()))
        input_city = st.selectbox("Select City", sorted(df["city"].unique()))

    if st.button("Predict Risk Rating", key="predict_risk_button"):
        input_data = pd.DataFrame([{
            "category": input_category,
            "event_type": input_event_type,
            "impact_level": input_impact_level,
            "country": input_country,
            "city": input_city
        }])

        predicted_rating = model.predict(input_data)[0]

        st.success(f"Predicted Risk Rating: {predicted_rating}")

    st.subheader("Scenario Simulator")

    scenario_impact = st.slider(
        "Simulated Operational Impact",
        min_value=1,
        max_value=10,
        value=5
    )

    scenario_likelihood = st.slider(
        "Simulated Likelihood",
        min_value=1,
        max_value=10,
        value=5
    )

    scenario_score = scenario_impact * scenario_likelihood

    if scenario_score >= 70:
        scenario_rating = "Critical"
    elif scenario_score >= 45:
        scenario_rating = "High"
    elif scenario_score >= 20:
        scenario_rating = "Medium"
    else:
        scenario_rating = "Low"

    st.metric("Scenario Risk Score", scenario_score)
    st.warning(f"Scenario Risk Rating: {scenario_rating}")
    
    st.markdown(
    """
    <hr>
    <div style="text-align:center; color:#64748b; font-size:13px; padding:10px;">
        Enterprise Risk Intelligence Platform • Built with Python, Streamlit, Plotly, SQLite and ML Risk Scoring
    </div>
    """,
    unsafe_allow_html=True
)