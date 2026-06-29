import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from database import get_all_results, get_model_summary, get_runs

st.set_page_config(
    page_title = "LLM Evaluatin Dashboard",
    page_icon = "🔬",
    layout = "wide"
)

st.title("🔬 LLM Evaluation Framework")
st.caption("SQL Generation Benchmark - Qwen3 vs LLaMA 3.1 8B vs LLaMA 4 Scout")

summary = get_model_summary()
results = get_all_results()

if not summary :
    st.warning("No results yet. Run 'python runner.py' first.")
    st.stop()
    
def short_name(model:str)->str:
    return model.split("/")[-1].replace("-instruct", "").replace("-instant", "")

df = pd.DataFrame(results)
df["model_short"] = df["model"].apply(short_name)

summary_df = pd.DataFrame(summary)
summary_df["model_short"] = summary_df["model"].apply(short_name)

st.markdown("### Overall Results")
cols = st.columns(len(summary))

for i, row in enumerate(summary):
    with cols[i]:
        name = short_name(row["model"])
        st.metric(
            label = name,
            value = f"{row['avg_total']}/5.0",
            delta = f"{round(row['avg_total'] - 3.5, 2)} vs baseline" 
        )
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Score Breakdown by Dimension")
    categories = ["Correctness","Faithfulness","Efficiency","Hallucination"]
    fig = go.Figure()
    
    colors = ["#3b82f6","#10b981","#f59e0b"]
    for i, row in enumerate(summary):
        values = [
            row["avg_correctness"],
            row["avg_faithfulness"],
            row["avg_efficiency"],
            row["avg_hallucination"]
        ]
        values_closed = values + [values[0]]
        
        cats_closed = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=cats_closed,
            fill="toself",
            name=short_name(row["model"]),
            line_color=colors[i],
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        height=350,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8")
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Average Score by Difficulty")
    diff_data = []
    for row in summary:
        for diff in ["easy", "medium", "hard"]:
            diff_data.append({
                "Model": short_name(row["model"]),
                "Difficulty": diff.capitalize(),
                "Score": row.get(f"{diff}_avg") or 0
            })

    diff_df = pd.DataFrame(diff_data)
    fig2 = px.bar(
        diff_df,
        x="Difficulty",
        y="Score",
        color="Model",
        barmode="group",
        color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"],
        range_y=[0, 5]
    )
    fig2.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    fig2.update_xaxes(gridcolor="#2d3748")
    fig2.update_yaxes(gridcolor="#2d3748")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── ROW 2: LATENCY + SCORE DISTRIBUTION ──────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Average Latency (ms)")
    latency_df = summary_df[["model_short", "avg_latency_ms"]].copy()
    latency_df.columns = ["Model", "Latency (ms)"]
    latency_df = latency_df.sort_values("Latency (ms)")

    fig3 = px.bar(
        latency_df,
        x="Model",
        y="Latency (ms)",
        color="Model",
        color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b"],
        text="Latency (ms)"
    )
    fig3.update_traces(texttemplate="%{text:.0f}ms", textposition="outside")
    fig3.update_layout(
        height=320,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8")
    )
    fig3.update_yaxes(gridcolor="#2d3748")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Score Distribution per Model")
    fig4 = px.box(
        df,
        x="model_short",
        y="total_score",
        color="model_short",
        color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"],
        points="all"
    )
    fig4.update_layout(
        height=320,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        xaxis_title="Model",
        yaxis_title="Total Score"
    )
    fig4.update_yaxes(gridcolor="#2d3748", range=[0, 5.5])
    fig4.update_xaxes(gridcolor="#2d3748")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── ROW 3: PER TEST CASE HEATMAP ─────────────────────────────────────────────
st.markdown("#### Score Heatmap — All Models x All Test Cases")

pivot = df.pivot_table(
    index="test_case_id",
    columns="model_short",
    values="total_score"
).round(1)

fig5 = px.imshow(
    pivot,
    color_continuous_scale="RdYlGn",
    zmin=1, zmax=5,
    text_auto=True,
    aspect="auto"
)
fig5.update_layout(
    height=550,
    margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8"),
    coloraxis_colorbar=dict(title="Score")
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── ROW 4: DETAILED RESULTS TABLE ────────────────────────────────────────────
st.markdown("#### Detailed Results")

filter_model = st.selectbox(
    "Filter by model",
    ["All"] + list(df["model_short"].unique())
)
filter_diff = st.selectbox(
    "Filter by difficulty",
    ["All", "Easy", "Medium", "Hard"]
)

filtered = df.copy()
if filter_model != "All":
    filtered = filtered[filtered["model_short"] == filter_model]
if filter_diff != "All":
    filtered = filtered[filtered["difficulty"] == filter_diff.lower()]

display_cols = [
    "model_short", "test_case_id", "difficulty",
    "question", "correctness_score", "faithfulness_score",
    "efficiency_score", "hallucination_score", "total_score", "latency_ms"
]

st.dataframe(
    filtered[display_cols].rename(columns={
        "model_short": "Model",
        "test_case_id": "Test Case",
        "difficulty": "Difficulty",
        "question": "Question",
        "correctness_score": "Correctness",
        "faithfulness_score": "Faithfulness",
        "efficiency_score": "Efficiency",
        "hallucination_score": "Hallucination",
        "total_score": "Total",
        "latency_ms": "Latency (ms)"
    }),
    use_container_width=True,
    height=400
)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built by Sia Shah · LLM Evaluation Framework · SQL Generation Benchmark")