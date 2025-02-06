import streamlit as st
import os
from utils.config import COLUMN_MAPPING_CSV, CATEGORY_MAPPING_CSV, RAW_DATA_PATH, IMPORTED_DATA_PATH, YEARLY_DATA_PATH, RESET, DEFAULT_COLUMN_MAPPING_CSV, DEFAULT_CATEGORY_MAPPING_CSV
import shutil
import pandas as pd

def init():
    if 'update_categories' not in st.session_state: st.session_state.update_categories = True
    if 'df' not in st.session_state: st.session_state.df = None
    if 'locked' not in st.session_state: st.session_state.locked = False
    if 'selected_df' not in st.session_state: st.session_state.selected_df = None
    if 'select_df_widget' not in st.session_state: st.session_state.select_df_widget = None
    if 'selected_category' not in st.session_state: st.session_state.selected_category = None
    if 'update_yearly' not in st.session_state: st.session_state.update_yearly = True
    if 'language_model' not in st.session_state: st.session_state.language_model = None
    if 'chat_messages' not in st.session_state: st.session_state.chat_messages = []
    print("Session state initialized")

    if RESET:
        if os.path.exists(COLUMN_MAPPING_CSV): os.remove(COLUMN_MAPPING_CSV)
        if os.path.exists(CATEGORY_MAPPING_CSV): os.remove(CATEGORY_MAPPING_CSV)

    # if not os.path.exists(COLUMN_MAPPING_CSV):
    if not check_df_exists(COLUMN_MAPPING_CSV):
        print("Loading default column mapping")
        print("os.path.exists(COLUMN_MAPPING_CSV): " + str(os.path.exists(COLUMN_MAPPING_CSV)))
        shutil.copy(DEFAULT_COLUMN_MAPPING_CSV, COLUMN_MAPPING_CSV)
    # if not os.path.exists(CATEGORY_MAPPING_CSV):
    if not check_df_exists(CATEGORY_MAPPING_CSV):
        print("Loading default category mapping")
        print("os.path.exists(COLUMN_MAPPING_CSV): " + str(os.path.exists(COLUMN_MAPPING_CSV)))
        shutil.copy(DEFAULT_CATEGORY_MAPPING_CSV, CATEGORY_MAPPING_CSV)
    if not os.path.exists(RAW_DATA_PATH):
        os.makedirs(RAW_DATA_PATH)
    if not os.path.exists(IMPORTED_DATA_PATH):
        os.makedirs(IMPORTED_DATA_PATH)
    if not os.path.exists(YEARLY_DATA_PATH):
        os.makedirs(YEARLY_DATA_PATH)
    print("Paths initialized")

def check_df_exists(path):
    try:
        df = pd.read_csv(path, delimiter=";")
    except Exception as e:
        print("Error reading file: " + str(e))
        return False
    return not df.empty
    