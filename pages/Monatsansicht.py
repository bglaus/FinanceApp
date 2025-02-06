import sys
sys.path.append("..")

from utils.config import IMPORTED_DATA_PATH
from utils.visualization_util import plotly_pie_chart, plotly_sunburst_chart, show_dataframe
from utils import file_util, streamlit_util

import streamlit as st
import pandas as pd
import os

def init():
    streamlit_util.init()

def daily_spending_chart(df: pd.DataFrame) -> None:
    # Bar Chart of daily spending
    st.markdown("### Tägliche Ausgaben")
    st.caption("Visualisierung der täglichen Ausgaben ohne Fixkosten.")
    date_range = pd.date_range(start=df['Datum'].min(), end=df['Datum'].max())
    daily_sums = {date: abs(df.loc[df["Kategorie"] != "Fixkosten"].loc[df['Datum'] == date].loc[df["Betrag"] < 0]['Betrag'].sum()) for date in date_range}
    st.bar_chart(daily_sums, x_label="Datum", y_label="CHF")

def spending_by_category_chart(df: pd.DataFrame) -> None:
    st.markdown("### Ausgaben nach Kategorie")
    st.caption("Visualisierung der Ausgaben nach Kategorie.")
    df = df[df["Betrag"] < 0]
    if st.toggle("Fixkosten ausblenden"):
        fig = plotly_pie_chart(df[df["Kategorie"] != "Fixkosten"], values="Betrag", names="Kategorie")
    else:
        fig = plotly_pie_chart(df, values="Betrag", names="Kategorie")
    st.plotly_chart(fig, use_container_width=True)

def sunburst_category_chart(df: pd.DataFrame) -> None:
    st.markdown("### Ausgaben nach Kategorie und Unterkategorie")
    st.caption("Visualisierung der Ausgaben nach Kategorie und Unterkategorie.")
    df = df[df["Betrag"] < 0]
    df["Betrag"] = df["Betrag"].abs()
    fig = plotly_sunburst_chart(df)
    st.plotly_chart(fig, use_container_width=True)

def single_category_chart(df: pd.DataFrame) -> None:
    st.markdown("### Details pro Kategorie")
    st.session_state.selected_category = st.selectbox("Kategorie", df["Kategorie"].unique())

    if st.session_state.selected_category is not None and st.session_state.selected_category != "":
        st.markdown(f"**Details für die Kategorie '{st.session_state.selected_category}'**")
        df = df.loc[df["Betrag"] < 0].loc[df["Kategorie"] == st.session_state.selected_category]
        fig = plotly_pie_chart(df, values="Betrag", names="Unterkategorie")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

def select_monthly_data() -> pd.DataFrame:
    # Load data
    df_names = [f[:-4] for f in os.listdir(IMPORTED_DATA_PATH) if f.endswith(".csv")]
    df_names = file_util.sort_by_month(df_names)
    index = df_names.index(st.session_state.selected_df) if st.session_state.selected_df in df_names else None
    st.session_state.selected_df = st.selectbox("Datensatz auswählen.", options=df_names, index=index)
    if not st.session_state.selected_df: 
        return None
    df_path = IMPORTED_DATA_PATH + st.session_state.selected_df + ".csv"
    file_util.load_df(df_path)
    df = st.session_state.df
    df = df[df["Kategorie"] != "IGNORE"]
    return df

def key_metrics(df: pd.DataFrame) -> None:
    total_in = lambda df : df[df["Betrag"] > 0]["Betrag"].sum()
    total_out = lambda df : df[df["Betrag"] < 0]["Betrag"].sum()
    fix_out = lambda df : df[(df["Kategorie"] == "Fixkosten") & (df["Betrag"] < 0)]["Betrag"].sum()
    var_out = lambda df : df[(df["Kategorie"] != "Fixkosten") & (df["Betrag"] < 0)]["Betrag"].sum()

    st.metric("Total", value=f"{total_in(df) + total_out(df):.2f} CHF")
    cols = st.columns(2)
    cols[0].metric("Einnahmen", value=f"{total_in(df):.2f} CHF")
    cols[1].metric("Ausgaben", value=f"{total_out(df):.2f} CHF")

    cols = st.columns(2)
    cols[0].metric("Fixkosten", value=f"{fix_out(df):.2f} CHF")
    cols[1].metric("Variable Kosten", value=f"{var_out(df):.2f} CHF")

def draw():
    st.header("Monatsdaten erkunden.")
    df = select_monthly_data()
    if df is None: return
    st.markdown(f"## {st.session_state.selected_df}")
    key_metrics(df)
    sunburst_category_chart(df)
    show_dataframe(df, sort_option=["Datum", "Betrag", "Kategorie"])
    st.divider()
    daily_spending_chart(df)
    spending_by_category_chart(df)
    single_category_chart(df)

def main():
    init()
    draw()

if __name__ == "__main__":
    main()