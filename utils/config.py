import streamlit as st

BASE_PATH = '/mnt'          # defined in package.json
LOGGING = True
RESET = True

# CSV settings storing the data
COLUMN_NAMES = ["Datum", "Betrag", "Beschreibung", "Kategorie", "Unterkategorie"]
COLUMN_MAPPING_CSV = BASE_PATH + '/data/column_mapping.csv'          # maps column names from imported CSV to internal CSV
CATEGORY_MAPPING_CSV = BASE_PATH + '/data/category_mapping.csv'      # maps "Beschreibung" Text to categories and subcategories
DEFAULT_COLUMN_MAPPING_CSV = BASE_PATH + '/data/default_column_mapping.csv'
DEFAULT_CATEGORY_MAPPING_CSV = BASE_PATH + '/data/default_category_mapping.csv'
UNCATEGORIZED = "Uncategorized"
COLUMN_CONFIG = {
    "Datum": st.column_config.DateColumn(
        "Datum",
        format="DD.MM.YYYY",
        width="small",
    ),
    "Betrag": st.column_config.NumberColumn(
        "Betrag",
        format="%.2f CHF",
        width="small",
    ),
    "Beschreibung": st.column_config.TextColumn(
        "Beschreibung",
        width="medium",
    ),
    "Kategorie": st.column_config.TextColumn(
        "Kategorie",
        width="medium",
    ),
    "Unterkategorie": st.column_config.TextColumn(
        "Unterkategorie",
        width="medium",
    )
}

# Data Storage Settings
RAW_DATA_PATH = BASE_PATH + '/data/raw/'                             # path to store the raw data (CSV files as they are uploaded)
IMPORTED_DATA_PATH = BASE_PATH + '/data/imported/'                   # path to store the imported data (CSV files after import-processing)
YEARLY_DATA_PATH = BASE_PATH + '/data/imported/yearly/'              # path to store the yearly data (CSV files after yearly processing)