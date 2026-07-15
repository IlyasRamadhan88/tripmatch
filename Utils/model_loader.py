import os
import pandas as pd
import streamlit as st
import joblib

# Path file model & preprocessor hasil training (dari notebook), disimpan via joblib.dump()
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Model", "model_kmeans_k4.pkl"))
PREPROCESSOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Model", "preprocessor_wisata.pkl"))

# Definisi mapping untuk Budget dan Durasi (sesuai ordinal mapping di notebook)
BUDGET_OPTIONS = [
    'Kurang dari Rp50.000',
    'Rp50.000–Rp150.000',
    'Rp150.000–Rp300.000',
    'Lebih dari Rp300.000'
]

DURASI_OPTIONS = [
    '1 hari (tanpa menginap)',
    '2 hari/Menginap',
    'Lebih dari 2 hari'
]

TRANSPORT_OPTIONS_MAP = {
    'Motor Pribadi': 'Motor',
    'Mobil Pribadi': 'Mobil',
    'Transportasi Umum Konvensional': 'Umum'
}

SUBPREF_MAP = {
    "Theme Park/Wahana": "theme park/wahana",
    "Lifestyle dan Shopping": "lifestyle dan shopping",
}

# Profil deskripsi dari masing-masing Cluster
CLUSTER_PROFILES = {
    0: {
        "name": "Practical Explorer",
        "description": "Anda termasuk tipe Practical Explorer. Kelompok ini umumnya menyukai perjalanan yang sederhana dan mudah direncanakan, sehingga destinasi yang mudah dijangkau dan tetap memberikan pengalaman wisata yang menarik cenderung lebih sesuai.",
        "dominant_pref": "Wisata Alam, Wisata Edukasi, Wisata Kota/Urban",
        "avg_budget": "Rp150.000 – Rp300.000",
        "avg_duration": "1 hari (tanpa menginap)",
        "common_transport": "Transportasi Umum, Campuran Motor & Mobil Pribadi",
        "color": "#FF9F43" # Orange
    },
    1: {
        "name": "Leisure Explorer",
        "description": "Anda termasuk tipe Leisure Explorer. Kelompok ini umumnya menikmati perjalanan dengan waktu yang lebih leluasa sehingga destinasi yang menawarkan pengalaman wisata secara lebih menyeluruh dan nyaman cenderung lebih sesuai.",
        "dominant_pref": "Wisata Alam, Wisata Hiburan, Wisata Hiburan",
        "avg_budget": "Kurang dari Rp50.000 s.d Rp150.000",
        "avg_duration": "1 hari (tanpa menginap)",
        "common_transport": "Sepeda Motor Pribadi, Transportasi Umum",
        "color": "#28C76F" # Green
    },
    2: {
        "name": "Versatile Explorer",
        "description":"Anda termasuk tipe Versatile Explorer. Kelompok ini umumnya memiliki keleluasaan dalam merencanakan perjalanan dan tidak terpaku pada satu cara bepergian, sehingga destinasi yang menawarkan berbagai alternatif aktivitas maupun akses perjalanan cenderung lebih sesuai.",
        "dominant_pref": "Wisata Alam, Wisata Kuliner, Wisata Kota/Urban",
        "avg_budget": "Lebih dari Rp300.000",
        "avg_duration": "2 hari/Menginap s.d Lebih dari 2 hari",
        "common_transport": "Mobil Pribadi",
        "color": "#EA5455" # Red/Coral
    },
    3: {
        "name": "Transit Explorer",
        "description": "Anda termasuk tipe Transit Explorer. Kelompok ini umumnya terbiasa memanfaatkan transportasi umum dalam melakukan perjalanan sehingga destinasi yang mudah diakses melalui jaringan transportasi publik cenderung lebih sesuai.",
        "dominant_pref": "Wisata Alam, Wisata Kuliner, Wisata Budaya dan Sejarah",
        "avg_budget": "Rp50.000 – Rp150.000",
        "avg_duration": "1 hari (tanpa menginap)",
        "common_transport": "Sepeda Motor Pribadi",
        "color": "#00CFE8" # Cyan
    }
}

@st.cache_resource(show_spinner=False)
def load_model_and_preprocessor():
    """
    Meload model K-Means dan preprocessor (ColumnTransformer) yang SUDAH DILATIH
    sebelumnya di notebook, langsung dari file .pkl hasil joblib.dump().
    TIDAK melatih ulang model saat aplikasi dijalankan (sesuai metodologi asli).

    Catatan penting: kedua file ini disimpan menggunakan `joblib.dump()`
    (bukan `pickle.dump()` biasa), jadi WAJIB dibaca dengan `joblib.load()`.
    Jika dibaca dengan `pickle.load()`, akan muncul error
    'UnpicklingError: invalid load key' karena joblib menyimpan array numpy
    besar (seperti cluster_centers_) lewat struktur internal NumpyArrayWrapper
    yang tidak dikenali oleh pickle standar.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"File model K-Means tidak ditemukan di: {MODEL_PATH}")
    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError(f"File preprocessor tidak ditemukan di: {PREPROCESSOR_PATH}")

    model_kmeans = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    return preprocessor, model_kmeans

def preprocess_and_predict(pref, subpref, budget_str, transport_list, durasi_str):
    """
    Melakukan preprocessing dari input raw form pengguna dan memprediksi Cluster ID.
    `transport_list` adalah LIST berisi 0, 1, atau lebih label transportasi yang
    dipilih user (hasil st.multiselect), sesuai skema multi-hot model terbaru
    (kolom independen: Motor, Mobil, Umum).
    """
    # 1. Load model & preprocessor (dari file .pkl, bukan training ulang)
    preprocessor, model_kmeans = load_model_and_preprocessor()
    
    # 2. Transformasi ke format training
    pref_model = f"Wisata {pref}"
    subpref_model = SUBPREF_MAP.get(subpref, subpref)
    
    try:
        budget_ord = BUDGET_OPTIONS.index(budget_str)
    except ValueError:
        budget_ord = 1

    try:
        durasi_ord = DURASI_OPTIONS.index(durasi_str)
    except ValueError:
        durasi_ord = 0

    # Skema multi-hot: setiap moda transportasi jadi fitur biner independen
    transport_list = transport_list or []
    motor = 1 if 'Motor Pribadi' in transport_list else 0
    mobil = 1 if 'Mobil Pribadi' in transport_list else 0
    umum = 1 if 'Transportasi Umum Konvensional' in transport_list else 0

    # 3. Membuat DataFrame satu baris untuk prediksi
    user_data = pd.DataFrame([{
        'Preferensi Wisata': pref_model,
        'Subpreferensi_Utama': subpref_model,
        'Motor': motor,
        'Mobil': mobil,
        'Umum': umum,
        'Budget_Ordinal': budget_ord,
        'Durasi_Ordinal': durasi_ord
    }])

    # 4. Preprocessing dengan preprocessor yang sudah di-fit
    user_scaled = preprocessor.transform(user_data)
    
    # 5. Prediksi Cluster
    cluster_id = int(model_kmeans.predict(user_scaled)[0])
    
    return cluster_id, CLUSTER_PROFILES[cluster_id]