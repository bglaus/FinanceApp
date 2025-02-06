import streamlit as st
from utils.config import COLUMN_MAPPING_CSV, COLUMN_NAMES, CATEGORY_MAPPING_CSV, DEFAULT_CATEGORY_MAPPING_CSV, DEFAULT_COLUMN_MAPPING_CSV
import utils.streamlit_util as streamlit_util
import pandas as pd
import os
import shutil

st.header("Einstellungen")

def init():
    streamlit_util.init()

@st.dialog("Zurücksetzen bestätigen")
def reset_data_dialog(mapping="Kategorie"):
    st.write(f"Soll das {mapping}-Mapping wirklich zurückgesetzt werden?")
    cols = st.columns(2)
    if cols[0].button("Ja", key="confirm_reset_data", use_container_width=True):
        if mapping == "Kolonnen":
            try:
                os.remove(COLUMN_MAPPING_CSV)
                shutil.copy(DEFAULT_COLUMN_MAPPING_CSV, COLUMN_MAPPING_CSV)
                st.rerun()
            except Exception as e:
                st.error("Fehler beim Zurücksetzen der Daten.")
                st.error(e)
            st.rerun()
        elif mapping == "Kategorie":
            try:
                os.remove(CATEGORY_MAPPING_CSV)
                shutil.copy(DEFAULT_CATEGORY_MAPPING_CSV, CATEGORY_MAPPING_CSV)   
                st.rerun()   
            except Exception as e:
                st.error("Fehler beim Zurücksetzen der Daten.")
                st.error(e)
    if cols[1].button("Nein", key="cancel_reset_data", type="primary", use_container_width=True):
        st.rerun()

@st.dialog("Kolonnen Mapping hochladen")
def upload_column_mapping_csv_dialog():
    st.write(f"Bitte lade die CSV Datei hoch, die für das Kolonnen Mapping verwendet werden sollte.")
    uploaded_file = st.file_uploader("Datei auswählen", type=["csv"])
    check_file = uploaded_file is not None
    cols = st.columns(2)
    if cols[0].button("Speichern", key="upload_file",  type="primary", disabled=not check_file, use_container_width=True):
        try:
            uploaded_df = pd.read_csv(uploaded_file, delimiter=";")
            os.remove(COLUMN_MAPPING_CSV)
            uploaded_df.to_csv(COLUMN_MAPPING_CSV, index=False, sep=";")
            st.rerun()
        except:
            st.error("Fehler beim Lesen der Datei. Bitte überprüfe das Format.")
            st.rerun()
    if cols[1].button("Abbrechen", key="cancel_upload_file", use_container_width=True):
        st.rerun()

@st.dialog("Kategorien Mapping hochladen")
def upload_category_mapping_csv_dialog():
    st.write(f"Bitte lade die CSV Datei hoch, die für das Kategorien Mapping verwendet werden sollte.")
    uploaded_file = st.file_uploader("Datei auswählen", type=["csv"])
    check_file = uploaded_file is not None
    cols = st.columns(2)
    if cols[0].button("Speichern", key="upload_file",  type="primary", disabled=not check_file, use_container_width=True):
        try:
            uploaded_df = pd.read_csv(uploaded_file, delimiter=";")
            os.remove(CATEGORY_MAPPING_CSV)
            uploaded_df.to_csv(CATEGORY_MAPPING_CSV, index=False, sep=";")
            st.rerun()
        except:
            st.error("Fehler beim Lesen der Datei. Bitte überprüfe das Format.")
            st.rerun()
    if cols[1].button("Abbrechen", key="cancel_upload_file", use_container_width=True):
        st.rerun()

def draw():
    # Kolonnen Mapping
    st.markdown(f"#### Kolonnen Mapping\n\nZuweisung der Kolonnen in den Kontoauszügen zu den Kolonnen in der verarbeiteten Datei. Folgende Kolonnen sind in der verarbeiteten Datei enthalten:")
    st.code(", ".join(COLUMN_NAMES))
    cols = st.columns(2)
    if cols[0].button("Datei hochladen", key="upload_column_mapping_dialog_button", use_container_width=True):
        upload_column_mapping_csv_dialog()
    if cols[1].button("Zurücksetzen", key="use_default_column_mapping", use_container_width=True):
        reset_data_dialog(mapping="Kolonnen")
    column_mapping_df = pd.read_csv(COLUMN_MAPPING_CSV, delimiter=";")
    column_mapping_df = st.data_editor(
        column_mapping_df, 
        use_container_width=True, 
        num_rows="dynamic"
    )
    missing_column = [col for col in set(column_mapping_df["to"]) if col not in COLUMN_NAMES and isinstance(col, str) and col != ""]
    if missing_column:
        st.warning("ACHTUNG missing columns:")
        st.text(missing_column)
        st.text([type(col) for col in missing_column])
        #st.warning("Die folgenden Kolonnen wurden zugewiesen, existieren aber nicht in der verarbeiteten Datei: " + ", ".join(missing_column))
    if st.button("Änderungen speichern", use_container_width=True, type="primary", key="save_column_mapping"):
        column_mapping_df.to_csv(COLUMN_MAPPING_CSV, index=False, sep=";")
        st.toast("Änderungen gespeichert.", icon="✅")

    # Kategorien Mapping
    st.divider()
    st.markdown(f"#### Kategorien Mapping\n\nZuweisung von (Unter-)Kategorie anhand der Beschreibung.")
    cols = st.columns(2)
    if cols[0].button("Datei hochladen", key="upload_category_mapping_dialog_button", use_container_width=True):
        upload_category_mapping_csv_dialog()
    if cols[1].button("Zurücksetzen", key="use_default_category_mapping", use_container_width=True):
        reset_data_dialog(mapping="Kategorie")
    st.session_state.update_categories = st.checkbox("Kategorisierung automatisch aktualisieren", value=True)

    category_mapping_df = pd.read_csv(CATEGORY_MAPPING_CSV, delimiter=";")
    category_mapping_df = category_mapping_df.sort_values(by=["Kategorie", "Unterkategorie"], ascending=[True, True])
    category_mapping_df = category_mapping_df.reset_index(drop=True)
    category_mapping_df = st.data_editor(
        category_mapping_df, 
        use_container_width=True, 
        num_rows="dynamic"
    )
    st.markdown("Besondere Kategorien:\n - `IGNORE`: Einträge mit dieser Kategorie werden ignoriert.\n - `Fixkosten`: Einträge werden besonders gelistet.")
    if st.button("Änderungen speichern", use_container_width=True, type="primary", key="save_category_mapping"):
        try:
            category_mapping_df.to_csv(CATEGORY_MAPPING_CSV, index=False, sep=";")
        except Exception as e:
            st.toast(f"Fehler beim Speichern der Daten: {e}", icon="❌")
        st.toast("Änderungen gespeichert.", icon="✅")

    # Danger Zone
    st.divider()
    st.markdown("#### Danger Zone")
    if st.button("Daten löschen", use_container_width=True, key="reset_data"):
        delete_data_dialog()
    st.write(f"streamlit version: {st.__version__}")

def delete_data():
    os.remove(COLUMN_MAPPING_CSV)
    os.remove(CATEGORY_MAPPING_CSV)
    st.session_state.update_categories = True

@st.dialog("Daten löschen")
def delete_data_dialog():
    st.write("Willst du wirklich alle Daten löschen?")
    cols = st.columns(2)
    if cols[0].button("Ja", key="confirm_delete_data", use_container_width=True):
        delete_data()
        st.rerun()
    if cols[1].button("Nein", key="cancel_delete_data", type="primary", use_container_width=True):
        st.rerun()

def main():
    init()
    draw()

if __name__ == "__main__":
    main()