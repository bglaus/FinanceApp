import sys
sys.path.append("..")

import streamlit as st
from utils.config import COLUMN_CONFIG

import plotly.express as px
import plotly.graph_objects as go

text_color = "#D3D4D8" # "#31333F" in bright mode, "#D3D4D8" in dark mode

def plotly_sunburst_chart(df, values="Betrag", path=["Kategorie", "Unterkategorie"]):
    df = df[[*path, values]].copy()
    data = df.groupby(path).sum().reset_index()
    fig = px.sunburst(
        data,
        path=path,
        values=values,
        color=values,
        title="Sunburst Chart",
        hover_data={values: True},
        color_continuous_scale="agsunset",
    )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>%{value:.2f} CHF'
    )
    fig.update_layout(
        height=600,
        margin=dict(t=40, b=40, l=40, r=40),
    )
    return fig

def plotly_pie_chart(df, values="Betrag", names="Kategorie"):
    df = df[[values, names]].copy()
    data = df.groupby(names).sum().reset_index()
    fig = go.Figure(
        data=[
            go.Pie(
                labels=data[names],
                values=data[values].abs(),
                textinfo='label+value',
                texttemplate='%{label}: %{value:.2f} CHF',
                hoverinfo='label+percent',
                marker=dict(
                    line=dict(color='white', width=1)
                )
            )
        ]
    )
    fig.update_layout(
        title="Pie Chart",
        title_x=0.5,
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
    )
    return fig


def show_dataframe(df, sort_option=["Datum", "Betrag", "Kategorie"]):
    invalid_options = [col for col in sort_option if col not in df.columns]
    if invalid_options: 
        print("Invalid sort options: ", invalid_options)
        sort_option = [col for col in sort_option if col in df.columns]     # make sure sort_options overlap with columns in df
    sortierung = st.selectbox("Sortieren nach",sort_option)
    if sortierung is not None and sortierung in sort_option:
        df = df.sort_values(by=sortierung)
        df = df.reset_index(drop=True)
    st.dataframe(df, column_config=COLUMN_CONFIG, use_container_width=True)

    