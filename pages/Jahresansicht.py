import sys
sys.path.append("..")

import streamlit as st
import os
import pandas as pd

from utils import streamlit_util, visualization_util, file_util
from utils.config import IMPORTED_DATA_PATH, YEARLY_DATA_PATH, LOGGING

st.header("Jahresansicht")

def init():
    streamlit_util.init()

def update():
    "Creates the yearly views of all the imported data."
    if not st.session_state.update_yearly: 
        if LOGGING: print("Jahresansicht: No update needed.")
        return

    # remove old data
    old_files = [f for f in os.listdir(YEARLY_DATA_PATH) if f.endswith(".csv")]
    for f in old_files:
        os.remove(os.path.join(YEARLY_DATA_PATH, f))
    
    # process all files
    all_csvs = [f for f in os.listdir(IMPORTED_DATA_PATH) if f.endswith(".csv")]
    if LOGGING: print("Jahresansicht: Found", len(all_csvs), "files")
    for csv in all_csvs:
        file_path = os.path.join(IMPORTED_DATA_PATH, csv)
        if LOGGING: print("Jahresansicht: Processing file", file_path) 
        process_file(file_path)
    if LOGGING: print("Jahresansicht: Done processing files.")
    st.session_state.update_yearly = False

def process_file(file_path):
    "Processes a single file and inserts it into the yearly views."
    # read file into one dataframe for each year
    full_df = file_util.load_df(file_path, set_df_session_state=False)
    min_year = full_df['Datum'].min().year
    max_year = full_df['Datum'].max().year
    for year in range(min_year, max_year+1):
        yearly_df = full_df.loc[full_df['Datum'].dt.year == year]
        if LOGGING: print(f"\tFound {len(yearly_df)} entries for year {year}")
        process_df(yearly_df, year)


def process_df(df, year):
    "Processes a single dataframe and inserts it into the yearly views."
    file_name = f"{year}.csv"
    file_path = os.path.join(YEARLY_DATA_PATH, file_name)
    if file_name in os.listdir(YEARLY_DATA_PATH):
        yearly_df = file_util.load_df(file_path, set_df_session_state=False)
    else:
        yearly_df = pd.DataFrame(columns=df.columns)
    if not df.empty:
        yearly_df = pd.concat([yearly_df, df])
    yearly_df.to_csv(file_path, index=False, encoding='iso-8859-1', sep=';')

# draw ui
def select_yearly_data():
    st.session_state.selected_df = st.selectbox("Jahr", [f for f in os.listdir(YEARLY_DATA_PATH) if f.endswith(".csv")])
    if not st.session_state.selected_df:
        return None
    df_path = os.path.join(YEARLY_DATA_PATH, st.session_state.selected_df)
    df = file_util.load_df(df_path)
    df = df[df["Kategorie"] != "IGNORE"]
    return df

    

def draw():
    df = select_yearly_data()
    if df is None: return

    # Monatsdurchschnitt
    monthly_avg(df)

    # Durchschnittliche Monatsausgaben pro Kategorie
    st.markdown("### Monatsdurchschnitt nach Kategorie")
    cagetory_chart_df = df.loc[df["Betrag"] < 0]
    num_months = len(cagetory_chart_df["Datum"].dt.to_period("M").unique())
    cagetory_chart_df.loc[:, "Betrag"] = cagetory_chart_df["Betrag"].abs() / num_months
    if st.checkbox("Fixkosten ausblenden"):
        cagetory_chart_df = cagetory_chart_df.loc[cagetory_chart_df["Kategorie"] != "Fixkosten"]
    
    fig = visualization_util.plotly_sunburst_chart(cagetory_chart_df, values="Betrag", path=["Kategorie", "Unterkategorie"])
    st.plotly_chart(fig, use_container_width=True)

    # Details pro Kategorie
    st.session_state.selected_category = st.selectbox("Kategorie", df["Kategorie"].unique())
    if st.session_state.selected_category is not None and st.session_state.selected_category != "":
        st.markdown(f"**Details für die Kategorie '{st.session_state.selected_category}'**")
        subcategory_chart_df = df.loc[df["Betrag"] < 0].loc[df["Kategorie"] == st.session_state.selected_category]
        subcategory_chart_df.loc[:, "Betrag"] = subcategory_chart_df["Betrag"].abs() / num_months
        fig = visualization_util.plotly_pie_chart(subcategory_chart_df, values="Betrag", names="Unterkategorie")
        st.plotly_chart(fig, use_container_width=True)
        subcategory_chart_df.loc[:, "Betrag"] = subcategory_chart_df["Betrag"] * num_months
        visualization_util.show_dataframe(subcategory_chart_df, sort_option=["Datum", "Betrag", "Unterkategorie"])


def monthly_avg(df):
    saved = df.loc[df["Betrag"] > 0]["Betrag"].sum() + df.loc[df["Betrag"] < 0]["Betrag"].sum()
    avg_saved = saved / len(df["Datum"].dt.to_period("M").unique())

    result_df = df.loc[df["Betrag"] < 0].copy()
    result_df['Betrag'] = result_df['Betrag'].abs()
    result_df["Month"] = result_df["Datum"].dt.to_period("M").astype(str)
    fixkosten_sum = result_df[result_df["Kategorie"] == "Fixkosten"].groupby("Month")["Betrag"].sum().reset_index(name="Fixkosten")
    non_fixkosten_sum = result_df[result_df["Kategorie"] != "Fixkosten"].groupby("Month")["Betrag"].sum().reset_index(name="Variable Kosten")
    total_sum = result_df.groupby("Month")["Betrag"].sum().reset_index(name="Total Sum")

    result = pd.merge(fixkosten_sum, non_fixkosten_sum, on="Month", how="outer")
    result = pd.merge(result, total_sum, on="Month", how="outer")

    cols = st.columns(3)

    cols[0].metric("Durchnittliche Fixkosten", value=f"{fixkosten_sum['Fixkosten'].mean():.2f} CHF")
    cols[1].metric("Durchnittliche Variable Kosten", value=f"{non_fixkosten_sum['Variable Kosten'].mean():.2f} CHF")
    cols[2].metric("Durchnittliches Erspartes", value=f"+{avg_saved:.2f} CHF")

    st.bar_chart(result, x="Month", y=["Variable Kosten", "Fixkosten"], use_container_width=True)


def main():
    init()
    with st.spinner("Daten werden geladen..."):
        update()
    draw()

if __name__ == "__main__":
    main()