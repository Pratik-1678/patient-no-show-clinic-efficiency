"""
Patient No-Show & Clinic Efficiency Analysis — Streamlit Dashboard
Run from the streamlit/ folder with: streamlit run app.py
Expects the cleaned dataset at ../data/cleaned/appointments_with_risk_segments.csv
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Patient No-Show & Clinic Efficiency Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
DATA_PATH = "../data/cleaned/appointments_with_risk_segments.csv"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["scheduled_day", "appointment_day"])
    return df

try:
    df_raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find the cleaned dataset at `{DATA_PATH}`. "
        "Run this app from the `streamlit/` folder, with `data/cleaned/appointments_with_risk_segments.csv` "
        "present one level up (see the project README)."
    )
    st.stop()

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
AGE_GROUP_ORDER = ["0-12 Child", "13-18 Teen", "19-35 Young Adult", "36-50 Adult", "51-65 Senior", "66+ Elderly"]
LEAD_BUCKET_ORDER = ["Same day", "1-3 days", "4-7 days", "8-14 days", "15-30 days", "31+ days"]
RISK_ORDER = ["Low Risk", "Medium Risk", "High Risk"]

# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.title("Filters")

date_min = df_raw["appointment_day"].min().date()
date_max = df_raw["appointment_day"].max().date()
date_range = st.sidebar.date_input(
    "Appointment date range", value=(date_min, date_max), min_value=date_min, max_value=date_max
)

gender_sel = st.sidebar.multiselect("Gender", sorted(df_raw["gender"].unique()), default=list(sorted(df_raw["gender"].unique())))
age_group_sel = st.sidebar.multiselect("Age group", AGE_GROUP_ORDER, default=AGE_GROUP_ORDER)

all_neighbourhoods = sorted(df_raw["neighbourhood"].unique())
neighbourhood_sel = st.sidebar.multiselect(
    "Neighbourhood (leave empty = all)", all_neighbourhoods, default=[]
)

reminder_sel = st.sidebar.multiselect(
    "Reminder status", ["SMS Received", "No SMS"], default=["SMS Received", "No SMS"]
)

risk_sel = st.sidebar.multiselect("Risk segment (Phase 7)", RISK_ORDER, default=RISK_ORDER)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: Kaggle Medical Appointment No Shows, cleaned in Notebook 01. "
    "One row = one scheduled appointment."
)

# ------------------------------------------------------------------
# Apply filters
# ------------------------------------------------------------------
df = df_raw.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df = df[(df["appointment_day"].dt.date >= start) & (df["appointment_day"].dt.date <= end)]

if gender_sel:
    df = df[df["gender"].isin(gender_sel)]
if age_group_sel:
    df = df[df["age_group"].isin(age_group_sel)]
if neighbourhood_sel:
    df = df[df["neighbourhood"].isin(neighbourhood_sel)]
if risk_sel:
    df = df[df["risk_segment"].isin(risk_sel)]

reminder_map = {"SMS Received": 1, "No SMS": 0}
if reminder_sel and len(reminder_sel) < 2:
    df = df[df["sms_received"] == reminder_map[reminder_sel[0]]]

if df.empty:
    st.warning("No appointments match the current filter combination. Try widening a filter.")
    st.stop()

# ------------------------------------------------------------------
# Header + KPI row
# ------------------------------------------------------------------
st.title("Patient No-Show & Clinic Efficiency Dashboard")
st.caption(f"Showing {len(df):,} of {len(df_raw):,} appointments based on current filters")

total_appts = len(df)
no_shows = int(df["no_show_flag"].sum())
show_ups = total_appts - no_shows
no_show_rate = no_shows / total_appts
avg_lead_time = df["lead_time_days"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total appointments", f"{total_appts:,}")
k2.metric("No-show rate", f"{no_show_rate:.1%}")
k3.metric("Show rate", f"{show_ups/total_appts:.1%}")
k4.metric("Total no-shows", f"{no_shows:,}")
k5.metric("Avg lead time", f"{avg_lead_time:.1f} days")

st.markdown("---")

# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Attendance Analysis", "No-Show Drivers", "Location Analysis", "Recommendations"]
)

# ==================== TAB 1: Attendance Analysis ====================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Appointment outcome")
        outcome_counts = df["no_show_flag"].map({0: "Attended", 1: "No-show"}).value_counts()
        fig = px.pie(
            values=outcome_counts.values, names=outcome_counts.index, hole=0.5,
            color=outcome_counts.index,
            color_discrete_map={"Attended": "#1D9E75", "No-show": "#E24B4A"},
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("No-show rate by weekday")
        wk = df.groupby("appointment_weekday")["no_show_flag"].agg(volume="count", no_show_rate="mean")
        wk = wk.reindex([w for w in WEEKDAY_ORDER if w in wk.index])
        fig = px.bar(wk, y="no_show_rate", text=wk["no_show_rate"].apply(lambda x: f"{x:.1%}"))
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False, yaxis_title="No-show rate", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        if "Saturday" in wk.index and wk.loc["Saturday", "volume"] < 100:
            st.caption(f"Note: Saturday has only {int(wk.loc['Saturday','volume'])} appointments in this filtered view — small sample, interpret with caution.")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("No-show rate by age group")
        ag = df.groupby("age_group")["no_show_flag"].agg(volume="count", no_show_rate="mean")
        ag = ag.reindex([a for a in AGE_GROUP_ORDER if a in ag.index])
        fig = px.bar(ag, y="no_show_rate", text=ag["no_show_rate"].apply(lambda x: f"{x:.1%}"))
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False, yaxis_title="No-show rate", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("No-show trend by month")
        df["year_month"] = df["appointment_day"].dt.to_period("M").astype(str)
        tr = df.groupby("year_month")["no_show_flag"].agg(volume="count", no_show_rate="mean").reset_index()
        fig = px.line(tr, x="year_month", y="no_show_rate", markers=True)
        fig.update_layout(yaxis_tickformat=".0%", yaxis_title="No-show rate", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Only ~6 weeks of appointment dates exist in this dataset — a short trend, not a robust seasonal signal.")

# ==================== TAB 2: No-Show Drivers ====================
with tab2:
    st.subheader("No-show rate by lead-time bucket")
    st.caption("The strongest validated driver in this project (Cramér's V = 0.295, see Notebook 03).")
    lt = df.groupby("waiting_time_group")["no_show_flag"].agg(volume="count", no_show_rate="mean")
    lt = lt.reindex([b for b in LEAD_BUCKET_ORDER if b in lt.index])
    fig = px.line(lt, y="no_show_rate", markers=True, text=lt["no_show_rate"].apply(lambda x: f"{x:.1%}"))
    fig.update_traces(textposition="top center")
    fig.update_layout(yaxis_tickformat=".0%", showlegend=False, yaxis_title="No-show rate", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Reminder status — controlled comparison")
        st.caption("Sliced by lead-time bucket to resolve the SMS confound (see Notebook 02/03).")
        rc = df.groupby(["waiting_time_group", "sms_received"])["no_show_flag"].mean().unstack()
        if set([0, 1]).issubset(rc.columns):
            rc.columns = ["No SMS", "SMS Received"]
            rc = rc.reindex([b for b in LEAD_BUCKET_ORDER if b in rc.index])
            fig = px.bar(rc, barmode="group")
            fig.update_layout(yaxis_tickformat=".0%", yaxis_title="No-show rate", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Both SMS statuses need to be present in the current filter to show this comparison.")

    with col2:
        st.subheader("No-show rate by patient history")
        def history_label(v):
            if pd.isna(v):
                return "No prior appointment"
            return "Previous no-show" if v == 1 else "Previous attended"
        df["history_label"] = df["prior_no_show"].apply(history_label)
        hs = df.groupby("history_label")["no_show_flag"].agg(volume="count", no_show_rate="mean")
        hs = hs.sort_values("no_show_rate", ascending=False)
        fig = px.bar(hs, y="no_show_rate", text=hs["no_show_rate"].apply(lambda x: f"{x:.1%}"))
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False, yaxis_title="No-show rate", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Second-strongest validated driver (Cramér's V = 0.169).")

    st.subheader("No-show rate by risk segment ")
    rs = df.groupby("risk_segment")["no_show_flag"].agg(volume="count", no_show_rate="mean").reindex(RISK_ORDER)
    fig = px.bar(rs, y="no_show_rate", text=rs["no_show_rate"].apply(lambda x: f"{x:.1%}"),
                 color=rs.index, color_discrete_map={"Low Risk": "#639922", "Medium Risk": "#EF9F27", "High Risk": "#E24B4A"})
    fig.update_layout(yaxis_tickformat=".0%", showlegend=False, yaxis_title="No-show rate", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: Location Analysis ====================
with tab3:
    st.subheader("Neighbourhood no-show rates")
    min_volume = st.slider(
        "Minimum appointment volume to include a neighbourhood (avoids ranking tiny samples)",
        min_value=10, max_value=500, value=100, step=10
    )
    loc = df.groupby("neighbourhood")["no_show_flag"].agg(volume="count", no_show_rate="mean")
    loc_filtered = loc[loc["volume"] >= min_volume].sort_values("no_show_rate", ascending=False)

    st.caption(f"{len(loc_filtered)} of {len(loc)} neighbourhoods have at least {min_volume} appointments in the current filter.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 by no-show rate** (among qualifying neighbourhoods)")
        top10_rate = loc_filtered.head(10)
        fig = px.bar(top10_rate, x="no_show_rate", y=top10_rate.index, orientation="h",
                     text=top10_rate["no_show_rate"].apply(lambda x: f"{x:.1%}"))
        fig.update_layout(xaxis_tickformat=".0%", yaxis_title="", xaxis_title="No-show rate",
                           yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Top 10 by appointment volume**")
        top10_vol = loc.sort_values("volume", ascending=False).head(10)
        fig = px.bar(top10_vol, x="volume", y=top10_vol.index, orientation="h",
                     text=top10_vol["volume"])
        fig.update_layout(yaxis_title="", xaxis_title="Appointments",
                           yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**High-volume AND above-average no-show rate** (top quartile volume, rate above the current filter's overall average)")
    overall_rate = df["no_show_flag"].mean()
    p75 = loc["volume"].quantile(0.75)
    priority = loc[(loc["volume"] >= p75) & (loc["no_show_rate"] > overall_rate)].sort_values("no_show_rate", ascending=False)
    st.dataframe(
        priority.rename(columns={"volume": "Volume", "no_show_rate": "No-Show Rate"}).style.format({"No-Show Rate": "{:.1%}"}),
        use_container_width=True,
    )

# ==================== TAB 4: Recommendations ====================
with tab4:
    st.subheader("Business recommendations")
    st.caption("Based on the validated drivers and efficiency analysis (Notebooks 03-05). These recompute against your current filter selection where the underlying pattern applies broadly.")

    long_lead = df[df["lead_time_days"] >= 8]
    long_lead_share_vol = len(long_lead) / total_appts if total_appts else 0
    long_lead_share_loss = long_lead["no_show_flag"].sum() / no_shows if no_shows else 0

    high_risk_df = df[df["risk_segment"] == "High Risk"]
    high_risk_rate = high_risk_df["no_show_flag"].mean() if len(high_risk_df) else float("nan")

    st.markdown(f"""
1. **Prioritize reconfirmation for long-lead-time bookings.** In the current filter, appointments booked
   8+ days ahead are {long_lead_share_vol:.1%} of volume but account for {long_lead_share_loss:.1%} of all
   lost appointments (no-shows). This is the single strongest, most consistent pattern in the whole project.

2. **Use the risk segmentation to target outreach.** The High Risk segment in the current filter has a
   {high_risk_rate:.1%} no-show rate (vs. {no_show_rate:.1%} overall) — concentrate reminder calls here first.

3. **Focus location-based effort on neighbourhoods that are both high-volume and above-average no-show rate**
   (see the Location Analysis tab) — these represent the best return on limited outreach capacity.

4. **Keep and consider expanding SMS reminders for long-lead-time bookings specifically** — once lead time is
   controlled for, reminders are associated with a real reduction in no-shows (see the No-Show Drivers tab).

5. **Don't ignore the "Low Risk" segment entirely** — due to sheer volume it can still contribute meaningfully
   to total lost appointments, so a baseline reminder program still has value clinic-wide.
""")

    st.info(
        "These are prioritization recommendations based on observational, historical data — not causal proof "
        "or a clinical/predictive model. See Notebook 03 for the full association-vs-causation discussion."
    )
