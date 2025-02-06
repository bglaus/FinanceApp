import sys
sys.path.append("..")

import streamlit as st
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime

import utils.streamlit_util as streamlit_util
from utils.config import RAW_DATA_PATH, IMPORTED_DATA_PATH, COLUMN_NAMES
from utils import file_util

def init():
    streamlit_util.init()

def map_foreign_currency(row):
    if "Original currency" in row:
        original_currency = row["Original currency"]
        if type(original_currency) == float and np.isnan(original_currency):
            return row["Kategorie"]
        elif original_currency not in ["CHF", ""]:
            return "Reisen"
    return row["Kategorie"]

def import_data(uploaded_files, out_name):
    file_names = [f"{out_name}_{uploaded_file.name}" for uploaded_file in uploaded_files]
    file_paths = [os.path.join(RAW_DATA_PATH, file_name) for file_name in file_names]

    # write csv file to disk
    for i, uploaded_file in enumerate(uploaded_files):
        with open(file_paths[i], "wb") as f: f.write(uploaded_file.read())

    # process csv files
    out_df = pd.DataFrame(columns=COLUMN_NAMES)
    column_mapping = file_util.load_column_mapping()
    for file_path in file_paths:
        df: pd.DataFrame = pd.read_csv(file_path, delimiter=";", encoding='iso-8859-1')
        df = df.rename(columns=column_mapping)
        for col in COLUMN_NAMES:
            if col not in df.columns:
                df[col] = None
        df["Kategorie"] = df.apply(map_foreign_currency, axis=1)
        df = df[COLUMN_NAMES]
        if 'Datum' in df.columns: df['Datum'] = pd.to_datetime(df['Datum'], format='mixed')
        out_df = pd.concat([out_df, df], ignore_index=True)
    
    out_df = file_util.apply_category_mapping(out_df)
    out_path = IMPORTED_DATA_PATH + out_name
    out_df.to_csv(f"{out_path}.csv", index=False, encoding='iso-8859-1', sep=';')

    min_date = out_df['Datum'].min().strftime("%d.%m.%Y")
    max_date = out_df['Datum'].max().strftime("%d.%m.%Y")

    info_dict: dict = {
        "name": out_name,
        "output_path": out_path,
        "input_files": file_paths,
        "import_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timerange": f"{min_date} - {max_date}",
        "n_entries": len(out_df),
    }
    with open(f"{out_path}.json", "w") as f: 
        json.dump(info_dict, f, indent=4)
    st.toast("Daten erfolgreich importiert.", icon="✅")
    st.session_state.update_yearly = True
    return
    

def draw():
    # show import data

    st.header("Daten importieren.")
    st.markdown("#### Import \nLade hier deine Kontoauszüge eines Monats hoch.\n")
    out_name: str = st.text_input("Name", value=file_util.default_file_name())
    if "." in out_name: out_name = out_name.split(".")[0]
    overwrite: bool = st.checkbox("Überschreiben erlauben.", value=False)
    uploaded_files = st.file_uploader("Kontoauszug hochladen", accept_multiple_files=True, type=["csv"])

    if st.button("verarbeiten", type="primary", use_container_width=True):
        overlap = (f"{out_name}.csv" in os.listdir(IMPORTED_DATA_PATH))
        if overlap and not overwrite:
            st.error(f"'{out_name}' existiert bereits. Um '{out_name}' zu überschreiben, aktiviere [Überschreiben erlauben].")
            return
        import_data(uploaded_files, out_name)
        
    # show imported data

    st.divider()
    configs = [f for f in os.listdir(IMPORTED_DATA_PATH) if f.endswith(".json")]
    if len(configs) > 0:
        st.markdown("#### Hochgeladene Daten")
        n_cols = 3 # TODO make dynamic, depending on screen width
        n_rows = len(configs) // n_cols + 1
        for i in range(n_rows):
            cols = st.columns(n_cols)
            for j in range(n_cols):
                idx = i * n_cols + j
                if idx >= len(configs): break
                with open(os.path.join(IMPORTED_DATA_PATH, configs[idx]), "r") as f:
                    config = json.load(f)
                    name = f"##### {config['name']}"
                    if 'locked' in config and config['locked']: name += " 🔒"
                    cols[j].markdown(name)
                    cols[j].text(f"{config['timerange']}\n{config['n_entries']} Einträge")
                    if cols[j].button("Bearbeiten", use_container_width=True, key=f"edit_{i}_{j}"):
                        file_util.load_df(f"{config['output_path']}.csv")
                        st.switch_page("pages/Monatsdaten bearbeiten.py")
                    if cols[j].button("Anschauen", use_container_width=True, type="primary", key=f"open_{i}_{j}"):
                        file_util.load_df(f"{config['output_path']}.csv")
                        st.switch_page("pages/Monatsansicht.py")

                
def main():
    init()
    draw()

if __name__ == "__main__":
    main()