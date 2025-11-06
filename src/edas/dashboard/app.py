# src/edas/dashboard/app.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output

from edas.db.connection import get_engine
from edas.dashboard import queries as Q


def _now_brussels_range():
    now_utc = pd.Timestamp.utcnow()  # Already UTC-aware
    now_bxl = now_utc.tz_convert("Europe/Brussels")
    end = now_bxl.floor("H")
    start = end - pd.Timedelta(days=10)
    return start.to_pydatetime(), end.to_pydatetime()



COUNTRY_OPTIONS = [
    {"label": "France", "value": "FR"},
    {"label": "Germany", "value": "DE"},
]

engine_factory = get_engine

app = Dash(__name__, title="Energy Analytics Dashboard")
app.layout = html.Div(
    [
        html.H3("Energy Analytics Dashboard"),
        html.Div(
            [
                html.Label("Select Countries"),
                dcc.Dropdown(
                    id="country-select",
                    options=COUNTRY_OPTIONS,
                    value=["FR"],
                    multi=True,
                    style={"width": "380px"},
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Date Range"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=_now_brussels_range()[0],
                    end_date=_now_brussels_range()[1],
                    display_format="YYYY-MM-DD",
                ),
            ],
            style={"margin": "10px 0"},
        ),
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(label="KPIs & Time Series", value="tab-1"),
                dcc.Tab(label="Production Mix", value="tab-2"),
                dcc.Tab(label="Cross-Border Flows", value="tab-3"),
                dcc.Tab(label="Hourly Heatmap", value="tab-4"),
                dcc.Tab(label="Tables", value="tab-5"),
            ],
        ),
        html.Div(id="tab-content"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("country-select", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def render_tab(tab, countries, start_date, end_date):
    countries = countries or ["FR"]

    if tab == "tab-1":
        df = Q.consumption_vs_production(engine_factory, countries, start_date, end_date)
        k = Q.kpis(engine_factory, countries, start_date, end_date)

        kpi = html.Div(
            [
                html.H4("KPIs"),
                html.Div(f"Total Consumption: {k['total_consumption']:.2f} MW"),
                html.Div(f"Avg Daily Consumption: {k['avg_daily_consumption']:.2f} MW"),
                html.Div(f"Avg Weekly Consumption: {k['avg_weekly_consumption']:.2f} MW"),
                html.Div(f"Avg Monthly Consumption: {k['avg_monthly_consumption']:.2f} MW"),
                html.Div(f"Total Production: {k['total_production']:.2f} MW"),
                html.Div(f"Net Balance (Imports - Exports): {k['net_balance']:.2f} MW"),
            ],
            style={"marginBottom": "15px"},
        )

        if df.empty:
            ts = html.Div("No data in this range.")
        else:
            ts = dcc.Graph(
                figure=px.line(
                    df,
                    x="time_stamp",
                    y=["consumption_mw", "production_mw"],
                    labels={"value": "MW", "time_stamp": "Time"},
                    title="Consumption vs Production",
                )
            )

        return html.Div([kpi, ts])

    if tab == "tab-2":
        df = Q.production_mix(engine_factory, countries, start_date, end_date)
        if df.empty:
            return html.Div("No data in this range.")
        fig = px.area(
            df, x="time_stamp", y="production_mw", color="source_type", title="Production Mix"
        )
        return dcc.Graph(figure=fig)

    if tab == "tab-3":
        df = Q.crossborder_flows(engine_factory, countries, start_date, end_date)
        if df.empty:
            return html.Div("No flow data available.")
        agg = (
            df.groupby(["from_country_code", "to_country_code"], as_index=False)["flow_mw"]
            .sum()
            .sort_values("flow_mw", ascending=False)
        )
        fig = px.bar(
            agg,
            x="to_country_code",
            y="flow_mw",
            color="from_country_code",
            barmode="group",
            title="Net Flows by Country",
        )
        return dcc.Graph(figure=fig)

    if tab == "tab-4":
        df = Q.hourly_consumption(engine_factory, countries, start_date, end_date)
        if df.empty:
            return html.Div("No data in this range.")
        pivot = df.pivot_table(index="day", columns="hour", values="consumption_mw", aggfunc="mean")
        pivot = pivot.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        fig = px.imshow(
            pivot,
            aspect="auto",
            labels=dict(x="Hour", y="Day", color="Consumption (MW)"),
            title="Hourly Consumption Patterns",
        )
        return dcc.Graph(figure=fig)

    if tab == "tab-5":
        d1 = Q.daily_summary(engine_factory, countries, start_date, end_date)
        d2 = Q.flow_table(engine_factory, countries, start_date, end_date)
        tbl1 = dash_table.DataTable(
            data=d1.to_dict("records"),
            columns=[{"name": c, "id": c} for c in d1.columns],
            page_size=10,
            style_table={"overflowX": "auto"},
        )
        tbl2 = dash_table.DataTable(
            data=d2.to_dict("records"),
            columns=[{"name": c, "id": c} for c in d2.columns],
            page_size=10,
            style_table={"overflowX": "auto"},
        )
        return html.Div(
            [
                html.H4("Daily Consumption & Production"),
                tbl1,
                html.H4(style={"marginTop": "20px"}, children="Cross-Border Flows"),
                tbl2,
            ]
        )

    return html.Div("Unknown tab")


if __name__ == "__main__":
    app.run(debug=True)
