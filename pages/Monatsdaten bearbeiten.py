import sys
sys.path.append("..")

import streamlit as st
from utils.config import IMPORTED_DATA_PATH, COLUMN_CONFIG
import utils.streamlit_util as streamlit_util
import utils.file_util as file_util
import os
import json

st.header("Monatsdaten bearbeiten")

def init():
    streamlit_util.init()

def draw():
    df_names = [f[:-4] for f in os.listdir(IMPORTED_DATA_PATH) if f.endswith(".csv")]
    index = df_names.index(st.session_state.selected_df) if st.session_state.selected_df in df_names else None
    st.session_state.selected_df = st.selectbox("Datensatz auswählen.", options=df_names, index=index)
    if not st.session_state.selected_df: return
    df_path = IMPORTED_DATA_PATH + st.session_state.selected_df + ".csv"
    file_util.load_df(df_path)

    json_path = IMPORTED_DATA_PATH + st.session_state.selected_df + ".json"
    with open(json_path, "r") as f:
        info_dict = json.load(f)
        if 'locked' not in info_dict: info_dict['locked'] = False

    # Editor
    df = st.session_state.df
    sortierung = st.selectbox("Sortieren nach", ["Datum", "Betrag", "Kategorie"])
    if sortierung is not None and sortierung != "":
        df = df.sort_values(by=sortierung)
        df = df.reset_index(drop=True)

    if info_dict['locked']:
        st.info("Bearbeitung gesperrt.")
        st.dataframe(df, column_config=COLUMN_CONFIG, use_container_width=True)
    else:
        df = st.data_editor(
            df, 
            column_config=COLUMN_CONFIG,
            use_container_width=True, 
            num_rows="dynamic",
        )

    cols = st.columns(2)
    lock_label = "Daten sperren" if not st.session_state.locked else "Daten entsperren"
    if cols[0].button(lock_label, use_container_width=True, type="secondary", key="lock_df_button"):
        st.session_state.locked = not st.session_state.locked
        st.session_state.update_categories = not st.session_state.locked
        json_path = IMPORTED_DATA_PATH + st.session_state.selected_df + ".json"
        info_dict["locked"] = st.session_state.locked
        with open(json_path, "w") as f:
            json.dump(info_dict, f, indent=4)
        toast_msg = "Daten gesperrt." if st.session_state.locked else "Daten entsperrt."
        st.toast(toast_msg, icon="🔒" if st.session_state.locked else "🔓")
        st.rerun()
    
    if cols[1].button("Änderungen speichern", use_container_width=True, type="primary", key="save_df_button"):
        df_path = IMPORTED_DATA_PATH + st.session_state.selected_df + ".csv"
        st.session_state.df = df
        df.to_csv(df_path, index=False, encoding='iso-8859-1', sep=';')
        file_util.load_df(df_path)
        st.session_state.update_yearly = True
        st.toast("Änderungen gespeichert.", icon="✅")

def main():
    init()
    draw()

if __name__ == "__main__":
    main()