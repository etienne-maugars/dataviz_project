import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Student Insomnia and Educational Outcomes",
    page_icon="📊",
    layout="wide",
)

FREQ_ORDER = [
    "Never",
    "Rarely (1-2 times a week)",
    "Rarely (1-2 times a month)",
    "Sometimes (1-2 times a week)",
    "Sometimes (3-4 times a week)",
    "Often (5-6 times a week)",
    "Every night",
    "Every day",
    "Always",
]

FREQ_SHORT = {
    "Never": "Never",
    "Rarely (1-2 times a week)": "Rarely",
    "Rarely (1-2 times a month)": "Rarely/mo",
    "Sometimes (1-2 times a week)": "Sometimes 1-2",
    "Sometimes (3-4 times a week)": "Sometimes 3-4",
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

QUALITY_ORDER = ["Very poor", "Poor", "Average", "Good", "Very good", "Excellent"]
STRESS_ORDER = ["No stress", "Low stress", "Moderate stress", "High stress", "Extremely high stress"]
PERF_ORDER = ["Poor", "Below Average", "Average", "Good", "Excellent"]
IMPACT_ORDER_FULL = ["No impact", "Minor impact", "Moderate impact", "Major impact", "Severe impact"]
YEAR_ORDER = ["First year", "Second year", "Third year", "Graduate student"]
CONC_ORDER = ["Never", "Rarely", "Sometimes", "Often", "Always"]


@st.cache_data
def load_data() -> pd.DataFrame:
    base = Path(__file__).resolve().parent
    csv_path = (
        base.parent
        / "Student Insomnia and Educational Outcomes Dataset"
        / "Student Insomnia and Educational Outcomes Dataset_version-2.csv"
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

    perf_score = {"Poor": 1, "Below Average": 2, "Average": 3, "Good": 4, "Excellent": 5}
    quality_score = {"Very poor": 1, "Poor": 2, "Average": 3, "Good": 4, "Very good": 5, "Excellent": 6}
    stress_score = {
        "No stress": 1,
        "Low stress": 2,
        "Moderate stress": 3,
        "High stress": 4,
        "Extremely high stress": 5,
    }
    impact_score = {"No impact": 0, "Minor impact": 1, "Moderate impact": 2, "Major impact": 3, "Severe impact": 4}
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

    df["perf_num"] = df["Academic_Performance"].map(perf_score)
    df["quality_num"] = df["Sleep_Quality"].map(quality_score)
    df["stress_num"] = df["Stress"].map(stress_score)
    df["impact_num"] = df["Impact_Assignments"].map(impact_score)

    df["insomnia_num"] = df["Difficulty_Falling_Asleep"].map(freq_score)
    df["wakeup_num"] = df["Wake_Up_Night"].map(freq_score)
    df["fatigue_num"] = df["Fatigue"].map(freq_score)
    df["skip_num"] = df["Skip_Classes"].map(freq_score)
    df["device_num"] = df["Device_Before_Sleep"].map(freq_score)
    df["caffeine_num"] = df["Caffeine"].map(freq_score)
    df["activity_num"] = df["Physical_Activity"].map(freq_score)
    df["concentration_num"] = df["Difficulty_Concentrating"].map(freq_score)
    return df


def show_fig(fig):
    st.plotly_chart(fig, use_container_width=True)


def viz1(df):
    ct = pd.crosstab(df["Sleep_Quality"], df["Academic_Performance"])
    ct = ct.reindex(index=[q for q in QUALITY_ORDER if q in ct.index], columns=[p for p in PERF_ORDER if p in ct.columns]).fillna(0)
    fig = px.imshow(
        ct,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels={"x": "Academic Performance", "y": "Sleep Quality", "color": "Students"},
        title=f"Viz 1: Sleep Quality vs Academic Performance (N={int(ct.values.sum())})",
    )
    return fig


def viz2(df):
    ct = pd.crosstab(df["Year"], df["Sleep_Hours"], normalize="index") * 100
    rows = [y for y in YEAR_ORDER if y in ct.index]
    cols = [h for h in SLEEP_HOURS_ORDER if h in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    long = ct.reset_index().melt(id_vars="Year", var_name="Sleep_Hours", value_name="Percent")
    fig = px.bar(
        long,
        x="Year",
        y="Percent",
        color="Sleep_Hours",
        barmode="group",
        category_orders={"Year": rows, "Sleep_Hours": cols},
        title="Viz 2: Sleep Duration Distribution by Year",
    )
    fig.update_layout(yaxis_title="Students (%)", xaxis_title="")
    return fig


def viz3(df):
    ct = pd.crosstab(df["Stress"], df["Difficulty_Falling_Asleep"], normalize="index") * 100
    rows = [s for s in STRESS_ORDER if s in ct.index]
    cols = [f for f in FREQ_ORDER if f in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    long = ct.reset_index().melt(id_vars="Stress", var_name="Difficulty_Falling_Asleep", value_name="Percent")
    fig = px.bar(
        long,
        y="Stress",
        x="Percent",
        color="Difficulty_Falling_Asleep",
        orientation="h",
        barmode="stack",
        category_orders={"Stress": rows, "Difficulty_Falling_Asleep": cols},
        title="Viz 3: Stress vs Insomnia Frequency",
    )
    fig.update_layout(xaxis_title="Students (%)", yaxis_title="")
    return fig


def viz4(df):
    order = [f for f in FREQ_ORDER if f in df["Caffeine"].dropna().unique()]
    stats = df.groupby("Caffeine")["quality_num"].agg(["mean", "count", "sem"]).reindex(order)
    stats = stats.reset_index()
    stats["label"] = stats["Caffeine"].map(FREQ_SHORT)
    stats["ci"] = stats["sem"] * 1.96
    fig = px.bar(
        stats,
        x="label",
        y="mean",
        error_y="ci",
        color="mean",
        color_continuous_scale="RdBu",
        title="Viz 4: Caffeine Consumption vs Sleep Quality",
        hover_data={"count": True, "mean": ":.2f", "ci": ":.2f"},
    )
    fig.add_hline(y=df["quality_num"].mean(), line_dash="dash", annotation_text="Overall mean")
    fig.update_layout(yaxis_title="Mean Sleep Quality Score (1-6)", xaxis_title="Caffeine Frequency", showlegend=False)
    return fig


def viz5(df):
    ct = pd.crosstab(df["Academic_Performance"], df["Impact_Assignments"], normalize="index") * 100
    rows = [p for p in PERF_ORDER if p in ct.index]
    cols = [i for i in IMPACT_ORDER_FULL if i in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    long = ct.reset_index().melt(id_vars="Academic_Performance", var_name="Impact_Assignments", value_name="Percent")
    fig = px.bar(
        long,
        x="Academic_Performance",
        y="Percent",
        color="Impact_Assignments",
        barmode="stack",
        category_orders={"Academic_Performance": rows, "Impact_Assignments": cols},
        title="Viz 5: Sleep Impact on Assignments by Performance",
    )
    fig.update_layout(yaxis_title="Students (%)")
    return fig


def viz6(df):
    gender_means = df.groupby("Gender")[["quality_num", "stress_num", "perf_num"]].mean()
    gender_means.columns = ["Sleep Quality", "Stress", "Performance"]
    gender_means = gender_means.loc[gender_means.index.isin(["Male", "Female"])].reset_index()
    long = gender_means.melt(id_vars="Gender", var_name="Metric", value_name="Mean")
    fig = px.bar(
        long,
        x="Gender",
        y="Mean",
        color="Metric",
        barmode="group",
        title="Viz 6: Gender Differences in Sleep, Stress, and Performance",
    )
    fig.update_layout(yaxis_title="Mean Score")
    return fig


def viz7(df):
    ct = pd.crosstab(df["Device_Before_Sleep"], df["Sleep_Quality"], normalize="index") * 100
    rows = [f for f in FREQ_ORDER if f in ct.index]
    cols = [q for q in QUALITY_ORDER if q in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    ct.index = [FREQ_SHORT.get(x, x) for x in ct.index]
    fig = px.imshow(
        ct,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale="BuPu",
        labels={"x": "Sleep Quality", "y": "Device Use Frequency", "color": "Students (%)"},
        title="Viz 7: Device Use Before Sleep vs Sleep Quality",
    )
    return fig


def viz8(df):
    order = [f for f in FREQ_ORDER if f in df["Physical_Activity"].dropna().unique()]
    stats = df.groupby("Physical_Activity")["perf_num"].agg(["mean", "count", "sem"]).reindex(order)
    stats = stats.reset_index()
    stats["label"] = stats["Physical_Activity"].map(FREQ_SHORT)
    stats["ci"] = stats["sem"] * 1.96
    fig = px.bar(
        stats,
        x="label",
        y="mean",
        error_y="ci",
        color="mean",
        color_continuous_scale="YlGn",
        title="Viz 8: Physical Activity vs Academic Performance",
        hover_data={"count": True, "mean": ":.2f", "ci": ":.2f"},
    )
    fig.add_hline(y=df["perf_num"].mean(), line_dash="dash", annotation_text="Overall mean")
    fig.update_layout(yaxis_title="Mean Academic Performance Score (1-5)", xaxis_title="Physical Activity Frequency", showlegend=False)
    return fig


def viz9(df):
    ct = pd.crosstab(df["Sleep_Hours"], df["Difficulty_Concentrating"], normalize="index") * 100
    rows = [h for h in SLEEP_HOURS_ORDER if h in ct.index]
    cols = [c for c in CONC_ORDER if c in ct.columns]
    ct = ct.reindex(index=rows, columns=cols).fillna(0)
    long = ct.reset_index().melt(id_vars="Sleep_Hours", var_name="Difficulty_Concentrating", value_name="Percent")
    fig = px.bar(
        long,
        y="Sleep_Hours",
        x="Percent",
        color="Difficulty_Concentrating",
        orientation="h",
        barmode="stack",
        category_orders={"Sleep_Hours": rows, "Difficulty_Concentrating": cols},
        title="Viz 9: Concentration Difficulty by Sleep Hours",
    )
    fig.update_layout(xaxis_title="Students (%)", yaxis_title="Sleep Duration")
    return fig


def viz10(df):
    corr_vars = {
        "Insomnia": "insomnia_num",
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
    corr_df = df[list(corr_vars.values())].dropna().rename(columns={v: k for k, v in corr_vars.items()})
    corr = corr_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.mask(mask)
    fig = px.imshow(
        corr_masked,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        labels={"x": "", "y": "", "color": "Correlation"},
        title="Viz 10: Correlation Matrix of Sleep, Lifestyle, and Outcomes",
    )
    return fig


def viz11(df):
    skip_pivot = df.pivot_table(values="skip_num", index="Sleep_Quality", columns="Stress", aggfunc="mean")
    skip_counts = df.pivot_table(values="skip_num", index="Sleep_Quality", columns="Stress", aggfunc="count")
    rows = [q for q in QUALITY_ORDER if q in skip_pivot.index]
    cols = [s for s in STRESS_ORDER if s in skip_pivot.columns]
    skip_pivot = skip_pivot.reindex(index=rows, columns=cols)
    skip_counts = skip_counts.reindex(index=rows, columns=cols).fillna(0)

    text = skip_pivot.copy().astype(str)
    for r in rows:
        for c in cols:
            val = skip_pivot.loc[r, c]
            cnt = int(skip_counts.loc[r, c])
            text.loc[r, c] = f"{val:.1f}<br>(n={cnt})" if pd.notna(val) else ""

    fig = go.Figure(
        data=go.Heatmap(
            z=skip_pivot.values,
            x=cols,
            y=rows,
            text=text.values,
            texttemplate="%{text}",
            colorscale="OrRd",
            colorbar={"title": "Mean class skipping score"},
            hovertemplate="Sleep Quality=%{y}<br>Stress=%{x}<br>Mean Skip=%{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(title="Viz 11: Class Skipping by Sleep Quality and Stress")
    return fig


def story_insights(df):
    low_stress = df[df["Stress"].isin(["No stress", "Low stress"])]
    high_stress = df[df["Stress"].isin(["High stress", "Extremely high stress"])]
    low_sleep = df[df["Sleep_Hours"].isin(["Less than 4 hours", "4-5 hours", "5-6 hours"])]
    high_sleep = df[df["Sleep_Hours"].isin(["7-8 hours", "More than 8 hours"])]

    stress_gap_quality = (
        low_stress["quality_num"].mean() - high_stress["quality_num"].mean()
        if not low_stress.empty and not high_stress.empty
        else np.nan
    )
    sleep_gap_perf = (
        high_sleep["perf_num"].mean() - low_sleep["perf_num"].mean()
        if not high_sleep.empty and not low_sleep.empty
        else np.nan
    )
    corr = df[["stress_num", "quality_num", "perf_num", "concentration_num"]].corr(numeric_only=True)

    return {
        "stress_gap_quality": stress_gap_quality,
        "sleep_gap_perf": sleep_gap_perf,
        "stress_perf_corr": corr.loc["stress_num", "perf_num"] if "stress_num" in corr.index else np.nan,
        "quality_perf_corr": corr.loc["quality_num", "perf_num"] if "quality_num" in corr.index else np.nan,
    }


def headline_line(insights):
    a = insights["stress_gap_quality"]
    b = insights["sleep_gap_perf"]
    if pd.notna(a) and pd.notna(b):
        return (
            f"In this cohort, moving from high to low stress aligns with about {a:.2f} points higher sleep quality, "
            f"and longer sleepers show about {b:.2f} points higher academic performance."
        )
    return "Filters selected a small slice of data; broaden filters to reveal stronger patterns."


def run_scenario(df):
    st.markdown("### Scenario Lab: If Stress Dropped, What Might Improve?")
    st.caption("This is a simple evidence-based estimate from observed group differences, not a causal model.")

    shift_pct = st.slider("Hypothetical share of high-stress students moving to low-stress", 0, 100, 25, 5)
    low = df[df["Stress"].isin(["No stress", "Low stress"])]
    high = df[df["Stress"].isin(["High stress", "Extremely high stress"])]

    if low.empty or high.empty:
        st.info("Not enough stress-level variation under current filters to run the scenario.")
        return

    gap_quality = low["quality_num"].mean() - high["quality_num"].mean()
    gap_perf = low["perf_num"].mean() - high["perf_num"].mean()
    lift_quality = gap_quality * (shift_pct / 100.0)
    lift_perf = gap_perf * (shift_pct / 100.0)

    c1, c2 = st.columns(2)
    c1.metric("Estimated Sleep Quality Lift", f"+{lift_quality:.2f}")
    c2.metric("Estimated Performance Lift", f"+{lift_perf:.2f}")


def render_act_1(df):
    st.subheader("Act 1: The Pressure Cooker")
    st.markdown("Academic pressure appears to escalate insomnia, and poorer sleep quality lines up with weaker performance.")
    show_fig(viz3(df))
    show_fig(viz1(df))


def render_act_2(df):
    st.subheader("Act 2: Lifestyle Side Quests")
    st.markdown("Caffeine habits and bedtime device use seem to shape sleep quality, while sleep duration shifts by year.")
    c1, c2 = st.columns(2)
    with c1:
        show_fig(viz4(df))
    with c2:
        show_fig(viz7(df))
    show_fig(viz2(df))


def render_act_3(df):
    st.subheader("Act 3: The Classroom Consequences")
    st.markdown("As sleep worsens, concentration suffers, assignment impact grows, and class skipping intensifies.")
    show_fig(viz9(df))
    show_fig(viz5(df))
    show_fig(viz11(df))


def render_act_4(df):
    st.subheader("Act 4: Different Students, Similar Pattern")
    st.markdown("Across groups, lifestyle and sleep signals continue to align with academic outcomes.")
    c1, c2 = st.columns(2)
    with c1:
        show_fig(viz6(df))
    with c2:
        show_fig(viz8(df))


def render_act_5(df):
    st.subheader("Act 5: Evidence Board")
    st.markdown("The correlation map summarizes the network of links among stress, sleep, behavior, and performance.")
    show_fig(viz10(df))


def main():
    df = load_data()

    st.title("Student Insomnia and Educational Outcomes")
    st.markdown(
        """
This interactive MVP is built as a story, not a chart dump.

**Plotline:** stress and lifestyle habits shape sleep, and sleep quality echoes through concentration, attendance,
assignment completion, and academic performance.
"""
    )

    with st.sidebar:
        st.header("Story Controls")
        selected_years = st.multiselect(
            "Filter by Year of Study",
            options=sorted(df["Year"].dropna().unique()),
            default=sorted(df["Year"].dropna().unique()),
        )
        selected_gender = st.multiselect(
            "Filter by Gender",
            options=sorted(df["Gender"].dropna().unique()),
            default=sorted(df["Gender"].dropna().unique()),
        )
        show_all = st.toggle("Auto-play all acts", value=True)
        selected_act = st.radio(
            "Choose an act",
            [
                "Act 1: The Pressure Cooker",
                "Act 2: Lifestyle Side Quests",
                "Act 3: The Classroom Consequences",
                "Act 4: Different Students, Similar Pattern",
                "Act 5: Evidence Board",
            ],
            disabled=show_all,
        )

    filtered = df[df["Year"].isin(selected_years) & df["Gender"].isin(selected_gender)].copy()

    if filtered.empty:
        st.warning("No records match the current filters. Select at least one Year and one Gender.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Responses", f"{len(filtered):,}")
    c2.metric("Mean Sleep Quality (1-6)", f"{filtered['quality_num'].mean():.2f}")
    c3.metric("Mean Academic Performance (1-5)", f"{filtered['perf_num'].mean():.2f}")

    insights = story_insights(filtered)
    st.success(headline_line(insights))
    c4, c5 = st.columns(2)
    c4.metric("Stress -> Performance Correlation", f"{insights['stress_perf_corr']:.2f}")
    c5.metric("Sleep Quality -> Performance Correlation", f"{insights['quality_perf_corr']:.2f}")

    st.divider()

    if show_all:
        render_act_1(filtered)
        render_act_2(filtered)
        render_act_3(filtered)
        render_act_4(filtered)
        render_act_5(filtered)
    else:
        if selected_act == "Act 1: The Pressure Cooker":
            render_act_1(filtered)
        elif selected_act == "Act 2: Lifestyle Side Quests":
            render_act_2(filtered)
        elif selected_act == "Act 3: The Classroom Consequences":
            render_act_3(filtered)
        elif selected_act == "Act 4: Different Students, Similar Pattern":
            render_act_4(filtered)
        else:
            render_act_5(filtered)

    st.divider()
    run_scenario(filtered)

    st.divider()
    st.subheader("MVP Takeaway")
    st.info(
        "The story is consistent across all interactive views: higher stress and poorer sleep align with worse"
        " concentration, stronger assignment disruption, and weaker academic outcomes. Lifestyle habits"
        " appear to amplify or buffer that pathway."
    )


if __name__ == "__main__":
    main()
