import sys
sys.path.append("..")

from datetime import datetime
import pandas as pd
import streamlit as st

from utils.config import COLUMN_MAPPING_CSV, CATEGORY_MAPPING_CSV, UNCATEGORIZED

MONTHS = ['januar', 'februar', 'märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember']

def load_df(file_path, set_df_session_state=True):
    df = pd.read_csv(file_path, delimiter=";", encoding='iso-8859-1')
    if 'Datum' in df.columns: 
        df['Datum'] = pd.to_datetime(df['Datum'], format='mixed')
    if st.session_state.update_categories:
        df = apply_category_mapping(df)
    if set_df_session_state:
        st.session_state.df = df
        st.session_state.selected_df = file_path.split("/")[-1][:-4]
    return df

def default_file_name() -> str:
    "Default file name is month + year: 'januar_2024'"
    current_month = datetime.now().month -1 or 12
    return f"{MONTHS[current_month-1]}_{datetime.now().year}"

def sort_by_month(df_names) -> list:
    return sorted(df_names, key=month_index)

def month_index(df_name) -> int:
    for i, month in enumerate(MONTHS):
        if df_name.startswith(month):       # TODO fix
            return i
    return None

def load_column_mapping() -> dict:
    "Returns a dictionary with the mapping of column names in the input file to the column names in the processed file."
    column_mapping_df = pd.read_csv(COLUMN_MAPPING_CSV, delimiter=";")
    return column_mapping_df.set_index('from')['to'].to_dict()

def apply_category_mapping(df: pd.DataFrame) -> pd.DataFrame:
    "Applies the category mapping to the dataframe"
    category_mapping_df = pd.read_csv(CATEGORY_MAPPING_CSV, delimiter=";")
    def process_row(row, return_subcategory=False):
        for _, mapping in category_mapping_df.iterrows():
            check = lambda a, b: str(a).lower() in str(b).lower()
            if check(mapping["Beschreibung"], row["Beschreibung"]):
                return mapping["Unterkategorie"] if return_subcategory else mapping["Kategorie"]
        return row["Unterkategorie"] if return_subcategory else row["Kategorie"]
    df['Kategorie'] = df.apply(process_row, args=[False], axis=1)
    df['Unterkategorie'] = df.apply(process_row, args=[True], axis=1)

    for col in ['Kategorie', 'Unterkategorie']:
        df[col] = df[col].fillna(UNCATEGORIZED)
        df[col] = df[col].replace('', UNCATEGORIZED)
    return df