import os
import pandas as pd
import streamlit as st

# Path to Destination_Dataset.xlsx relative to this utility file
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data", "Destination_Dataset.xlsx"))

@st.cache_data
def load_destinations():
    """
    Memuat dataset destinasi dari file Excel dan mengembalikan DataFrame yang bersih.
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset destinasi tidak ditemukan di: {DATA_PATH}")
    
    # Membaca data excel
    df = pd.read_excel(DATA_PATH)
    
    # Membersihkan nama kolom dari spasi berlebih
    df.columns = [col.strip() for col in df.columns]
    
    return df

def get_preferensi_list(df):
    """
    Mengembalikan daftar kategori Preferensi unik.
    """
    return sorted(df['Preferensi'].unique().tolist())

def get_subpreferensi_by_preferensi(df, preferensi):
    """
    Mengembalikan daftar Subpreferensi unik berdasarkan kategori Preferensi yang dipilih.
    """
    filtered_df = df[df['Preferensi'] == preferensi]
    return sorted(filtered_df['Subpreferensi'].unique().tolist())

def filter_destinations(df, preferensi, subpreferensi=None):
    """
    Menyaring destinasi berdasarkan Preferensi dan Subpreferensi yang dipilih.
    Jika subpreferensi bernilai None atau "Pilih Subpreferensi...", saring berdasarkan Preferensi saja.
    """
    if subpreferensi is None or subpreferensi == "Pilih Subpreferensi...":
        return df[df['Preferensi'] == preferensi]
    return df[(df['Preferensi'] == preferensi) & (df['Subpreferensi'] == subpreferensi)]
