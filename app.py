"""
Sleep & Grades — What 996 Students Revealed
A data-storytelling Streamlit app for exploring the relationship between
sleep habits, lifestyle choices, and academic performance.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
from typing import Literal

# ─────────────────────────── Page config ───────────────────────────

st.set_page_config(
    page_title="Sleep & Grades: What 996 Students Revealed",
    page_icon="🌙",
    layout="wide",
)

# ─────────────────────────── Constants ─────────────────────────────

FREQ_ORDER = [
    "Never",
    "Rarely (1-2 times a week)",
    "Rarely (1-2 times a month)",
    "Rarely",
    "Sometimes (1-2 times a week)",
    "Sometimes (3-4 times a week)",
    "Sometimes",
    "Often (5-6 times a week)",
    "Often",
    "Every night",
    "Every day",
    "Always",
]

FREQ_SHORT = {
    "Never": "Never",
    "Rarely (1-2 times a week)": "Rarely",
    "Rarely (1-2 times a month)": "Rarely/mo",
    "Sometimes (1-2 times a week)": "Sometimes",
    "Sometimes (3-4 times a week)": "Sometimes+",
    "Often (5-6 times a week)": "Often",
    "Every night": "Every night",
    "Every day": "Every day",
    "Always": "Always",
}

SLEEP_HOURS_ORDER = [
    "Less than 4 hours",
    "4-5 hours",
    "5-6 hours",
    "6-7 hours",
    "7-8 hours",
    "More than 8 hours",
]
SLEEP_HOURS_SHORT = {
    "Less than 4 hours": "<4 h",
    "4-5 hours": "4–5 h",
    "5-6 hours": "5–6 h",
    "6-7 hours": "6–7 h",
    "7-8 hours": "7–8 h",
    "More than 8 hours": "8+ h",
}

QUALITY_ORDER = ["Very poor", "Poor", "Average", "Good", "Very good"]
STRESS_ORDER = ["No stress", "Low stress", "High stress", "Extremely high stress"]
INSOMNIA_ORDER = [
    "Never",
    "Rarely (1-2 times a week)",
    "Sometimes (3-4 times a week)",
    "Often (5-6 times a week)",
    "Every night",
]
INSOMNIA_SHORT = {
    "Never": "Never",
    "Rarely (1-2 times a week)": "Rarely",
    "Sometimes (3-4 times a week)": "Sometimes",
    "Often (5-6 times a week)": "Often",
    "Every night": "Every night",
}
PERF_ORDER = ["Poor", "Below Average", "Average", "Good", "Excellent"]
CONC_ORDER = ["Never", "Rarely", "Sometimes", "Often", "Always"]
YEAR_ORDER = ["First year", "Second year", "Third year", "Graduate student"]

# ─────────────────────────── Custom CSS ────────────────────────────

st.markdown(
    """
<style>
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1b1e2b 0%, #23273a 100%);
    border: 1px solid #353b50;
    border-radius: 12px;
    padding: 16px 20px;
}
.takeaway {
    background: linear-gradient(135deg, #0d253f 0%, #102a44 100%);
    border-left: 4px solid #4fc3f7;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0 20px 0;
    font-size: 0.97rem;
    line-height: 1.5;
    color: #e0e6f0;
}
.takeaway strong { color: #4fc3f7; }
.story-header {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 2.2rem;
    margin-bottom: 0.2rem;
}
.story-subtext {
    color: #9ea7bf;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}
.hero-card {
    background: linear-gradient(135deg, #1b1e2b 0%, #23273a 100%);
    border: 1px solid #353b50;
    border-radius: 12px;
    padding: 14px 18px;
    min-height: 92px;
}
.hero-card-title {
    color: #e9edf7;
    font-size: 1.2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
}
.hero-card-sub {
    color: #9ea7bf;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.35;
}
</style>
""",
    unsafe_allow_html=True,
)


def takeaway(text: str):
    st.markdown(f'<div class="takeaway">{text}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="story-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<div class="story-subtext">{subtitle}</div>', unsafe_allow_html=True
        )


def hero_card(title: str, subtitle: str):
    st.markdown(
        f"""
<div class="hero-card">
    <p class="hero-card-title">{title}</p>
    <p class="hero-card-sub">{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────── Data loading ──────────────────────────

FREQ_SCORE = {
    "Never": 0,
    "Rarely (1-2 times a month)": 1,
    "Rarely (1-2 times a week)": 1,
    "Sometimes (1-2 times a week)": 2,
    "Sometimes (3-4 times a week)": 3,
    "Often (5-6 times a week)": 4,
    "Often (3-4 times a week)": 3,
    "Every night": 5,
    "Every day": 5,
    "Always": 6,
    "Sometimes": 3,
    "Often": 4,
    "Rarely": 1,
}
PERF_SCORE = {"Poor": 1, "Below Average": 2, "Average": 3, "Good": 4, "Excellent": 5}
QUALITY_SCORE = {"Very poor": 1, "Poor": 2, "Average": 3, "Good": 4, "Very good": 5}
STRESS_SCORE = {
    "No stress": 0,
    "Low stress": 1,
    "High stress": 3,
    "Extremely high stress": 4,
}
IMPACT_SCORE = {
    "No impact": 0,
    "Minor impact": 1,
    "Moderate impact": 2,
    "Major impact": 3,
    "Severe impact": 4,
}
SLEEP_MID = {
    "Less than 4 hours": 3.5,
    "4-5 hours": 4.5,
    "5-6 hours": 5.5,
    "6-7 hours": 6.5,
    "7-8 hours": 7.5,
    "More than 8 hours": 8.5,
}
CONC_SCORE = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4}


@st.cache_data
def load_data() -> pd.DataFrame:
    base = Path(__file__).resolve().parent
    csv_path = ("Student Insomnia and Educational Outcomes Dataset_version-2.csv"
    )
    df = pd.read_csv(csv_path)
    df.columns = [
        "Timestamp",
        "Year",
        "Gender",
        "Difficulty_Falling_Asleep",
        "Sleep_Hours",
        "Wake_Up_Night",
        "Sleep_Quality",
        "Difficulty_Concentrating",
        "Fatigue",
        "Skip_Classes",
        "Impact_Assignments",
        "Device_Before_Sleep",
        "Caffeine",
        "Physical_Activity",
        "Stress",
        "Academic_Performance",
    ]
    df["perf_num"] = df["Academic_Performance"].map(PERF_SCORE)
    df["quality_num"] = df["Sleep_Quality"].map(QUALITY_SCORE)
    df["stress_num"] = df["Stress"].map(STRESS_SCORE)
    df["impact_num"] = df["Impact_Assignments"].map(IMPACT_SCORE)
    df["insomnia_num"] = df["Difficulty_Falling_Asleep"].map(FREQ_SCORE)
    df["wakeup_num"] = df["Wake_Up_Night"].map(FREQ_SCORE)
    df["fatigue_num"] = df["Fatigue"].map(FREQ_SCORE)
    df["skip_num"] = df["Skip_Classes"].map(FREQ_SCORE)
    df["device_num"] = df["Device_Before_Sleep"].map(FREQ_SCORE)
    df["caffeine_num"] = df["Caffeine"].map(FREQ_SCORE)
    df["activity_num"] = df["Physical_Activity"].map(FREQ_SCORE)
    df["concentration_num"] = df["Difficulty_Concentrating"].map(CONC_SCORE)
    df["sleep_mid"] = df["Sleep_Hours"].map(SLEEP_MID)
    return df


# ─────────────────────────── Layout helper ─────────────────────────


def _layout(fig, height=420, margin=None):
    """Apply a consistent dark layout to every chart."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=margin or dict(l=40, r=20, t=50, b=40),
        font=dict(family="Inter, sans-serif", size=13),
        title_font_size=16,
        hoverlabel=dict(bgcolor="#1e1e2e", font_size=13, font_color="#e0e6f0"),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# CHART 1 — THE DIAGNOSIS: HOW MUCH SLEEP?
# ═══════════════════════════════════════════════════════════════════


def chart_sleep_distribution(df):
    """Vertical bar chart showing how many students fall into each sleep bucket."""
    counts = df["Sleep_Hours"].value_counts()
    ordered = [h for h in SLEEP_HOURS_ORDER if h in counts.index]
    labels = [SLEEP_HOURS_SHORT.get(h, h) for h in ordered]
    values = [counts[h] for h in ordered]
    pcts = [v / len(df) * 100 for v in values]

    # Colour intensity: less sleep → redder
    colors = ["#e74c3c", "#e67e22", "#f1c40f", "#82e0aa", "#2ecc71", "#1abc9c"]
    colors = colors[: len(ordered)]

    fig = go.Figure(
        go.Bar(
            y=values,
            x=labels,
            orientation="v",
            marker_color=colors,
            text=[f"{v}  ({p:.0f}%)" for v, p in zip(values, pcts)],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} students<extra></extra>",
        )
    )
    fig.update_layout(
        title="How Much Sleep Are Students Really Getting?",
        xaxis_title="Sleep Duration",
        yaxis_title="Number of Students",
        showlegend=False,
    )
    return _layout(fig, height=400)


# ═══════════════════════════════════════════════════════════════════
# CHART 2 — WHY? STRESS → INSOMNIA
# ═══════════════════════════════════════════════════════════════════


def chart_stress_vs_insomnia(df):
    """Horizontal stacked bar: stress level × difficulty falling asleep (% within stress level)."""
    ct = (
        pd.crosstab(df["Stress"], df["Difficulty_Falling_Asleep"], normalize="index")
        * 100
    )
    rows = [s for s in STRESS_ORDER if s in ct.index]
    cols = [i for i in INSOMNIA_ORDER if i in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)

    long_df = ct.reset_index().melt(
        id_vars="Stress",
        var_name="Difficulty_Falling_Asleep",
        value_name="Percent",
    )

    color_map = {
        "Never": "#2ecc71",
        "Rarely (1-2 times a week)": "#82e0aa",
        "Sometimes (3-4 times a week)": "#f1c40f",
        "Often (5-6 times a week)": "#e67e22",
        "Every night": "#e74c3c",
    }

    fig = px.bar(
        long_df,
        x="Percent",
        y="Stress",
        color="Difficulty_Falling_Asleep",
        orientation="h",
        barmode="stack",
        category_orders={"Stress": rows[::-1], "Difficulty_Falling_Asleep": cols},
        color_discrete_map=color_map,
        labels={
            "Percent": "Percentage of students",
            "Stress": "Stress level",
            "Difficulty_Falling_Asleep": "Difficulty to fall asleep",
        },
        title="How Academic Stress Levels Impact Difficulty Falling Asleep",
    )
    fig.update_layout(legend_title_text="Difficulty to fall asleep")
    return _layout(fig, height=380)


# ═══════════════════════════════════════════════════════════════════
# CHART 3 — EXTERIOR FACTOR: SCREENS → SLEEP QUALITY
# ═══════════════════════════════════════════════════════════════════


def chart_device_vs_sleep_quality(
    df, normalize_mode: Literal["index", "columns"] = "index"
):
    """Heatmap: device use frequency × sleep quality with switchable normalization."""
    ct = (
        pd.crosstab(
            df["Device_Before_Sleep"],
            df["Sleep_Quality"],
            normalize=normalize_mode,
        )
        * 100
    )
    dev_order = [f for f in FREQ_ORDER if f in ct.index]
    q_order = [q for q in QUALITY_ORDER if q in ct.columns]
    ct = ct.reindex(index=dev_order, columns=q_order).fillna(0)

    row_labels = [FREQ_SHORT.get(d, d) for d in dev_order]

    fig = px.imshow(
        ct.values,
        x=q_order,
        y=row_labels,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Sleep Quality", y="Electronic Device Use Before Bed", color="%"),
    )
    subtitle = (
        "(% within each device-use group)"
        if normalize_mode == "index"
        else "(% within each sleep-quality column)"
    )
    fig.update_layout(
        title=f"Electronic Device Use Before Bed and Sleep Quality {subtitle}"
    )
    fig.update_coloraxes(colorbar_title="%")
    return _layout(fig, height=380)


def chart_screen_time_vs_fatigue(df):
    """Stacked bar: device use before bed × fatigue frequency (% within device-use group)."""
    ct = pd.crosstab(df["Device_Before_Sleep"], df["Fatigue"], normalize="index") * 100
    ct_counts = pd.crosstab(df["Device_Before_Sleep"], df["Fatigue"])

    rows = [f for f in FREQ_ORDER if f in ct.index]
    cols = [f for f in FREQ_ORDER if f in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    ct_counts = ct_counts.reindex(index=rows, columns=cols).fillna(0)

    row_labels = [
        f"{FREQ_SHORT.get(r, r)} (n={int(ct_counts.loc[r].sum())})" for r in rows
    ]
    ct.index = pd.Index(row_labels, name="Device_Before_Sleep")

    long_df = ct.reset_index().melt(
        id_vars="Device_Before_Sleep", var_name="Fatigue", value_name="Percent"
    )

    fatigue_color_map = {
        "Never": "#2ecc71",
        "Rarely": "#82e0aa",
        "Sometimes": "#f1c40f",
        "Often": "#e67e22",
        "Always": "#922b21",
    }

    fig = px.bar(
        long_df,
        x="Device_Before_Sleep",
        y="Percent",
        color="Fatigue",
        barmode="stack",
        color_discrete_map=fatigue_color_map,
        category_orders={"Device_Before_Sleep": row_labels, "Fatigue": cols},
        labels={
            "Device_Before_Sleep": "Screen use before bed",
            "Percent": "Percentage of students",
            "Fatigue": "Fatigue frequency",
        },
        title="Screen Time Before Bed vs Fatigue",
    )
    fig.update_layout(
        xaxis_title="Screen use before bed",
        yaxis_title="Percentage of students",
        legend_title="Fatigue frequency",
    )
    return _layout(fig, height=430)


# ═══════════════════════════════════════════════════════════════════
# CHART 4 — SLEEP → CONCENTRATION
# ═══════════════════════════════════════════════════════════════════


def chart_sleep_vs_concentration(df):
    """Stacked bar: sleep duration → concentration difficulty distribution."""
    ct = (
        pd.crosstab(
            df["Sleep_Hours"], df["Difficulty_Concentrating"], normalize="index"
        )
        * 100
    )
    ct_counts = pd.crosstab(df["Sleep_Hours"], df["Difficulty_Concentrating"])
    rows = [h for h in SLEEP_HOURS_ORDER if h in ct.index]
    cols = [c for c in CONC_ORDER if c in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    ct_counts = ct_counts.reindex(index=rows, columns=cols).fillna(0)

    sleep_labels = [
        f"{SLEEP_HOURS_SHORT.get(h, h)} (n={int(ct_counts.loc[h].sum())})" for h in rows
    ]
    ct.index = pd.Index(sleep_labels, name="Sleep_Hours")

    color_map = dict(
        zip(CONC_ORDER, ["#1abc9c", "#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"])
    )
    long = ct.reset_index().melt(
        id_vars="Sleep_Hours", var_name="Concentration Difficulty", value_name="Percent"
    )

    fig = px.bar(
        long,
        x="Sleep_Hours",
        y="Percent",
        color="Concentration Difficulty",
        barmode="stack",
        color_discrete_map=color_map,
        category_orders={
            "Concentration Difficulty": cols,
            "Sleep_Hours": sleep_labels,
        },
        title="Less Sleep → Harder to Focus",
    )
    fig.update_layout(
        xaxis_title="Sleep Duration",
        yaxis_title="% of Students",
        legend_title="Concentration<br>Difficulty",
    )
    return _layout(fig, height=440)


# ═══════════════════════════════════════════════════════════════════
# CHART 5 — CONCENTRATION → ACADEMIC PERFORMANCE
# ═══════════════════════════════════════════════════════════════════


def chart_concentration_vs_performance(df):
    """Stacked bar: academic performance × sleep impact on assignments (% within performance)."""
    ct = (
        pd.crosstab(
            df["Academic_Performance"],
            df["Impact_Assignments"],
            normalize="index",
        )
        * 100
    )
    ct_counts = pd.crosstab(df["Academic_Performance"], df["Impact_Assignments"])
    perf_rows = [p for p in PERF_ORDER if p in ct.index]
    impact_cols = [
        c
        for c in [
            "No impact",
            "Minor impact",
            "Moderate impact",
            "Major impact",
            "Severe impact",
        ]
        if c in ct.columns
    ]
    ct = ct.reindex(index=perf_rows, columns=impact_cols).fillna(0)
    ct_counts = ct_counts.reindex(index=perf_rows, columns=impact_cols).fillna(0)

    perf_labels = [f"{p} (n={int(ct_counts.loc[p].sum())})" for p in perf_rows]
    ct.index = pd.Index(perf_labels, name="Academic_Performance")

    long_df = ct.reset_index().melt(
        id_vars="Academic_Performance",
        var_name="Sleep_Impact_on_Assignments",
        value_name="Percent",
    )

    impact_color_map = {
        "No impact": "#2ecc71",
        "Minor impact": "#a9dfbf",
        "Moderate impact": "#f1c40f",
        "Major impact": "#e67e22",
        "Severe impact": "#e74c3c",
    }

    fig = px.bar(
        long_df,
        x="Academic_Performance",
        y="Percent",
        color="Sleep_Impact_on_Assignments",
        barmode="stack",
        color_discrete_map=impact_color_map,
        category_orders={
            "Academic_Performance": perf_labels,
            "Sleep_Impact_on_Assignments": impact_cols,
        },
        labels={
            "Academic_Performance": "Academic Performance",
            "Percent": "Percentage of students",
            "Sleep_Impact_on_Assignments": "Sleep impact on assignments",
        },
        title="Academic Performance by Sleep Impact on Assignments",
    )
    fig.update_layout(
        yaxis_title="Percentage of students", xaxis_title="Academic performance"
    )
    return _layout(fig, height=380)


def chart_concentration_difficulty_vs_academic_performance(df):
    """Stacked bar: concentration difficulty × academic performance (% within concentration)."""
    ct = (
        pd.crosstab(
            df["Difficulty_Concentrating"],
            df["Academic_Performance"],
            normalize="index",
        )
        * 100
    )
    ct_counts = pd.crosstab(df["Difficulty_Concentrating"], df["Academic_Performance"])

    conc_rows = [c for c in CONC_ORDER if c in ct.index]
    perf_cols = [p for p in PERF_ORDER if p in ct.columns]
    ct = ct.reindex(index=conc_rows, columns=perf_cols).fillna(0)
    ct_counts = ct_counts.reindex(index=conc_rows, columns=perf_cols).fillna(0)

    conc_labels = [f"{c} (n={int(ct_counts.loc[c].sum())})" for c in conc_rows]
    ct.index = pd.Index(conc_labels, name="Difficulty_Concentrating")

    long_df = ct.reset_index().melt(
        id_vars="Difficulty_Concentrating",
        var_name="Academic_Performance",
        value_name="Percent",
    )

    perf_color_map = {
        "Poor": "#e74c3c",
        "Below Average": "#e67e22",
        "Average": "#f1c40f",
        "Good": "#82e0aa",
        "Excellent": "#2ecc71",
    }

    fig = px.bar(
        long_df,
        x="Difficulty_Concentrating",
        y="Percent",
        color="Academic_Performance",
        barmode="stack",
        color_discrete_map=perf_color_map,
        category_orders={
            "Difficulty_Concentrating": conc_labels,
            "Academic_Performance": perf_cols,
        },
        labels={
            "Difficulty_Concentrating": "Concentration difficulty",
            "Percent": "Percentage of students",
            "Academic_Performance": "Academic performance",
        },
        title="Concentration Difficulty vs Academic Performance",
    )
    fig.update_layout(
        xaxis_title="Concentration difficulty",
        yaxis_title="Percentage of students",
    )
    return _layout(fig, height=400)


# ═══════════════════════════════════════════════════════════════════
# CHART 6 — THE BIG PICTURE: CORRELATION HEATMAP
# ═══════════════════════════════════════════════════════════════════


def chart_correlation_heatmap(df):
    """Correlation heatmap matched to notebook encoding/labels."""
    df_corr = df.copy()

    # Match notebook scoring exactly for the correlation view.
    perf_score = {
        "Poor": 1,
        "Below Average": 2,
        "Average": 3,
        "Good": 4,
        "Excellent": 5,
    }
    quality_score = {
        "Very poor": 1,
        "Poor": 2,
        "Average": 3,
        "Good": 4,
        "Very good": 5,
        "Excellent": 6,
    }
    stress_score = {
        "No stress": 1,
        "Low stress": 2,
        "Moderate stress": 3,
        "High stress": 4,
        "Extremely high stress": 5,
    }
    impact_score = {
        "No impact": 0,
        "Minor impact": 1,
        "Moderate impact": 2,
        "Major impact": 3,
    }

    df_corr["perf_num"] = df_corr["Academic_Performance"].map(perf_score)
    df_corr["quality_num"] = df_corr["Sleep_Quality"].map(quality_score)
    df_corr["stress_num"] = df_corr["Stress"].map(stress_score)
    df_corr["impact_num"] = df_corr["Impact_Assignments"].map(impact_score)

    freq_score = {
        "Never": 0,
        "Rarely (1-2 times a month)": 1,
        "Rarely (1-2 times a week)": 1,
        "Sometimes (1-2 times a week)": 2,
        "Sometimes (3-4 times a week)": 3,
        "Often (5-6 times a week)": 4,
        "Every night": 5,
        "Every day": 5,
        "Always": 6,
    }

    df_corr["insomnia_num"] = df_corr["Difficulty_Falling_Asleep"].map(freq_score)
    df_corr["wakeup_num"] = df_corr["Wake_Up_Night"].map(freq_score)
    df_corr["fatigue_num"] = df_corr["Fatigue"].map(freq_score)
    df_corr["skip_num"] = df_corr["Skip_Classes"].map(freq_score)
    df_corr["device_num"] = df_corr["Device_Before_Sleep"].map(freq_score)
    df_corr["caffeine_num"] = df_corr["Caffeine"].map(freq_score)
    df_corr["activity_num"] = df_corr["Physical_Activity"].map(freq_score)
    df_corr["concentration_num"] = df_corr["Difficulty_Concentrating"].map(freq_score)

    corr_vars = {
        "Insomnia Freq.": "insomnia_num",
        "Night Waking": "wakeup_num",
        "Sleep Quality": "quality_num",
        "Fatigue": "fatigue_num",
        "Concentration": "concentration_num",
        "Skip Classes": "skip_num",
        "Assignment Impact": "impact_num",
        "Device Use": "device_num",
        "Caffeine": "caffeine_num",
        "Exercise": "activity_num",
        "Stress": "stress_num",
        "Performance": "perf_num",
    }

    corr_df = df_corr[[v for v in corr_vars.values()]].dropna()
    corr_df.columns = list(corr_vars.keys())
    corr = corr_df.corr()
    n_corr = len(corr_df)

    # Match notebook mask: hide upper triangle including diagonal.
    mask = np.triu(np.ones_like(corr, dtype=bool))
    corr_masked = corr.where(~mask)

    fig = px.imshow(
        corr_masked,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        labels=dict(color="r"),
        title="Correlation Matrix: Sleep, Lifestyle & Academic Factors",
    )
    fig.update_coloraxes(colorbar_title="r")
    return _layout(fig, height=560, margin=dict(l=100, r=20, t=50, b=40))


# ═══════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════


def main():
    df = load_data()

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🌙 Filters")
        selected_years = st.multiselect(
            "Year of Study",
            options=YEAR_ORDER,
            default=YEAR_ORDER,
        )
        selected_gender = st.multiselect(
            "Gender",
            options=["Male", "Female"],
            default=["Male", "Female"],
        )
        st.divider()
        st.markdown(
            "**996 students** surveyed about sleep, stress, "
            "lifestyle habits, and academic outcomes."
        )

    filtered = df[
        df["Year"].isin(selected_years) & df["Gender"].isin(selected_gender)
    ].copy()
    if filtered.empty:
        st.warning("No data matches these filters. Please broaden your selection.")
        return

    # ── Hero section ─────────────────────────────────────────────
    st.markdown("# 🌙 Sleep & Grades — What 996 Students Revealed")
    st.markdown(
        "*Everyone says sleep matters. But how much really? "
        "996 university students were asked about their nights, their stress, "
        "and their grades. The data tells quite a story.*"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        hero_card(
            "Who?", f"{len(filtered):,} students from undergraduate to postgraduate"
        )
    with c2:
        hero_card("Where?", "Bangladesh")
    with c3:
        hero_card("When?", "Oct/Nov 2024")

    st.divider()

    # ═════════ 1. THE DIAGNOSIS ══════════════════════════════════
    section_header(
        "📊 The Diagnosis",
        "Let's start with the basics: how much sleep are students actually getting?",
    )

    st.plotly_chart(chart_sleep_distribution(filtered), use_container_width=True)

    short_sleepers = filtered[
        filtered["Sleep_Hours"].isin(["Less than 4 hours", "4-5 hours", "5-6 hours"])
    ]
    pct_under6 = len(short_sleepers) / len(filtered) * 100 if len(filtered) else 0
    pct_7plus = (
        len(filtered[filtered["Sleep_Hours"].isin(["7-8 hours", "More than 8 hours"])])
        / len(filtered)
        * 100
    )
    takeaway(
        f"<strong>Takeaway:</strong> The vast majority of students ({pct_7plus:.0f}%) "
        f"report sleeping 7 hours or more ; that sounds healthy on paper. "
        f"But the real question isn't "
        f"just <em>how long</em> they sleep, it's <em>how well</em>. "
    )

    st.divider()

    # ═════════ 2. STRESS → INSOMNIA ═════════════════════════════
    section_header(
        "😰 But why?",
        "The first suspect: the pressure cooker of university life.",
    )

    st.plotly_chart(chart_stress_vs_insomnia(filtered), use_container_width=True)

    # Compute dynamic stat
    extreme = filtered[filtered["Stress"] == "Extremely high stress"]
    if not extreme.empty:
        pct_often_every = (
            extreme["Difficulty_Falling_Asleep"]
            .isin(["Often (5-6 times a week)", "Every night"])
            .mean()
            * 100
        )
    else:
        pct_often_every = 0
    takeaway(
        f"<strong>Takeaway:</strong> Among students with <em>extremely high stress</em>, "
        f"a staggering <strong>{pct_often_every:.0f}%</strong> struggle to fall asleep "
        f"<em>often</em> or <em>every single night</em>. "
        f"Stress doesn't just feel bad, it physically keeps you awake. "
        f"But stress isn't the only culprit…"
    )

    st.divider()

    # ═════════ 3. SCREENS → SLEEP QUALITY ════════════════════════
    section_header(
        "📱 An other Suspect: Screens Before Bed",
        "Academic stress aside, what else is sabotaging sleep quality?",
    )

    device_norm_label = st.radio(
        "Normalization mode",
        options=[
            "Within each screen-use group (rows sum to 100%)",
            "Within each sleep-quality column (columns sum to 100%)",
        ],
        horizontal=True,
        help=(
            "Switch perspective: row-normalized highlights sleep-quality mix per device-use group; "
            "column-normalized shows which screen-use groups dominate each sleep-quality level."
        ),
    )
    device_norm_mode = "index" if "rows" in device_norm_label else "columns"

    st.plotly_chart(
        chart_device_vs_sleep_quality(filtered, normalize_mode=device_norm_mode),
        use_container_width=True,
    )

    st.plotly_chart(chart_screen_time_vs_fatigue(filtered), use_container_width=True)

    # Dynamic stat
    heavy_users = filtered[
        filtered["Device_Before_Sleep"].isin(
            ["Often (5-6 times a week)", "Every night"]
        )
    ]
    if not heavy_users.empty:
        pct_poor_quality = (
            heavy_users["Sleep_Quality"].isin(["Very poor", "Poor"]).mean() * 100
        )
    else:
        pct_poor_quality = 0

    takeaway(
        f"<strong>Takeaway:</strong> The data reveals a significant 'restoration gap.' "
        f"While screen use doesn't appear to degrade self-reported sleep quality, <strong>it is a primary driver of physical fatigue</strong>. "
        f"This suggests an 'illusion of rest': students may feel they are sleeping fine, but that sleep isn't actually recovery-focused. "
        f"For the <strong>{heavy_users.shape[0] / filtered.shape[0] * 100:.0f}%</strong> of students using devices before bed, "
        f"the takeaway is clear: screen times are likely the hidden tax on energy levels, even if it doesn't feel as 'ruining' your sleep."
    )

    st.divider()

    # ═════════ 4. SLEEP → CONCENTRATION ══════════════════════════
    section_header(
        "🧠 Less Sleep, Less Focus?",
        "Time to check if poor sleep actually makes it harder to concentrate.",
    )

    st.plotly_chart(chart_sleep_vs_concentration(filtered), use_container_width=True)

    short = filtered[filtered["Sleep_Hours"].isin(["Less than 4 hours", "4-5 hours"])]
    long_sleep = filtered[
        filtered["Sleep_Hours"].isin(["7-8 hours", "More than 8 hours"])
    ]
    if not short.empty and not long_sleep.empty:
        often_always_short = (
            short["Difficulty_Concentrating"].isin(["Often", "Always"]).mean() * 100
        )
        often_always_long = (
            long_sleep["Difficulty_Concentrating"].isin(["Often", "Always"]).mean()
            * 100
        )
        takeaway(
            f"<strong>Takeaway:</strong> This visualization presents counter-intuitive finding, with"
            f" students reporting the least amount of sleep claiming great concentration capabilities. "
            f"However this trend, especially for students sleeping less than 5 hours, has to be taken with "
            f"caution due to the low number of students in such cases. "
            f"Those sleeping less than 5 hours might survive on sheer adrenaline and stress hormones, but it's not sustainable from a health perspective."
        )
    else:
        takeaway(
            "<strong>Takeaway:</strong> As sleep shrinks, the red and orange zones grow — "
            "concentration difficulty increases sharply. But does it translate to worse grades?"
        )

    st.divider()

    # ═════════ 5. CONCENTRATION → PERFORMANCE ════════════════════
    section_header(
        "📉 Where it Hurts: The Assignment Struggles",
        "The final domino: does concentration difficulty actually tank academic performance?",
    )

    st.plotly_chart(
        chart_concentration_difficulty_vs_academic_performance(filtered),
        use_container_width=True,
    )

    # st.plotly_chart(
    #     chart_concentration_vs_performance(filtered), use_container_width=True
    # )

    always_conc = filtered[filtered["Difficulty_Concentrating"] == "Always"]
    never_conc = filtered[filtered["Difficulty_Concentrating"] == "Never"]
    if not always_conc.empty and not never_conc.empty:
        pct_poor_always = (
            always_conc["Academic_Performance"].isin(["Poor", "Below Average"]).mean()
            * 100
        )
        pct_good_never = (
            never_conc["Academic_Performance"].isin(["Good", "Excellent"]).mean() * 100
        )
        takeaway(
            f"<strong>Takeaway:</strong> The link is undeniable. Among students who "
            f"<em>always</em> struggle to concentrate, <strong>{pct_poor_always:.0f}%</strong> "
            f"report <em>Poor</em> or <em>Below Average</em> grades. "
            f"The chain is complete: stress → bad sleep → can't focus → grades drop."
        )
    else:
        takeaway(
            "<strong>Takeaway:</strong> Students who always struggle to focus "
            "overwhelmingly report poor grades. The domino chain is real."
        )

    st.divider()

    # ═════════ 6. THE BIG PICTURE ════════════════════════════════
    section_header(
        "🔗 The Big Picture",
        "We've traced the chain link by link. Now let's zoom out and see how "
        "every factor connects to every other — all at once.",
    )

    st.plotly_chart(chart_correlation_heatmap(filtered), use_container_width=True)

    """

    """

    takeaway(
        "<strong>Takeaway:</strong> The correlation matrix reveals the full web, and confirms what"
        " we've always suspected: student success is a house of cards. "
        "The massive <strong>0.93</strong> correlation between <em>Fatigue</em> and <em>Concentration</em> shows that sleep isn't just a luxury, it's the engine for academic performance. "
        "When you factor in the high correlation between <em>Caffeine</em> and <em>Night Waking</em> (0.78), you see a cycle where students are trying to medicate"
        " their way out of a sleep debt that is ultimately tanking their GPA."
    )

    st.divider()

    # ── Final takeaway ───────────────────────────────────────────
    st.markdown("### 🎓 The Bottom Line")
    st.info(
        """
Across nearly 1,000 responses, the story is consistent: **academic success is a byproduct of sleep hygiene**. 
When stress spikes, sleep fails, and the 'concentration tax' begins to drain student grades. 
It’s a predictable chain reaction, but there's a lever within reach. 
The data suggests that the simplest way to break this cycle is to address the screen time currently fueling the midnight fatigue.
    """
    )


if __name__ == "__main__":
    main()
