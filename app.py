import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

st.set_page_config(
    page_title="Employee Performance KPI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp { background-color: #0d0f14; color: #e4e8f5; }
[data-testid="stSidebar"] { background-color: #161922 !important; border-right: 1px solid #2a2f3d; }
[data-testid="metric-container"] {
    background: #161922; border: 1px solid #2a2f3d;
    border-radius: 10px; padding: 16px !important;
}
.section-title {
    font-size: 11px; font-weight: 600; letter-spacing: .15em;
    text-transform: uppercase; color: #6b7494;
    margin: 24px 0 10px; border-bottom: 1px solid #2a2f3d; padding-bottom: 6px;
}
.dash-title {
    font-size: 26px; font-weight: 700; color: #e4e8f5;
    border-left: 4px solid #4f8ef7; padding-left: 14px; margin-bottom: 4px;
}
.dash-sub { font-size: 13px; color: #6b7494; padding-left: 18px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def generate_data():
    random.seed(42)
    np.random.seed(42)

    departments = ["Engineering", "Marketing", "Sales", "HR", "Product"]
    names = [
        "Alice Johnson", "Bob Smith", "Clara Lee", "David Park",
        "Eva Torres", "Frank Muller", "Grace Kim", "Henry Brown",
        "Iris Chen", "James Wilson", "Karen Patel", "Leo Martinez",
        "Mia Nguyen", "Nathan Scott", "Olivia Davis", "Paul Zhang",
        "Quinn Adams", "Rachel Green", "Sam Taylor", "Tina White",
    ]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    emp_records = []
    for i, name in enumerate(names):
        dept = departments[i % len(departments)]
        base_score = int(np.random.randint(55, 98))
        tasks_assigned = int(np.random.randint(20, 60))
        tasks_completed = int(tasks_assigned * np.random.uniform(0.65, 1.0))
        emp_records.append({
            "ID": f"E{1000+i}",
            "Name": name,
            "Department": dept,
            "Role": random.choice(["Senior", "Mid", "Junior"]),
            "Tasks_Assigned": tasks_assigned,
            "Tasks_Completed": tasks_completed,
            "Avg_Task_Quality": round(float(np.random.uniform(60, 99)), 1),
            "On_Time_Rate": round(float(np.random.uniform(55, 100)), 1),
            "Productivity_Score": base_score,
            "Overdue_Tasks": int(np.random.randint(0, 8)),
            "Collaboration_Score": round(float(np.random.uniform(60, 100)), 1),
        })

    df = pd.DataFrame(emp_records)
    df["Completion_Rate"] = (df["Tasks_Completed"] / df["Tasks_Assigned"] * 100).round(1)
    df["Overall_KPI"] = (
        df["Productivity_Score"] * 0.35 +
        df["Completion_Rate"]    * 0.25 +
        df["On_Time_Rate"]       * 0.20 +
        df["Avg_Task_Quality"]   * 0.20
    ).round(1)

    def assign_level(score):
        if score >= 90: return "Outstanding"
        elif score >= 80: return "Excellent"
        elif score >= 70: return "Good"
        elif score >= 60: return "Needs Improvement"
        else: return "Critical"

    df["Performance_Level"] = df["Overall_KPI"].apply(assign_level)

    trend_rows = []
    for dept in departments:
        score = int(np.random.randint(68, 82))
        for m in months:
            score = max(55, min(100, score + int(np.random.randint(-4, 6))))
            trend_rows.append({"Month": m, "Department": dept, "Score": score})

    return df, pd.DataFrame(trend_rows)


df, trend_df = generate_data()

PERF_ORDER = ["Critical", "Needs Improvement", "Good", "Excellent", "Outstanding"]
PERF_COLORS = {
    "Outstanding": "#a78bfa",
    "Excellent": "#43d98c",
    "Good": "#4f8ef7",
    "Needs Improvement": "#f7884f",
    "Critical": "#f74f6e",
}

# ── SIDEBAR ──────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")
    dept_options = ["All"] + sorted(df["Department"].unique().tolist())
    selected_dept = st.selectbox("Department", dept_options)
    role_options = ["All"] + sorted(df["Role"].unique().tolist())
    selected_role = st.selectbox("Role Level", role_options)
    perf_options = ["All"] + PERF_ORDER
    selected_perf = st.selectbox("Performance Level", perf_options)
    kpi_range = st.slider("Overall KPI Range", 0, 100,
                          (int(df["Overall_KPI"].min()), int(df["Overall_KPI"].max())))
    st.markdown("---")
    st.markdown("### 📊 Metric Spotlight")
    highlight_metric = st.selectbox("Drill-down by",
        ["Productivity_Score", "Completion_Rate", "On_Time_Rate", "Avg_Task_Quality"])
    st.markdown("---")
    st.caption("Data: Sample · Refreshed per session")

# ── FILTER ───────────────────────────────────
filtered = df.copy()
if selected_dept != "All":
    filtered = filtered[filtered["Department"] == selected_dept]
if selected_role != "All":
    filtered = filtered[filtered["Role"] == selected_role]
if selected_perf != "All":
    filtered = filtered[filtered["Performance_Level"] == selected_perf]
filtered = filtered[
    (filtered["Overall_KPI"] >= kpi_range[0]) &
    (filtered["Overall_KPI"] <= kpi_range[1])
]

# ── HEADER ───────────────────────────────────
st.markdown('<div class="dash-title">📊 Employee Performance KPI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Task Completion & Productivity · Interactive Drill-Down</div>', unsafe_allow_html=True)

if len(filtered) == 0:
    st.warning("No employees match the current filters. Please adjust the sidebar filters.")
    st.stop()

# ── KPI CARDS ────────────────────────────────
st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Employees",           len(filtered))
c2.metric("Avg Overall KPI",     f"{filtered['Overall_KPI'].mean():.1f}")
c3.metric("Avg Completion Rate", f"{filtered['Completion_Rate'].mean():.1f}%")
c4.metric("Avg On-Time Rate",    f"{filtered['On_Time_Rate'].mean():.1f}%")
c5.metric("Avg Productivity",    f"{filtered['Productivity_Score'].mean():.1f}")

# ── ROW 1: HISTOGRAM + PIE ───────────────────
st.markdown('<div class="section-title">Performance Distribution</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([2, 1])

with col_a:
    fig_hist = px.histogram(filtered, x="Overall_KPI", nbins=12,
        color_discrete_sequence=["#4f8ef7"], title="Overall KPI Score Distribution",
        labels={"Overall_KPI": "Overall KPI Score"})
    fig_hist.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14, bargap=0.1, showlegend=False,
        xaxis=dict(gridcolor="#2a2f3d"), yaxis=dict(gridcolor="#2a2f3d"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    perf_counts = filtered["Performance_Level"].value_counts().reset_index()
    perf_counts.columns = ["Level", "Count"]
    fig_pie = px.pie(perf_counts, names="Level", values="Count",
        title="Performance Level Breakdown", color="Level",
        color_discrete_map=PERF_COLORS, hole=0.45)
    fig_pie.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        margin=dict(l=10, r=10, t=40, b=10), legend=dict(font=dict(size=11)))
    st.plotly_chart(fig_pie, use_container_width=True)

# ── ROW 2: BAR + SCATTER ─────────────────────
st.markdown('<div class="section-title">Department & Individual Analysis</div>', unsafe_allow_html=True)
col_c, col_d = st.columns([1, 2])

with col_c:
    dept_agg = filtered.groupby("Department")[
        ["Overall_KPI", "Completion_Rate", "On_Time_Rate", "Productivity_Score"]
    ].mean().round(1).reset_index()
    fig_bar = px.bar(dept_agg, x="Department", y="Overall_KPI", color="Overall_KPI",
        color_continuous_scale=["#f74f6e", "#f7884f", "#4f8ef7", "#43d98c"],
        title="Avg KPI by Department", text_auto=True)
    fig_bar.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2f3d"), yaxis=dict(gridcolor="#2a2f3d", range=[0, 105]),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_d:
    fig_scatter = px.scatter(filtered, x="Completion_Rate", y="Productivity_Score",
        size="Tasks_Assigned", color="Department", hover_name="Name",
        hover_data={"On_Time_Rate": True, "Avg_Task_Quality": True, "Overall_KPI": True},
        title="Completion Rate vs Productivity (bubble = Tasks Assigned)",
        color_discrete_sequence=px.colors.qualitative.Bold)
    fig_scatter.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        xaxis=dict(gridcolor="#2a2f3d"), yaxis=dict(gridcolor="#2a2f3d"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── ROW 3: TREND LINE ────────────────────────
st.markdown('<div class="section-title">Monthly Productivity Trend</div>', unsafe_allow_html=True)
trend_filter = trend_df.copy()
if selected_dept != "All":
    trend_filter = trend_filter[trend_filter["Department"] == selected_dept]
fig_line = px.line(trend_filter, x="Month", y="Score", color="Department", markers=True,
    color_discrete_sequence=["#4f8ef7", "#f7884f", "#43d98c", "#f74f6e", "#a78bfa"])
fig_line.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
    font_color="#e4e8f5", xaxis=dict(gridcolor="#2a2f3d"),
    yaxis=dict(gridcolor="#2a2f3d", range=[50, 105]),
    margin=dict(l=10, r=10, t=10, b=30), legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig_line, use_container_width=True)

# ── ROW 4: TOP 10 BAR + RADAR ────────────────
st.markdown(f'<div class="section-title">Drill-Down: {highlight_metric.replace("_", " ")}</div>', unsafe_allow_html=True)
col_e, col_f = st.columns([2, 1])

with col_e:
    top_n = filtered.nlargest(10, highlight_metric)[["Name", "Department", highlight_metric, "Overall_KPI"]]
    fig_top = px.bar(top_n.sort_values(highlight_metric), x=highlight_metric, y="Name",
        orientation="h", color=highlight_metric,
        color_continuous_scale=["#4f8ef7", "#43d98c"],
        title=f"Top 10 by {highlight_metric.replace('_', ' ')}", text_auto=True)
    fig_top.update_layout(plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2f3d", range=[0, 110]),
        yaxis=dict(gridcolor="#0d0f14"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_top, use_container_width=True)

with col_f:
    categories = ["Productivity", "Completion", "On-Time", "Quality", "Collaboration"]
    values = [
        float(filtered["Productivity_Score"].mean()),
        float(filtered["Completion_Rate"].mean()),
        float(filtered["On_Time_Rate"].mean()),
        float(filtered["Avg_Task_Quality"].mean()),
        float(filtered["Collaboration_Score"].mean()),
    ]
    fig_radar = go.Figure(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(79,142,247,0.2)",
        line=dict(color="#4f8ef7", width=2),
    ))
    fig_radar.update_layout(
        polar=dict(bgcolor="#161922",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2f3d", color="#6b7494"),
            angularaxis=dict(gridcolor="#2a2f3d", color="#e4e8f5")),
        paper_bgcolor="#161922", font_color="#e4e8f5",
        title=dict(text="Avg KPI Radar", font=dict(size=14)),
        showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_radar, use_container_width=True)

# ── TABLE ────────────────────────────────────
st.markdown('<div class="section-title">Employee Detail Table</div>', unsafe_allow_html=True)

show_cols = ["ID", "Name", "Department", "Role",
             "Tasks_Assigned", "Tasks_Completed", "Completion_Rate",
             "Productivity_Score", "On_Time_Rate", "Avg_Task_Quality",
             "Overall_KPI", "Performance_Level"]

display_df = filtered[show_cols].sort_values("Overall_KPI", ascending=False).reset_index(drop=True)

def color_perf(val):
    return PERF_COLORS.get(str(val), "")

styled = (
    display_df.style
    .map(color_perf, subset=["Performance_Level"])
    .background_gradient(subset=["Overall_KPI"], cmap="Blues")
    .format({"Completion_Rate": "{:.1f}%", "On_Time_Rate": "{:.1f}%", "Overall_KPI": "{:.1f}"})
)

st.dataframe(styled, use_container_width=True, height=380)

csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Export Filtered Data as CSV",
    data=csv_data, file_name="employee_kpi_filtered.csv", mime="text/csv")

st.markdown("---")
st.caption("Employee Performance KPI Dashboard · Built with Streamlit & Plotly · Sample Data")
