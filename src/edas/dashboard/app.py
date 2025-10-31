"""
Energy Analytics Dashboard
Run: poetry run python -m edas.dashboard.app
"""

import datetime as dt
import pandas as pd
import plotly.express as px

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table

from edas.dashboard import queries as Q

# ── App
app = dash.Dash(__name__)
app.title = "Energy Analytics Dashboard"
server = app.server  # if later you deploy behind gunicorn

# ── Defaults (last 30 days)
now_utc = pd.Timestamp.utcnow()  # already UTC-aware
start_default = (now_utc - pd.Timedelta(days=30)).tz_convert("Europe/Brussels").strftime("%Y-%m-%d")
end_default   = now_utc.tz_convert("Europe/Brussels").strftime("%Y-%m-%d")

app.layout = html.Div([
    html.H2("Energy Analytics Dashboard"),

    html.Div([
        html.Label("Select Countries"),
        dcc.Dropdown(
            id="country-select",
            options=[
                {"label": "France", "value": "FR"},
                {"label": "Germany", "value": "DE"},
            ],
            value=["FR"],
            multi=True,
            style={"minWidth": "280px"}
        ),
        html.Label("Date Range", style={"marginLeft": "24px"}),
        dcc.DatePickerRange(
            id="date-range",
            start_date=start_default,
            end_date=end_default,
            display_format="YYYY-MM-DD"
        ),
    ], style={"display": "flex", "alignItems": "center", "gap": "16px", "marginBottom": "10px"}),

    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="KPIs & Time Series", value="tab-1"),
        dcc.Tab(label="Production Mix", value="tab-2"),
        dcc.Tab(label="Cross-Border Flows", value="tab-3"),
        dcc.Tab(label="Hourly Heatmap", value="tab-4"),
        dcc.Tab(label="Tables", value="tab-5"),
    ]),
    html.Div(id="tab-content"),
], style={"padding": "16px"})


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("country-select", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def render_tab(tab, countries, start_date, end_date):
    if not countries:
        countries = ["FR"]

    # Normalize ISO strings; dash gives date-only → interpret as local midnight Brussels
    start_iso = pd.Timestamp(start_date).tz_localize("Europe/Brussels").tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")
    end_iso   = (pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))\
                    .tz_localize("Europe/Brussels").tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")

    if tab == "tab-1":
        df = Q.consumption_vs_production(countries, start_iso, end_iso)
        stats = Q.kpis(countries, start_iso, end_iso)

        kpi = html.Div([
            html.H4("KPIs"),
            html.P(f"Total Consumption: {stats['total_consumption']:.2f} MW"),
            html.P(f"Avg Daily Consumption: {stats['avg_daily_consumption']:.2f} MW"),
            html.P(f"Avg Weekly Consumption: {stats['avg_weekly_consumption']:.2f} MW"),
            html.P(f"Avg Monthly Consumption: {stats['avg_monthly_consumption']:.2f} MW"),
            html.P(f"Total Production: {stats['total_production']:.2f} MW"),
        ])

        fig = px.line(
            df, x="time_stamp", y=["consumption_mw", "production_mw"],
            labels={"value": "MW", "time_stamp": "Time"},
            title="Consumption vs. Production"
        )
        return html.Div([kpi, dcc.Graph(figure=fig)])

    elif tab == "tab-2":
        df = Q.production_mix(countries, start_iso, end_iso)
        if df.empty:
            return html.Div("No data")
        fig = px.area(df, x="time_stamp", y="production_mw", color="source_type",
                      title="Production Mix by Source")
        return dcc.Graph(figure=fig)

    elif tab == "tab-3":
        df = Q.crossborder_flows(countries, start_iso, end_iso)
        if df.empty:
            return html.Div("No flow data")
        agg = df.groupby(["from_country_code", "to_country_code"]).agg({"flow_mw": "sum"}).reset_index()
        fig = px.bar(agg, x="to_country_code", y="flow_mw", color="from_country_code",
                     barmode="group", title="Net Flows by Country")
        return dcc.Graph(figure=fig)

    elif tab == "tab-4":
        df = Q.hourly_consumption(countries, start_iso, end_iso)
        if df.empty:
            return html.Div("No data")
        pivot = df.pivot_table(index="day", columns="hour", values="consumption_mw", aggfunc="mean")
        pivot = pivot.reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        fig = px.imshow(pivot, labels=dict(x="Hour", y="Day", color="Consumption (MW)"),
                        aspect="auto", title="Hourly Consumption Patterns")
        return dcc.Graph(figure=fig)

    elif tab == "tab-5":
        daily = Q.daily_summary(countries, start_iso, end_iso)
        flows = Q.flow_table(countries, start_iso, end_iso)
        return html.Div([
            html.H4("Daily Consumption & Production"),
            dash_table.DataTable(
                data=daily.to_dict("records"),
                columns=[{"name": c, "id": c} for c in daily.columns],
                page_size=10,
            ),
            html.Hr(),
            html.H4("Cross-Border Flows"),
            dash_table.DataTable(
                data=flows.to_dict("records"),
                columns=[{"name": c, "id": c} for c in flows.columns],
                page_size=10,
            ),
        ])

    return html.Div("Select a tab.")


if __name__ == "__main__":
    # Dash default: http://127.0.0.1:8050
    app.run(debug=True)

