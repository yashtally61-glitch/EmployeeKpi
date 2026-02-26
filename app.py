import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Employee Performance KPI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (refined dark-industrial theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #161922;
    --border:    #2a2f3d;
    --accent:    #4f8ef7;
    --accent2:   #f7884f;
    --green:     #43d98c;
    --red:       #f74f6e;
    --text:      #e4e8f5;
    --muted:     #6b7494;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
    color: var(--text) !important;
}

/* Main background */
.stApp { background-color: var(--bg); }

/* Metric cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.kpi-label  { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; }
.kpi-value  { font-size: 36px; font-weight: 700; font-family: 'Space Mono', monospace; color: var(--accent); margin: 4px 0; }
.kpi-delta  { font-size: 13px; }
.kpi-delta.up   { color: var(--green); }
.kpi-delta.down { color: var(--red); }

/* Section headers */
.section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 28px 0 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
}

/* Streamlit metric overrides */
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px !important;
}
[data-testid="metric-container"] label  { color: var(--muted) !important; font-size: 12px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace;
    font-size: 26px !important;
}

/* Dataframe */
.dataframe { background: var(--surface) !important; }

/* Button */
.stButton > button {
    background: var(--accent); color: #fff;
    border: none; border-radius: 8px;
    font-family: 'Sora', sans-serif; font-weight: 600;
    padding: 8px 20px;
}
.stButton > button:hover { background: #3a7de8; }

/* Select / slider labels */
.stSelectbox label, .stSlider label, .stMultiSelect label { color: var(--muted) !important; font-size: 13px; }

/* Title area */
.dash-title {
    font-size: 28px; font-weight: 700; color: var(--text);
    border-left: 4px solid var(--accent);
    padding-left: 14px; margin-bottom: 4px;
}
.dash-sub { font-size: 13px; color: var(--muted); padding-left: 18px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SAMPLE DATA GENERATOR
# ─────────────────────────────────────────────
@st.cache_data
def generate_data():
    random.seed(42)
    np.random.seed(42)

    departments = ["Engineering", "Marketing", "Sales", "HR", "Product"]
    employees = []
    names = [
        "Alice Johnson", "Bob Smith", "Clara Lee", "David Park",
        "Eva Torres", "Frank Müller", "Grace Kim", "Henry Brown",
        "Iris Chen", "James Wilson", "Karen Patel", "Leo Martinez",
        "Mia Nguyen", "Nathan Scott", "Olivia Davis", "Paul Zhang",
        "Quinn Adams", "Rachel Green", "Sam Taylor", "Tina White",
    ]

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    emp_records = []
    for i, name in enumerate(names):
        dept = departments[i % len(departments)]
        base_score = np.random.randint(55, 98)
        emp_records.append({
            "ID": f"E{1000+i}",
            "Name": name,
            "Department": dept,
            "Role": random.choice(["Senior", "Mid", "Junior"]),
            "Tasks_Assigned": np.random.randint(20, 60),
            "Tasks_Completed": 0,
            "Avg_Task_Quality": round(np.random.uniform(60, 99), 1),
            "On_Time_Rate": round(np.random.uniform(55, 100), 1),
            "Productivity_Score": base_score,
            "Overdue_Tasks": np.random.randint(0, 8),
            "Collaboration_Score": round(np.random.uniform(60, 100), 1),
            "Self_Assessment": round(np.random.uniform(65, 100), 1),
        })
        emp_records[-1]["Tasks_Completed"] = int(
            emp_records[-1]["Tasks_Assigned"] * np.random.uniform(0.65, 1.0)
        )

    df = pd.DataFrame(emp_records)
    df["Completion_Rate"] = (df["Tasks_Completed"] / df["Tasks_Assigned"] * 100).round(1)
    df["Overall_KPI"] = (
        df["Productivity_Score"] * 0.35 +
        df["Completion_Rate"]    * 0.25 +
        df["On_Time_Rate"]       * 0.20 +
        df["Avg_Task_Quality"]   * 0.20
    ).round(1)
    df["Performance_Level"] = pd.cut(
        df["Overall_KPI"],
        bins=[0, 60, 70, 80, 90, 100],
        labels=["Critical", "Needs Improvement", "Good", "Excellent", "Outstanding"]
    )

    # Monthly trend (per department)
    trend_rows = []
    for dept in departments:
        score = np.random.randint(68, 82)
        for m in months:
            score = max(55, min(100, score + np.random.randint(-4, 6)))
            trend_rows.append({"Month": m, "Department": dept, "Score": score})
    trend_df = pd.DataFrame(trend_rows)

    return df, trend_df


df, trend_df = generate_data()


# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    dept_options = ["All"] + sorted(df["Department"].unique().tolist())
    selected_dept = st.selectbox("Department", dept_options)

    role_options = ["All"] + sorted(df["Role"].unique().tolist())
    selected_role = st.selectbox("Role Level", role_options)

    perf_options = ["All"] + df["Performance_Level"].cat.categories.tolist()
    selected_perf = st.selectbox("Performance Level", perf_options)

    kpi_range = st.slider(
        "Overall KPI Range", 
        min_value=0, max_value=100,
        value=(int(df["Overall_KPI"].min()), int(df["Overall_KPI"].max()))
    )

    st.markdown("---")
    st.markdown("### 📊 Metric Spotlight")
    highlight_metric = st.selectbox(
        "Drill-down by",
        ["Productivity_Score", "Completion_Rate", "On_Time_Rate", "Avg_Task_Quality"]
    )

    st.markdown("---")
    st.caption("Data: Sample · Refreshed per session")


# ─────────────────────────────────────────────
#  FILTER DATA
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="dash-title">📊 Employee Performance KPI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Task Completion & Productivity · Interactive Drill-Down</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TOP KPI METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Key Metrics — Filtered View</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Employees", len(filtered))
with c2:
    avg_kpi = filtered["Overall_KPI"].mean() if len(filtered) else 0
    st.metric("Avg Overall KPI", f"{avg_kpi:.1f}")
with c3:
    avg_comp = filtered["Completion_Rate"].mean() if len(filtered) else 0
    st.metric("Avg Completion Rate", f"{avg_comp:.1f}%")
with c4:
    avg_ontime = filtered["On_Time_Rate"].mean() if len(filtered) else 0
    st.metric("Avg On-Time Rate", f"{avg_ontime:.1f}%")
with c5:
    avg_prod = filtered["Productivity_Score"].mean() if len(filtered) else 0
    st.metric("Avg Productivity Score", f"{avg_prod:.1f}")


# ─────────────────────────────────────────────
#  ROW 1: DISTRIBUTION + PERFORMANCE LEVEL PIE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Performance Distribution</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([2, 1])

with col_a:
    fig_hist = px.histogram(
        filtered, x="Overall_KPI", nbins=15,
        color_discrete_sequence=["#4f8ef7"],
        title="Overall KPI Score Distribution",
        labels={"Overall_KPI": "Overall KPI Score"},
    )
    fig_hist.update_layout(
        plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        bargap=0.1, showlegend=False,
        xaxis=dict(gridcolor="#2a2f3d"),
        yaxis=dict(gridcolor="#2a2f3d"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    perf_counts = filtered["Performance_Level"].value_counts().reset_index()
    perf_counts.columns = ["Level", "Count"]
    fig_pie = px.pie(
        perf_counts, names="Level", values="Count",
        title="Performance Level Breakdown",
        color_discrete_sequence=["#f74f6e", "#f7884f", "#4f8ef7", "#43d98c", "#a78bfa"],
        hole=0.45,
    )
    fig_pie.update_layout(
        plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(font=dict(size=11)),
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 2: DEPARTMENT AVG KPIs + SCATTER
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Department & Individual Analysis</div>', unsafe_allow_html=True)

col_c, col_d = st.columns([1, 2])

with col_c:
    dept_agg = (
        filtered.groupby("Department")[
            ["Overall_KPI", "Completion_Rate", "On_Time_Rate", "Productivity_Score"]
        ].mean().round(1).reset_index()
    )
    fig_bar = px.bar(
        dept_agg, x="Department", y="Overall_KPI",
        color="Overall_KPI",
        color_continuous_scale=["#f74f6e", "#f7884f", "#4f8ef7", "#43d98c"],
        title="Avg KPI by Department",
        text_auto=True,
    )
    fig_bar.update_layout(
        plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2f3d"),
        yaxis=dict(gridcolor="#2a2f3d", range=[0, 105]),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_d:
    fig_scatter = px.scatter(
        filtered,
        x="Completion_Rate", y="Productivity_Score",
        size="Tasks_Assigned", color="Department",
        hover_name="Name",
        hover_data={"On_Time_Rate": True, "Avg_Task_Quality": True, "Overall_KPI": True},
        title="Completion Rate vs Productivity (size = Tasks Assigned)",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_scatter.update_layout(
        plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        xaxis=dict(gridcolor="#2a2f3d"),
        yaxis=dict(gridcolor="#2a2f3d"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 3: MONTHLY TREND
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Monthly Productivity Trend (All Departments)</div>', unsafe_allow_html=True)

trend_filter = trend_df.copy()
if selected_dept != "All":
    trend_filter = trend_filter[trend_filter["Department"] == selected_dept]

fig_line = px.line(
    trend_filter, x="Month", y="Score", color="Department",
    markers=True,
    color_discrete_sequence=["#4f8ef7", "#f7884f", "#43d98c", "#f74f6e", "#a78bfa"],
)
fig_line.update_layout(
    plot_bgcolor="#161922", paper_bgcolor="#161922",
    font_color="#e4e8f5",
    xaxis=dict(gridcolor="#2a2f3d"),
    yaxis=dict(gridcolor="#2a2f3d", range=[50, 105]),
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", y=-0.2),
)
st.plotly_chart(fig_line, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 4: METRIC SPOTLIGHT + RADAR
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-title">Drill-Down: {highlight_metric.replace("_", " ")}</div>', unsafe_allow_html=True)

col_e, col_f = st.columns([2, 1])

with col_e:
    top_n = filtered.nlargest(10, highlight_metric)[["Name", "Department", highlight_metric, "Overall_KPI"]]
    fig_top = px.bar(
        top_n.sort_values(highlight_metric),
        x=highlight_metric, y="Name",
        orientation="h",
        color=highlight_metric,
        color_continuous_scale=["#4f8ef7", "#43d98c"],
        title=f"Top 10 Employees by {highlight_metric.replace('_', ' ')}",
        text_auto=True,
    )
    fig_top.update_layout(
        plot_bgcolor="#161922", paper_bgcolor="#161922",
        font_color="#e4e8f5", title_font_size=14,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2f3d", range=[0, 110]),
        yaxis=dict(gridcolor="#0d0f14"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col_f:
    # Radar: avg KPI dimensions for filtered group
    categories = ["Productivity", "Completion", "On-Time", "Quality", "Collaboration"]
    values = [
        filtered["Productivity_Score"].mean(),
        filtered["Completion_Rate"].mean(),
        filtered["On_Time_Rate"].mean(),
        filtered["Avg_Task_Quality"].mean(),
        filtered["Collaboration_Score"].mean(),
    ] if len(filtered) else [0]*5

    fig_radar = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(79,142,247,0.2)",
        line=dict(color="#4f8ef7", width=2),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#161922",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2f3d", color="#6b7494"),
            angularaxis=dict(gridcolor="#2a2f3d", color="#e4e8f5"),
        ),
        paper_bgcolor="#161922",
        font_color="#e4e8f5",
        title=dict(text="Avg KPI Dimensions (Radar)", font=dict(size=14)),
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 5: EMPLOYEE TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Employee Detail Table</div>', unsafe_allow_html=True)

show_cols = [
    "ID", "Name", "Department", "Role",
    "Tasks_Assigned", "Tasks_Completed", "Completion_Rate",
    "Productivity_Score", "On_Time_Rate", "Avg_Task_Quality",
    "Overall_KPI", "Performance_Level"
]

def color_perf(val):
    colors = {
        "Outstanding":       "color: #a78bfa; font-weight: 700",
        "Excellent":         "color: #43d98c; font-weight: 700",
        "Good":              "color: #4f8ef7",
        "Needs Improvement": "color: #f7884f",
        "Critical":          "color: #f74f6e; font-weight: 700",
    }
    return colors.get(str(val), "")

display_df = filtered[show_cols].sort_values("Overall_KPI", ascending=False).reset_index(drop=True)

styled = display_df.style \
    .applymap(color_perf, subset=["Performance_Level"]) \
    .background_gradient(subset=["Overall_KPI"], cmap="Blues") \
    .format({"Completion_Rate": "{:.1f}%", "On_Time_Rate": "{:.1f}%", "Overall_KPI": "{:.1f}"})

st.dataframe(styled, use_container_width=True, height=350)

# Download
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Export Filtered Data as CSV",
    data=csv_data,
    file_name="employee_kpi_filtered.csv",
    mime="text/csv",
)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Employee Performance KPI Dashboard · Built with Streamlit & Plotly · Sample Data")
