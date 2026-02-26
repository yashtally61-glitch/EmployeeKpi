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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0f1117; }
[data-testid="stSidebar"] { background-color: #1a1d27 !important; border-right: 1px solid #2d3144; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1d27 0%, #1e2235 100%);
    border: 1px solid #2d3144;
    border-radius: 12px;
    padding: 18px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
[data-testid="stMetricValue"] { color: #60a5fa !important; font-size: 24px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 12px !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Section headers */
.section-hdr {
    font-size: 10px; font-weight: 700; letter-spacing: .2em;
    text-transform: uppercase; color: #475569;
    margin: 28px 0 14px;
    padding-bottom: 8px; border-bottom: 1px solid #1e2235;
}

/* Title */
.hero-title { font-size: 30px; font-weight: 700; color: #f1f5f9; margin-bottom: 2px; }
.hero-sub   { font-size: 13px; color: #64748b; margin-bottom: 24px; }
.accent     { color: #60a5fa; }

/* Performance badges */
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }

/* Scrollable table area */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Sidebar labels */
.stSelectbox label, .stSlider label, .stMultiSelect label { color: #94a3b8 !important; font-size: 12px !important; }
div[data-baseweb="select"] { background-color: #1e2235 !important; }

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; padding: 10px 24px;
    transition: all 0.2s;
}
.stDownloadButton > button:hover { opacity: 0.85; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA GENERATION — 100 employees, project-based
# ─────────────────────────────────────────────
@st.cache_data
def generate_data():
    random.seed(99)
    np.random.seed(99)

    departments = ["Engineering", "Marketing", "Sales", "HR", "Product", "Finance", "Operations", "Design"]
    roles       = ["Director", "Senior Manager", "Manager", "Senior", "Mid-Level", "Junior", "Intern"]
    projects    = [
        "Project Alpha", "Project Beta", "Project Gamma", "Project Delta",
        "Project Epsilon", "Project Zeta", "Project Eta", "Project Theta",
        "Project Iota", "Project Kappa"
    ]

    first_names = ["Aarav","Priya","Rohit","Sneha","Vikram","Anjali","Amit","Pooja","Rahul","Deepa",
                   "Karan","Nisha","Suresh","Kavya","Arjun","Meera","Nikhil","Riya","Sanjay","Divya",
                   "Aditya","Shruti","Manish","Swati","Rajesh","Komal","Varun","Neha","Sachin","Prachi",
                   "Dev","Ananya","Kunal","Simran","Tarun","Isha","Vivek","Tanya","Ashish","Pallavi",
                   "Naveen","Garima","Harsh","Ritika","Sumit","Preeti","Gaurav","Sonal","Akash","Jyoti",
                   "James","Emma","Oliver","Sophia","Liam","Ava","Noah","Isabella","William","Mia",
                   "Benjamin","Charlotte","Lucas","Amelia","Mason","Harper","Ethan","Evelyn","Alexander","Abigail",
                   "Henry","Emily","Sebastian","Elizabeth","Jacob","Sofia","Michael","Avery","Daniel","Ella",
                   "Logan","Scarlett","Jackson","Grace","Aiden","Chloe","Samuel","Victoria","David","Riley",
                   "Muhammad","Fatima","Omar","Layla","Hassan","Yasmin","Ali","Nour","Khalid","Sara"]

    last_names  = ["Sharma","Patel","Gupta","Singh","Kumar","Verma","Joshi","Shah","Mehta","Nair",
                   "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Anderson",
                   "Taylor","Thomas","Jackson","White","Harris","Martin","Thompson","Moore","Young","Allen",
                   "Khan","Ahmed","Ali","Hassan","Hussain","Malik","Qureshi","Chaudhry","Iqbal","Sheikh",
                   "Park","Kim","Lee","Choi","Jung","Yoon","Lim","Han","Oh","Seo",
                   "Chen","Wang","Li","Liu","Zhang","Huang","Zhao","Wu","Zhou","Sun",
                   "Tanaka","Yamamoto","Suzuki","Watanabe","Ito","Sato","Kobayashi","Kato","Abe","Nakamura",
                   "Silva","Santos","Oliveira","Souza","Costa","Alves","Carvalho","Gomes","Martins","Rocha",
                   "Lopez","Martinez","Rodriguez","Hernandez","Gonzalez","Perez","Sanchez","Ramirez","Torres","Flores",
                   "Muller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann"]

    records = []
    for i in range(100):
        dept      = departments[i % len(departments)]
        role      = random.choice(roles)
        project   = random.choice(projects)
        proj2     = random.choice([p for p in projects if p != project]) if random.random() > 0.5 else None

        tasks_assigned  = int(np.random.randint(15, 80))
        tasks_completed = int(tasks_assigned * np.random.uniform(0.55, 1.0))
        tasks_overdue   = int(np.random.randint(0, max(1, tasks_assigned - tasks_completed + 1)))

        quality    = round(float(np.random.uniform(50, 100)), 1)
        ontime     = round(float(np.random.uniform(45, 100)), 1)
        collab     = round(float(np.random.uniform(50, 100)), 1)
        initiative = round(float(np.random.uniform(50, 100)), 1)
        prod_score = round(float(np.random.uniform(50, 100)), 1)

        name = f"{first_names[i]} {last_names[i]}"

        records.append({
            "ID":               f"EMP{1000+i+1}",
            "Name":             name,
            "Department":       dept,
            "Role":             role,
            "Primary_Project":  project,
            "Secondary_Project": proj2 if proj2 else "—",
            "Tasks_Assigned":   tasks_assigned,
            "Tasks_Completed":  tasks_completed,
            "Tasks_Overdue":    tasks_overdue,
            "Quality_Score":    quality,
            "On_Time_Rate":     ontime,
            "Collaboration":    collab,
            "Initiative":       initiative,
            "Productivity":     prod_score,
        })

    df = pd.DataFrame(records)
    df["Completion_Rate"] = (df["Tasks_Completed"] / df["Tasks_Assigned"] * 100).round(1)
    df["Overall_KPI"] = (
        df["Productivity"]      * 0.25 +
        df["Completion_Rate"]   * 0.25 +
        df["On_Time_Rate"]      * 0.20 +
        df["Quality_Score"]     * 0.20 +
        df["Collaboration"]     * 0.10
    ).round(1)

    def assign_level(s):
        if s >= 88:  return "🏆 Outstanding"
        elif s >= 78: return "⭐ Excellent"
        elif s >= 68: return "✅ Good"
        elif s >= 55: return "⚠️ Needs Improvement"
        else:         return "🔴 Critical"

    df["Performance_Level"] = df["Overall_KPI"].apply(assign_level)

    # Monthly trend per dept
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    trend_rows = []
    for dept in departments:
        score = int(np.random.randint(65, 82))
        for m in months:
            score = max(50, min(100, score + int(np.random.randint(-5, 7))))
            trend_rows.append({"Month": m, "Department": dept, "KPI_Score": score})

    # Project summary
    proj_rows = []
    for proj in projects:
        proj_df = df[df["Primary_Project"] == proj]
        if len(proj_df) == 0:
            continue
        proj_rows.append({
            "Project": proj,
            "Team_Size": len(proj_df),
            "Avg_KPI": round(proj_df["Overall_KPI"].mean(), 1),
            "Avg_Completion": round(proj_df["Completion_Rate"].mean(), 1),
            "Avg_Quality": round(proj_df["Quality_Score"].mean(), 1),
            "Total_Tasks": proj_df["Tasks_Assigned"].sum(),
            "Completed_Tasks": proj_df["Tasks_Completed"].sum(),
            "Overdue_Tasks": proj_df["Tasks_Overdue"].sum(),
        })

    return df, pd.DataFrame(trend_rows), pd.DataFrame(proj_rows)


df, trend_df, proj_df = generate_data()

PERF_COLORS_MAP = {
    "🏆 Outstanding":      "#a78bfa",
    "⭐ Excellent":        "#34d399",
    "✅ Good":             "#60a5fa",
    "⚠️ Needs Improvement": "#fbbf24",
    "🔴 Critical":         "#f87171",
}
DEPT_COLORS = px.colors.qualitative.Bold

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    all_projects = sorted(df["Primary_Project"].unique().tolist())
    sel_project  = st.multiselect("Project", all_projects, default=all_projects)

    all_depts   = sorted(df["Department"].unique().tolist())
    sel_dept    = st.multiselect("Department", all_depts, default=all_depts)

    all_roles   = sorted(df["Role"].unique().tolist())
    sel_role    = st.multiselect("Role", all_roles, default=all_roles)

    perf_opts   = list(PERF_COLORS_MAP.keys())
    sel_perf    = st.multiselect("Performance Level", perf_opts, default=perf_opts)

    kpi_range   = st.slider("KPI Score Range", 0, 100,
                            (int(df["Overall_KPI"].min()), int(df["Overall_KPI"].max())))

    st.markdown("---")
    drill_metric = st.selectbox("Drill-down Metric",
        ["Overall_KPI", "Completion_Rate", "On_Time_Rate", "Quality_Score", "Productivity"])

    st.markdown("---")
    st.caption(f"👥 Total Employees: **{len(df)}**")
    st.caption(f"📁 Total Projects: **{len(all_projects)}**")


# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
filtered = df[
    df["Primary_Project"].isin(sel_project) &
    df["Department"].isin(sel_dept) &
    df["Role"].isin(sel_role) &
    df["Performance_Level"].isin(sel_perf) &
    (df["Overall_KPI"] >= kpi_range[0]) &
    (df["Overall_KPI"] <= kpi_range[1])
].copy()


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<p class="hero-title">📊 Employee <span class="accent">Performance</span> KPI Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">100 Employees · Project-Based Tracking · Real-Time Filters</p>', unsafe_allow_html=True)

if len(filtered) == 0:
    st.warning("⚠️ No employees match the current filters. Please adjust your selections.")
    st.stop()


# ─────────────────────────────────────────────
#  KPI SUMMARY CARDS
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">📈 Summary KPIs</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("👥 Employees",        len(filtered),
          delta=f"{len(filtered)-len(df)} vs total")
k2.metric("🎯 Avg KPI Score",    f"{filtered['Overall_KPI'].mean():.1f}",
          delta=f"{filtered['Overall_KPI'].mean() - df['Overall_KPI'].mean():+.1f} vs all")
k3.metric("✅ Avg Completion",   f"{filtered['Completion_Rate'].mean():.1f}%")
k4.metric("⏰ Avg On-Time",      f"{filtered['On_Time_Rate'].mean():.1f}%")
k5.metric("⭐ Avg Quality",      f"{filtered['Quality_Score'].mean():.1f}")
k6.metric("🔴 Total Overdue",    int(filtered['Tasks_Overdue'].sum()))


# ─────────────────────────────────────────────
#  ROW 1: KPI DISTRIBUTION + PERFORMANCE PIE
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">📊 Performance Overview</div>', unsafe_allow_html=True)
r1c1, r1c2, r1c3 = st.columns([2, 1, 1])

with r1c1:
    fig = px.histogram(filtered, x="Overall_KPI", nbins=20,
        color="Performance_Level",
        color_discrete_map=PERF_COLORS_MAP,
        title="KPI Score Distribution by Performance Level",
        labels={"Overall_KPI": "Overall KPI Score", "Performance_Level": "Level"})
    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13, bargap=0.05,
        xaxis=dict(gridcolor="#1e2235", color="#64748b"),
        yaxis=dict(gridcolor="#1e2235", color="#64748b"),
        legend=dict(font=dict(size=10), bgcolor="#1a1d27"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    perf_vc = filtered["Performance_Level"].value_counts().reset_index()
    perf_vc.columns = ["Level", "Count"]
    fig2 = px.pie(perf_vc, names="Level", values="Count",
        title="Performance Breakdown", hole=0.5,
        color="Level", color_discrete_map=PERF_COLORS_MAP)
    fig2.update_traces(textposition="outside", textfont_size=10)
    fig2.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13, showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig2, use_container_width=True)

with r1c3:
    dept_kpi = filtered.groupby("Department")["Overall_KPI"].mean().round(1).reset_index()
    dept_kpi = dept_kpi.sort_values("Overall_KPI", ascending=True)
    fig3 = px.bar(dept_kpi, x="Overall_KPI", y="Department", orientation="h",
        title="Avg KPI by Department",
        color="Overall_KPI", color_continuous_scale=["#f87171","#fbbf24","#34d399"],
        text_auto=True)
    fig3.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#1e2235", range=[0,105]),
        yaxis=dict(gridcolor="#1e2235"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 2: PROJECT ANALYSIS
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">📁 Project Performance Analysis</div>', unsafe_allow_html=True)

proj_filtered = proj_df[proj_df["Project"].isin(sel_project)].copy()

r2c1, r2c2 = st.columns([3, 2])

with r2c1:
    fig_proj = px.bar(proj_filtered.sort_values("Avg_KPI", ascending=False),
        x="Project", y=["Avg_KPI", "Avg_Completion", "Avg_Quality"],
        title="Project KPI Comparison",
        barmode="group",
        color_discrete_sequence=["#60a5fa","#34d399","#a78bfa"],
        labels={"value": "Score", "variable": "Metric"})
    fig_proj.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13,
        xaxis=dict(gridcolor="#1e2235", tickangle=-20),
        yaxis=dict(gridcolor="#1e2235", range=[0,110]),
        legend=dict(bgcolor="#1a1d27", font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=40))
    st.plotly_chart(fig_proj, use_container_width=True)

with r2c2:
    fig_bubble = px.scatter(proj_filtered,
        x="Avg_Completion", y="Avg_KPI",
        size="Team_Size", color="Avg_Quality",
        hover_name="Project",
        hover_data={"Overdue_Tasks": True, "Team_Size": True},
        title="Project Health: Completion vs KPI",
        color_continuous_scale=["#f87171","#fbbf24","#34d399"],
        size_max=50)
    fig_bubble.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13,
        xaxis=dict(gridcolor="#1e2235", title="Avg Completion Rate %"),
        yaxis=dict(gridcolor="#1e2235", title="Avg KPI Score"),
        coloraxis_colorbar=dict(title="Quality", tickfont=dict(color="#94a3b8")),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_bubble, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 3: TASK STATUS + MONTHLY TREND
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">📅 Task Tracking & Monthly Trends</div>', unsafe_allow_html=True)
r3c1, r3c2 = st.columns([1, 2])

with r3c1:
    task_data = {
        "Status": ["Completed", "In Progress / Pending", "Overdue"],
        "Count": [
            int(filtered["Tasks_Completed"].sum()),
            int((filtered["Tasks_Assigned"] - filtered["Tasks_Completed"] - filtered["Tasks_Overdue"]).clip(lower=0).sum()),
            int(filtered["Tasks_Overdue"].sum())
        ]
    }
    fig_task = px.pie(pd.DataFrame(task_data), names="Status", values="Count",
        title="Overall Task Status", hole=0.55,
        color="Status",
        color_discrete_map={"Completed":"#34d399","In Progress / Pending":"#60a5fa","Overdue":"#f87171"})
    fig_task.update_traces(textposition="outside", textfont_size=11)
    fig_task.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13,
        legend=dict(font=dict(size=10), bgcolor="#1a1d27"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_task, use_container_width=True)

with r3c2:
    tf = trend_df[trend_df["Department"].isin(sel_dept)]
    fig_trend = px.line(tf, x="Month", y="KPI_Score", color="Department",
        markers=True, title="Monthly KPI Trend by Department",
        color_discrete_sequence=DEPT_COLORS)
    fig_trend.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13,
        xaxis=dict(gridcolor="#1e2235"),
        yaxis=dict(gridcolor="#1e2235", range=[45, 105]),
        legend=dict(orientation="h", y=-0.25, bgcolor="#1a1d27", font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=40))
    st.plotly_chart(fig_trend, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 4: DRILL-DOWN + RADAR
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-hdr">🔍 Drill-Down: {drill_metric.replace("_"," ")}</div>', unsafe_allow_html=True)
r4c1, r4c2 = st.columns([2, 1])

with r4c1:
    top10 = filtered.nlargest(10, drill_metric)[["Name","Department","Primary_Project", drill_metric,"Overall_KPI"]]
    fig_top = px.bar(top10.sort_values(drill_metric),
        x=drill_metric, y="Name", orientation="h",
        color=drill_metric, color_continuous_scale=["#3b82f6","#34d399"],
        title=f"Top 10 Employees — {drill_metric.replace('_',' ')}",
        hover_data={"Department": True, "Primary_Project": True, "Overall_KPI": True},
        text_auto=True)
    fig_top.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
        font_color="#94a3b8", title_font_size=13, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#1e2235", range=[0, 110]),
        yaxis=dict(gridcolor="#1a1d27"),
        margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_top, use_container_width=True)

with r4c2:
    cats   = ["Productivity", "Completion", "On-Time", "Quality", "Collaboration", "Initiative"]
    vals   = [
        float(filtered["Productivity"].mean()),
        float(filtered["Completion_Rate"].mean()),
        float(filtered["On_Time_Rate"].mean()),
        float(filtered["Quality_Score"].mean()),
        float(filtered["Collaboration"].mean()),
        float(filtered["Initiative"].mean()),
    ]
    fig_radar = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(96,165,250,0.15)",
        line=dict(color="#60a5fa", width=2),
        marker=dict(color="#60a5fa", size=6)
    ))
    fig_radar.update_layout(
        polar=dict(bgcolor="#1a1d27",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="#2d3144", color="#64748b", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#2d3144", color="#94a3b8")),
        paper_bgcolor="#1a1d27", font_color="#94a3b8",
        title=dict(text="Avg Performance Radar", font=dict(size=13, color="#94a3b8")),
        showlegend=False,
        margin=dict(l=30, r=30, t=50, b=30))
    st.plotly_chart(fig_radar, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW 5: SCATTER — PRODUCTIVITY vs QUALITY
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">🔬 Productivity vs Quality Scatter</div>', unsafe_allow_html=True)

fig_pq = px.scatter(filtered, x="Productivity", y="Quality_Score",
    color="Department", symbol="Performance_Level",
    hover_name="Name",
    hover_data={"Primary_Project": True, "Overall_KPI": True, "Role": True},
    size="Tasks_Completed", size_max=18,
    title="Productivity vs Quality (size = Tasks Completed)",
    color_discrete_sequence=DEPT_COLORS)
fig_pq.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#1a1d27",
    font_color="#94a3b8", title_font_size=13,
    xaxis=dict(gridcolor="#1e2235", title="Productivity Score"),
    yaxis=dict(gridcolor="#1e2235", title="Quality Score"),
    legend=dict(bgcolor="#1a1d27", font=dict(size=10)),
    margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig_pq, use_container_width=True)


# ─────────────────────────────────────────────
#  PROJECT SUMMARY TABLE (clean — no styling)
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">📋 Project Summary Table</div>', unsafe_allow_html=True)
st.dataframe(
    proj_filtered.sort_values("Avg_KPI", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=320
)


# ─────────────────────────────────────────────
#  EMPLOYEE DETAIL TABLE (no pandas styling — avoids ValueError)
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">👤 Employee Detail Table</div>', unsafe_allow_html=True)

show_cols = ["ID","Name","Department","Role","Primary_Project",
             "Tasks_Assigned","Tasks_Completed","Tasks_Overdue",
             "Completion_Rate","On_Time_Rate","Quality_Score",
             "Productivity","Overall_KPI","Performance_Level"]

display_df = filtered[show_cols].sort_values("Overall_KPI", ascending=False).reset_index(drop=True)

# Use plain st.dataframe — no .style to avoid ValueError on newer Pandas/Streamlit
st.dataframe(display_df, use_container_width=True, height=420)

# Download
csv_bytes = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️  Export Employee Data as CSV",
    data=csv_bytes,
    file_name="employee_kpi_export.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Employee Performance KPI Dashboard · 100 Employees · Project-Based · Built with Streamlit & Plotly")
