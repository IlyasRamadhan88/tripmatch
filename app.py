import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import sys
import base64

# Menambahkan working directory ke path agar import Utils bekerja
sys.path.append(os.path.dirname(__file__))

from Utils.data_loader import (
    load_destinations,
    get_preferensi_list,
    get_subpreferensi_by_preferensi,
    filter_destinations
)
from Utils.model_loader import (
    preprocess_and_predict,
    BUDGET_OPTIONS,
    DURASI_OPTIONS,
    TRANSPORT_OPTIONS_MAP
)

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Sistem Rekomendasi Destinasi Wisata",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Custom Google Fonts dan Premium CSS (Dark Theme, Glassmorphism, Micro-Animations)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Mengubah font utama aplikasi */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
        color: #E2E8F0;
    }
    
    /* Latar belakang dasar aplikasi — selalu aktif sebagai fallback */
    html, body {
        background: radial-gradient(circle at 10% 20%, rgba(20, 24, 38, 1) 0%, rgba(11, 14, 23, 1) 90%) !important;
    }

    /* .stApp transparan agar gambar hero di body::before bisa terlihat */
    .stApp {
        background: transparent !important;
    }
    
    /* Header & Title - Golden Peak */
    .app-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD54F 0%, #FF7043 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.6)); /* Shadow untuk memisahkan dari background */
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        font-weight: 400; /* Sedikit ditebalkan dari 300 agar lebih terbaca */
        color: #FFF3E0;
        text-align: center;
        margin-bottom: 2.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8); /* Tambahan shadow agar terbaca di atas gambar */
    }

    /* Section Title */
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #FF9800;
        margin-bottom: 15px;
        border-left: 4px solid #FF5722;
        padding-left: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }

    /* Custom Label */
    .custom-label {
        font-size: 0.95rem;
        font-weight: 400;
        color: #FAFAFA; /* Putih bersih untuk keterbacaan instruksi */
        margin-bottom: 8px;
        display: block;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
  
    
    /* Glassmorphism Card Wrapper */
    .glass-card {
        background: rgba(22, 28, 45, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 207, 232, 0.3);
    }
    

    
    /* Destination Cards */
    .dest-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        margin-bottom: 16px;
        height: 100%;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
    }
    .dest-card:hover {
        background: rgba(30, 41, 59, 0.9);
        border-color: rgba(26, 140, 255, 0.4);
        transform: scale(1.01);
    }
    /* Container gambar destinasi, rasio dikonsistenkan 4:3 (gambar boleh terpotong via object-fit: cover) */
    .dest-card-image {
        width: 100%;
        aspect-ratio: 4 / 3;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.04);
        flex-shrink: 0;
    }
    .dest-card-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .dest-card-body {
        padding: 20px;
    }
    .dest-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .dest-meta {
        font-size: 0.85rem;
        color: #FF9800;
        font-weight: 500;
        margin-bottom: 12px;
    }
    .dest-desc {
        font-size: 0.9rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    
    /* Badge styling */
    .dest-badge {
        display: inline-block;
        background: rgba(148, 163, 184, 0.1);
        color: #CBD5E1;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Success Badge for matching values */
    .badge-match {
        background: rgba(40, 199, 111, 0.15) !important;
        color: #28C76F !important;
        border-color: rgba(40, 199, 111, 0.3) !important;
    }
    
    /* Cluster Result Card styling */
    .cluster-card {
        background: rgba(22, 28, 45, 0.75);
        border-radius: 20px;
        padding: 30px;
        margin-top: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .cluster-glow {
        position: absolute;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.35;
        top: -50px;
        right: -50px;
    }
</style>
""", unsafe_allow_html=True)

# Brand Logo "TripMatch" di pojok kiri atas (Tugas 4)

# 1. Fungsi pembaca gambar (bisa diletakkan di bagian atas file app.py Anda)
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 2. Mencari path logo.png secara otomatis
# Asumsi: folder Assets berada sejajar dengan file app.py
logo_path = os.path.join(os.path.dirname(__file__), "Assets", "logo.png")

try:
    # Mengubah gambar ke base64
    logo_base64 = get_image_base64(logo_path)
    
    # 3. Injeksi HTML/CSS dengan Flexbox
    brand_html = f"""
    <div style="position: fixed; top: 15px; left: 30px; z-index: 999999; display: flex; align-items: center; gap: 6px;">
        <img src="data:image/png;base64,{logo_base64}" style="height: 28px; width: auto; object-fit: contain;">
        <span style="font-weight: 700; font-size: 1.5rem; background: linear-gradient(135deg, #FFD54F 0%, #FF7043 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0px 1px 2px rgba(0,0,0,0.5));">TripMatch</span>
    </div>
    """
    st.markdown(brand_html, unsafe_allow_html=True)

except FileNotFoundError:
    # Error handling jika path folder salah
    st.error("Logo tidak ditemukan! Pastikan file berada di folder Assets/logo.png")

# ── Hero Background (hanya untuk layar pertama / sebelum preferensi dipilih) ──
# Gambar di-embed sebagai base64 agar tidak bergantung pada serving file statis.
bg_path = os.path.join(os.path.dirname(__file__), "Assets", "background1.jpg")
try:
    bg_base64 = get_image_base64(bg_path)
    # Layer fixed full-viewport yang hanya terlihat selama BELUM ada preferensi terpilih.
    # Begitu konten baru muncul di bawah, layer ini sudah tidak relevan karena
    # ia hanya setinggi 100vh dan fixed — area di bawah layar pertama tetap
    # menggunakan .stApp background (gradient dark).
    hero_bg_css = f"""
    <style>
        /* ── Hero background image layer ── */
        body::before {{
            content: "";
            position: fixed;
            inset: 0;                       /* top/right/bottom/left = 0 */
            z-index: -1;                    /* tepat di belakang semua konten */
            background-image: url("data:image/jpeg;base64,{bg_base64}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            /* Hanya tampil saat belum ada preferensi: dikontrol via JS di bawah */
            opacity: 1;
            transition: opacity 0.6s ease;
        }}

        /* ── Dark overlay di atas gambar ── */
        body::after {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: -1;                    /* sama z-index dengan ::before tapi ::after di atas ::before */
            background: rgba(5, 8, 18, 0.55);
            pointer-events: none;
            transition: opacity 0.6s ease;
        }}

        /* Saat kelas 'pref-selected' ditambahkan ke body, sembunyikan hero layer */
        body.pref-selected::before,
        body.pref-selected::after {{
            opacity: 0;
            pointer-events: none;
        }}

        /* Pastikan .stApp tetap transparan agar gambar di body::before terlihat */
        .stApp {{
            background: transparent !important;
        }}

        /* Gradient gelap untuk area di bawah layar pertama (scroll ke bawah) */
        .stApp > div:first-child {{
            background: transparent;
        }}
    </style>
    """
    st.markdown(hero_bg_css, unsafe_allow_html=True)

    # JS: amati nilai selectbox preferensi — jika sudah dipilih, tambahkan kelas
    # 'pref-selected' ke body sehingga hero image + overlay ter-fade-out via CSS.
    hero_js = """
    <script>
    (function() {
        function checkPref() {
            // Streamlit merender selectbox sebagai <div data-baseweb="select">
            // Nilai yang sedang dipilih ada di <span> pertama di dalam komponen tersebut.
            var selects = document.querySelectorAll('[data-baseweb="select"] [class*="valueContainer"] span');
            var prefSelected = false;
            for (var i = 0; i < selects.length; i++) {
                var txt = selects[i].textContent.trim();
                if (txt && txt !== 'Pilih Preferensi...') {
                    prefSelected = true;
                    break;
                }
            }
            if (prefSelected) {
                document.body.classList.add('pref-selected');
            } else {
                document.body.classList.remove('pref-selected');
            }
        }

        // Jalankan sekali saat halaman dimuat
        checkPref();

        // Amati perubahan DOM dengan MutationObserver
        var observer = new MutationObserver(function() {
            checkPref();
        });
        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    })();
    </script>
    """
    st.markdown(hero_js, unsafe_allow_html=True)
except FileNotFoundError:
    pass  # Jika background tidak ditemukan, pakai gradient default

# Main Header (Tugas 3)
st.markdown('<div class="app-title">Where to?</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Perjalanan singkat, cerita yang tak terlupakan.</div>', unsafe_allow_html=True)

# Memuat data destinasi
try:
    df_dest = load_destinations()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

def parse_estimasi_biaya(val):
    """
    Mengembalikan (min, max) dari Estimasi Biaya Kunjungan.
    Menangani angka tunggal maupun teks rentang seperti '80.000–130.000'.
    """
    if pd.isna(val):
        return (0, 0)
    if isinstance(val, (int, float)):
        return (val, val)
    s = str(val).replace('.', '').replace('—', '-').replace('–', '-').strip()
    parts = [p.strip() for p in s.split('-') if p.strip().isdigit()]
    numbers = [int(p) for p in parts]
    if len(numbers) >= 2:
        return (min(numbers), max(numbers))
    elif len(numbers) == 1:
        return (numbers[0], numbers[0])
    return (0, 0)

# Helper rupiah formatting
def format_rupiah(val):
    if pd.isna(val) or val == 0:
        return "Gratis/Sesuai infomasi tiket"
    if isinstance(val, str):
        return f"Rp{val}"  # sudah berupa teks rentang, misal "80.000–130.000" -> "Rp80.000–130.000"
    return f"Rp{val:,.0f}".replace(",", ".")

# Folder tempat gambar destinasi disimpan (mengikuti nama Place_Name)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "Assets")
FALLBACK_IMAGE_NAME = "gambar_tidak_tersedia.jpg"

def _mime_from_ext(ext):
    ext = ext.lower().lstrip(".")
    mapping = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}
    return mapping.get(ext, "jpeg")

def get_dest_image_data_uri(place_name):
    """
    Mencari file gambar di folder Assets/ dengan nama PERSIS sama dengan Place_Name
    (mengikuti beberapa kemungkinan ekstensi umum). Jika tidak ditemukan, pakai
    gambar fallback 'gambar_tidak_tersedia.jpg'. Mengembalikan None jika keduanya
    tidak ada (supaya card tetap tampil tanpa gambar, tidak error).
    """
    candidate_extensions = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]

    for ext in candidate_extensions:
        candidate_path = os.path.join(ASSETS_DIR, f"{place_name}{ext}")
        if os.path.isfile(candidate_path):
            try:
                b64 = get_image_base64(candidate_path)
                return f"data:image/{_mime_from_ext(ext)};base64,{b64}"
            except Exception:
                break

    # Fallback ke gambar default jika gambar destinasi belum tersedia
    fallback_path = os.path.join(ASSETS_DIR, FALLBACK_IMAGE_NAME)
    if os.path.isfile(fallback_path):
        try:
            b64 = get_image_base64(fallback_path)
            return f"data:image/{_mime_from_ext(FALLBACK_IMAGE_NAME)};base64,{b64}"
        except Exception:
            return None

    return None


def get_detail_image_data_uri(place_name):
    """
    Mencari gambar detail di folder Assets/ dengan nama '{place_name}1.ext'.
    Jika tidak ditemukan, pakai gambar fallback 'gambar_tidak_tersedia.jpg'.
    """
    candidate_extensions = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]

    for ext in candidate_extensions:
        candidate_path = os.path.join(ASSETS_DIR, f"{place_name}1{ext}")
        if os.path.isfile(candidate_path):
            try:
                b64 = get_image_base64(candidate_path)
                return f"data:image/{_mime_from_ext(ext)};base64,{b64}"
            except Exception:
                break

    # Fallback ke gambar default
    fallback_path = os.path.join(ASSETS_DIR, FALLBACK_IMAGE_NAME)
    if os.path.isfile(fallback_path):
        try:
            b64 = get_image_base64(fallback_path)
            return f"data:image/{_mime_from_ext(FALLBACK_IMAGE_NAME)};base64,{b64}"
        except Exception:
            return None

    return None


@st.dialog("Detail Destinasi", width="large")
def show_dest_detail(row):
    """Popup dialog yang menampilkan detail lengkap sebuah destinasi wisata."""
    place_name = row['Place_Name']

    # --- Gambar Detail (suffix '1') ---
    detail_image_uri = get_detail_image_data_uri(place_name)
    if detail_image_uri:
        st.markdown(
            f'<img src="{detail_image_uri}" alt="{place_name}" '
            'style="width:100%; border-radius:12px; margin-bottom:16px; object-fit:cover; max-height:320px;">',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div style="font-size:1.3rem; font-weight:700; color:#F8FAFC; margin-bottom:4px;">{place_name}</div>'
        f'<div style="font-size:0.9rem; color:#FF9800; font-weight:500; margin-bottom:16px;">📍 {row["City"]}</div>',
        unsafe_allow_html=True
    )

    # --- Deskripsi ---
    description = row['Description'] if 'Description' in row.index else ''
    if pd.isna(description):
        description = '-'
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px; padding: 14px 16px; margin-bottom: 12px;">
        <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;
                    letter-spacing: 0.06em; margin-bottom: 8px; font-weight: 600;">📝 Deskripsi</div>
        <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.7;">{description}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- Alamat ---
    alamat_val = row['Alamat'] if 'Alamat' in row.index else None
    if alamat_val is None or (not isinstance(alamat_val, str) and pd.isna(alamat_val)):
        alamat = '-'
    else:
        alamat = str(alamat_val).strip() or '-'
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px; padding: 14px 16px; margin-bottom: 4px;">
        <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;
                    letter-spacing: 0.06em; margin-bottom: 8px; font-weight: 600;">📍 Alamat</div>
        <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.7;">{alamat}</div>
    </div>
    """, unsafe_allow_html=True)


# Helper untuk merender daftar card destinasi secara HORIZONTAL dengan drag-to-scroll (mouse)
def render_dest_cards_horizontal(candidates, height=620):
    cards_html = ""
    for _, row in candidates.iterrows():
        transports = []
        if row['Motor Pribadi'] == 1:
            transports.append("🏍️ Motor Pribadi")
        if row['Mobil Pribadi'] == 1:
            transports.append("🚗 Mobil Pribadi")
        if row['Transportasi Umum Konvensional'] == 1:
            transports.append("🚌 Transportasi Umum")

        image_uri = get_dest_image_data_uri(row['Place_Name'])
        image_html = ""
        if image_uri:
            image_html = f"""
            <div class="dest-card-image">
                <img src="{image_uri}" alt="{row['Place_Name']}">
            </div>
            """

        cards_html += f"""
        <div class="dest-card">
            {image_html}
            <div class="dest-card-body">
                <div class="dest-title">{row['Place_Name']}</div>
                <div class="dest-meta">📍 {row['City']}</div>
                <div>
                    <span class="dest-badge">💵 Est. Biaya: {format_rupiah(row['Estimasi Biaya Kunjungan'])}</span>
                    <span class="dest-badge">🕒 Durasi: {row['Durasi Perjalan']}</span>
                </div>
                <div style="margin-top: 8px;">
                    {" ".join([f'<span class="dest-badge">{t}</span>' for t in transports])}
                </div>
            </div>
        </div>
        """

    html_code = f"""
    <html>
    <head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Outfit', sans-serif;
            overflow-x: hidden;
            overflow-y: hidden;
        }}
        .dest-scroll-container {{
            display: flex;
            gap: 24px;
            overflow-x: scroll;             /* scroll = selalu tampil, bukan auto */
            overflow-y: hidden;
            cursor: grab;
            padding: 4px 4px 24px 4px;     /* padding bawah cukup untuk scrollbar */
            box-sizing: border-box;
            user-select: none;
            /* Firefox */
            scrollbar-width: auto;
            scrollbar-color: #1A8CFF rgba(255,255,255,0.10);
        }}
        .dest-scroll-container.grabbing {{
            cursor: grabbing;
        }}

        /* ── Webkit Scrollbar — lebih tebal & terlihat ── */
        .dest-scroll-container::-webkit-scrollbar {{
            height: 10px;
        }}
        .dest-scroll-container::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.07);
            border-radius: 999px;
            margin: 0 4px;
        }}
        .dest-scroll-container::-webkit-scrollbar-thumb {{
            background: linear-gradient(90deg, #00CFE8 0%, #1A8CFF 60%, #7F00FF 100%);
            border-radius: 999px;
            border: 2px solid rgba(0,0,0,0.3);
            min-width: 48px;
        }}
        .dest-scroll-container::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(90deg, #00e5ff 0%, #3fa9ff 60%, #a040ff 100%);
        }}

        /* ── Scroll shadow effect ── */
        .scroll-wrapper {{
            position: relative;
            width: 100%;
        }}

        /* Fade kiri — tampil saat ada konten tersembunyi di kiri */
        .scroll-fade-left,
        .scroll-fade-right {{
            position: absolute;
            top: 0;
            bottom: 10px;           /* tidak menutupi scrollbar */
            width: 60px;
            pointer-events: none;
            z-index: 10;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .scroll-fade-left {{
            left: 0;
            background: linear-gradient(to right, rgba(11, 14, 23, 0.85), transparent);
        }}
        .scroll-fade-right {{
            right: 0;
            background: linear-gradient(to left, rgba(11, 14, 23, 0.85), transparent);
        }}

        /* Scroll hint badge */
        .scroll-hint {{
            position: absolute;
            bottom: 22px;
            right: 8px;
            background: rgba(26, 140, 255, 0.18);
            border: 1px solid rgba(26, 140, 255, 0.35);
            color: #7DBFFF;
            font-size: 0.72rem;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: 999px;
            backdrop-filter: blur(4px);
            pointer-events: none;
            opacity: 1;
            transition: opacity 0.4s ease;
            letter-spacing: 0.03em;
        }}

        /* Lebar card dihitung agar PAS 3 card penuh terlihat di satu layar */
        .dest-card {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            overflow: hidden;
            transition: background 0.3s ease, border-color 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            flex: 0 0 calc((100% - 2 * 24px) / 3);
            width: calc((100% - 2 * 24px) / 3);
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}
        .dest-card:hover {{
            background: rgba(30, 41, 59, 0.9);
            border-color: rgba(26, 140, 255, 0.4);
        }}
        /* Container gambar dikonsistenkan rasio 4:3, gambar boleh terpotong (object-fit: cover) */
        .dest-card-image {{
            width: 100%;
            aspect-ratio: 4 / 3;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.04);
            flex-shrink: 0;
        }}
        .dest-card-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .dest-card-body {{
            padding: 20px 24px 24px 24px;
        }}
        .dest-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #F8FAFC;
            margin-bottom: 6px;
        }}
        .dest-meta {{
            font-size: 0.9rem;
            color: #FF9800;
            font-weight: 500;
            margin-bottom: 14px;
        }}
        .dest-desc {{
            font-size: 0.9rem;
            color: #94A3B8;
            line-height: 1.6;
            margin-bottom: 18px;
        }}
        .dest-badge {{
            display: inline-block;
            background: rgba(148, 163, 184, 0.1);
            color: #CBD5E1;
            font-size: 0.78rem;
            font-weight: 500;
            padding: 5px 10px;
            border-radius: 6px;
            margin-right: 6px;
            margin-bottom: 6px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
    </style>
    </head>
    <body>
        <div class="scroll-wrapper" id="scrollWrapper">
            <div class="scroll-fade-left" id="fadeLeft"></div>
            <div class="scroll-fade-right" id="fadeRight"></div>
            <div class="dest-scroll-container" id="destScroll">
                {cards_html}
            </div>
            <div class="scroll-hint" id="scrollHint">&#8592; geser &#8594;</div>
        </div>
        <script>
            const slider = document.getElementById('destScroll');
            const fadeLeft = document.getElementById('fadeLeft');
            const fadeRight = document.getElementById('fadeRight');
            const scrollHint = document.getElementById('scrollHint');
            let isDown = false;
            let startX;
            let scrollLeftStart;
            let hintDismissed = false;

            function updateFades() {{
                const maxScroll = slider.scrollWidth - slider.clientWidth;
                fadeLeft.style.opacity = slider.scrollLeft > 10 ? '1' : '0';
                fadeRight.style.opacity = (maxScroll - slider.scrollLeft) > 10 ? '1' : '0';
            }}

            // Init
            updateFades();

            // Sembunyikan scroll hint setelah pertama kali scroll
            slider.addEventListener('scroll', () => {{
                updateFades();
                if (!hintDismissed) {{
                    hintDismissed = true;
                    scrollHint.style.opacity = '0';
                    setTimeout(() => scrollHint.style.display = 'none', 400);
                }}
            }});

            slider.addEventListener('mousedown', (e) => {{
                isDown = true;
                slider.classList.add('grabbing');
                startX = e.pageX - slider.offsetLeft;
                scrollLeftStart = slider.scrollLeft;
                if (!hintDismissed) {{
                    hintDismissed = true;
                    scrollHint.style.opacity = '0';
                    setTimeout(() => scrollHint.style.display = 'none', 400);
                }}
            }});
            slider.addEventListener('mouseleave', () => {{
                isDown = false;
                slider.classList.remove('grabbing');
            }});
            window.addEventListener('mouseup', () => {{
                isDown = false;
                slider.classList.remove('grabbing');
            }});
            slider.addEventListener('mousemove', (e) => {{
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - slider.offsetLeft;
                const walk = (x - startX) * 1.5;
                slider.scrollLeft = scrollLeftStart - walk;
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)

# Initialize session state for progressive steps
if 'selected_pref' not in st.session_state:
    st.session_state.selected_pref = None
if 'selected_subpref' not in st.session_state:
    st.session_state.selected_subpref = None
if 'predict_clicked' not in st.session_state:
    st.session_state.predict_clicked = False
if 'detail_dest_row' not in st.session_state:
    st.session_state.detail_dest_row = None

# Initialize variables to avoid UnboundLocalError
user_budget = None
user_transport = None
user_duration = None

# Grid Layout untuk Langkah 1 (Tugas 2)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="section-title">Preferensi Wisata Utama</div>', unsafe_allow_html=True)

    # 1. Buat teks label kustom Anda sendiri dengan class CSS baru (misal: "custom-label")
    st.markdown('<div class="custom-label">Kategori wisata apa yang paling ingin Anda kunjungi?</div>', unsafe_allow_html=True)
    preferensi_options = ["Pilih Preferensi..."] + get_preferensi_list(df_dest)
    selected_pref = st.selectbox(
        "",
        options=preferensi_options,
        index=0,
        key="pref_selectbox",
        label_visibility="collapsed"
    )
    
    # Update session state jika preferensi berubah
    if selected_pref != "Pilih Preferensi...":
        if st.session_state.selected_pref != selected_pref:
            st.session_state.selected_pref = selected_pref
            st.session_state.selected_subpref = None
            st.session_state.predict_clicked = False
    else:
        st.session_state.selected_pref = None
        st.session_state.selected_subpref = None
        st.session_state.predict_clicked = False
    st.markdown('</div>', unsafe_allow_html=True)

# Alur Logika Progressive Interaction (Tugas 5 & Tugas 1)
# Susunan vertikal: Destinasi (by Preferensi) -> Subpreferensi -> Destinasi (by Preferensi+Subpreferensi) -> Form Profil
if st.session_state.selected_pref:
    # LANGKAH 2: DESTINASI WISATA BERDASARKAN PREFERENSI
    # Sengaja diletakkan DI LUAR col2 supaya melebar penuh (full-width) ke kiri & kanan layar,
    # tetap ada jarak tipis mengikuti padding bawaan Streamlit (bukan menempel mepet ke tepi).
    candidates_pref = filter_destinations(df_dest, st.session_state.selected_pref, None)

    st.markdown(f'<div class="section-title">Destinasi Wisata ({len(candidates_pref)} Ditemukan)</div>', unsafe_allow_html=True)
    st.write(f"Berikut seluruh destinasi wisata untuk preferensi **{st.session_state.selected_pref}**:")
    render_dest_cards_horizontal(candidates_pref)

    # --- Tombol Detail untuk setiap card di horizontal scroll ---
    pref_rows = list(candidates_pref.iterrows())
    if pref_rows:
        with st.expander("🔍 Selengkapnya — Pilih destinasi untuk melihat detail"):
            n_pref = len(pref_rows)
            exp_cols_pref = st.columns(min(n_pref, 4))
            for i, (_, row) in enumerate(pref_rows):
                with exp_cols_pref[i % min(n_pref, 4)]:
                    if st.button(f"📍 {row['Place_Name']}", key=f"pref_detail_btn_{i}", use_container_width=True):
                        show_dest_detail(row)
    st.markdown('</div>', unsafe_allow_html=True)

    # Membuat BARIS KOLOM BARU (bukan reuse col2 lama) supaya posisinya benar-benar
    # muncul di bawah section full-width di atas, sesuai urutan kode.
    sub_col1, sub_col2, sub_col3 = st.columns([1, 2, 1])

    with sub_col2:
        # LANGKAH 3: SUBPREFERENSI
        st.markdown(f'<div class="section-title">Subpreferensi Wisata {st.session_state.selected_pref}</div>', unsafe_allow_html=True)

        subpref_options = ["Pilih Subpreferensi..."] + get_subpreferensi_by_preferensi(df_dest, st.session_state.selected_pref)
        selected_subpref = st.selectbox(
            f"Subpreferensi {st.session_state.selected_pref} mana yang paling menarik bagi Anda?",
            options=subpref_options,
            index=0,
            key="subpref_selectbox"
        )

        if selected_subpref != "Pilih Subpreferensi...":
            st.session_state.selected_subpref = selected_subpref
        else:
            st.session_state.selected_subpref = None
            st.session_state.predict_clicked = False
        st.markdown('</div>', unsafe_allow_html=True)

    # LANGKAH 4: DESTINASI WISATA BERDASARKAN PREFERENSI + SUBPREFERENSI (section baru, terpisah)
    # Diletakkan DI LUAR sub_col2 (full-width, sama seperti section by Preferensi di atas)
    # supaya konsisten: horizontal-scroll + bisa digeser dengan cursor.
    if st.session_state.selected_subpref:
        candidates_subpref = filter_destinations(df_dest, st.session_state.selected_pref, st.session_state.selected_subpref)

        st.markdown(f'<div class="section-title">Destinasi Wisata ({len(candidates_subpref)} Ditemukan)</div>', unsafe_allow_html=True)
        st.write(f"Berikut destinasi wisata untuk preferensi **{st.session_state.selected_pref}** - subpreferensi **{st.session_state.selected_subpref}** (geser kartu ke kiri/kanan):")
        render_dest_cards_horizontal(candidates_subpref)

        # --- Tombol Detail untuk setiap card di horizontal scroll ---
        subpref_rows = list(candidates_subpref.iterrows())
        if subpref_rows:
            with st.expander("🔍 Selengkapnya — Pilih destinasi untuk melihat detail"):
                n_subpref = len(subpref_rows)
                exp_cols_subpref = st.columns(min(n_subpref, 4))
                for i, (_, row) in enumerate(subpref_rows):
                    with exp_cols_subpref[i % min(n_subpref, 4)]:
                        if st.button(f"📍 {row['Place_Name']}", key=f"subpref_detail_btn_{i}", use_container_width=True):
                            show_dest_detail(row)
        st.markdown('</div>', unsafe_allow_html=True)

        # LANGKAH 5: FORM PROFIL PERJALANAN — kembali ke kolom tengah (narrower), muncul di bawah section destinasi
        form_col1, form_col2, form_col3 = st.columns([1, 2, 1])
        with form_col2:
            st.markdown('<div class="section-title">Profil Perilaku Perjalanan Anda</div>', unsafe_allow_html=True)
            st.write("Isi formulir di bawah ini untuk menentukan karakteristik kelompok (cluster) perjalanan Anda menggunakan K-Means.")

            # Pilihan Form
            budget_form_options = ["Pilih estimasi budget perjalanan Anda..."] + BUDGET_OPTIONS
            user_budget_raw = st.selectbox("1. Estimasi Budget Perjalanan", budget_form_options, index=0)
            user_budget = user_budget_raw if user_budget_raw != budget_form_options[0] else None

            user_transport = st.multiselect(
                "2. Moda Transportasi Utama",
                options=list(TRANSPORT_OPTIONS_MAP.keys()),
                default=[],
                placeholder="Pilih satu atau lebih moda transportasi Anda..."
            )

            durasi_form_options = ["Pilih durasi perjalanan Anda..."] + DURASI_OPTIONS
            user_duration_raw = st.selectbox("3. Durasi Perjalanan", durasi_form_options, index=0)
            user_duration = user_duration_raw if user_duration_raw != durasi_form_options[0] else None



            # Tombol Prediksi
            predict_button = st.button("🚀 Temukan Cluster & Dapatkan Rekomendasi", type="primary", use_container_width=True)
            if predict_button:
                st.session_state.predict_clicked = True


# HASIL PREDIKSI CLUSTER DAN REKOMENDASI TERSEGMENTASI (Baris Bawah)
if st.session_state.selected_pref and st.session_state.selected_subpref and st.session_state.predict_clicked:
    st.markdown('<hr style="border-color: rgba(255,255,255,0.08); margin: 40px 0;">', unsafe_allow_html=True)
    
    # Melakukan preprocessing & prediksi menggunakan data dari form
    with st.spinner("Menganalisis profil perilaku perjalanan menggunakan K-Means..."):
        try:
            cluster_id, profile = preprocess_and_predict(
                pref=st.session_state.selected_pref,
                subpref=st.session_state.selected_subpref,
                budget_str=user_budget,
                transport_list=user_transport,
                durasi_str=user_duration    
            )
        except Exception as e:
            st.error(f"Gagal melakukan klasterisasi: {e}")
            st.stop()
            
    # Tampilkan Hasil Analisis Cluster
    st.markdown(f"""
    <div class="cluster-card" style="border-left: 6px solid {profile['color']};">
        <div class="cluster-glow" style="background: {profile['color']};"></div>
        <div style="position: relative; z-index: 2;">
            <span style="background: {profile['color']}; color: #FFF; padding: 6px 14px; border-radius: 30px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">
                Cluster Terdeteksi: {cluster_id}
            </span>
            <h2 style="margin-top: 15px; font-weight: 700; color: #FFF;">{profile['name']}</h2>
            <p style="font-size: 1.1rem; color: #CBD5E1; margin-bottom: 20px; line-height: 1.6;">{profile['description']}</p>
            <div class="row" style="display: flex; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Dominasi Jenis Wisata</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #E2E8F0; margin-top: 4px;">{profile['dominant_pref']}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rekomendasi Tersegementasi: Menampilkan rekomendasi dan memberi kecocokan filter
    st.markdown('<div class="section-title">Rekomendasi Destinasi Wisata Berdasarkan Cluster</div>', unsafe_allow_html=True)
    
    # Grid columns untuk rekomendasi final
    candidates = filter_destinations(df_dest, st.session_state.selected_pref, st.session_state.selected_subpref)
    
    scored_candidates = []
    for idx, row in candidates.iterrows():
        # Evaluasi kecocokan budget
        # Budget options ordinal: 0: <50k, 1: 50k-150k, 2: 150k-300k, 3: >300k
        est_cost = row['Estimasi Biaya Kunjungan']
        est_min, est_max = parse_estimasi_biaya(est_cost)
        budget_matched = False
        if user_budget == 'Kurang dari Rp50.000' and est_min < 50000:
            budget_matched = True
        elif user_budget == 'Rp50.000–Rp150.000' and est_max >= 50000 and est_min <= 150000:
            budget_matched = True
        elif user_budget == 'Rp150.000–Rp300.000' and est_max >= 150000 and est_min <= 300000:
            budget_matched = True
        elif user_budget == 'Lebih dari Rp300.000' and est_max > 300000:
            budget_matched = True

            
        # Evaluasi kecocokan transportasi
        transport_matched = False
        if user_transport:
            if 'Motor Pribadi' in user_transport and row['Motor Pribadi'] == 1:
                transport_matched = True
            if 'Mobil Pribadi' in user_transport and row['Mobil Pribadi'] == 1:
                transport_matched = True
            if 'Transportasi Umum Konvensional' in user_transport and row['Transportasi Umum Konvensional'] == 1:
                transport_matched = True
            
        # Evaluasi kecocokan durasi
        durasi_matched = (row['Durasi Perjalan'] == user_duration)
        
        num_matches = int(budget_matched) + int(transport_matched) + int(durasi_matched)
        num_mismatches = 3 - num_matches
        
        scored_candidates.append({
            'row': row,
            'budget_matched': budget_matched,
            'transport_matched': transport_matched,
            'durasi_matched': durasi_matched,
            'num_mismatches': num_mismatches,
            'est_cost': est_cost
        })

    # Tentukan kecocokan terbaik menggunakan logika fallback bertingkat
    perfect_matches = [c for c in scored_candidates if c['num_mismatches'] == 0]
    
    narrative_text = "Daftar destinasi wisata yang direkomendasikan berdasarkan Preferensi dan Subpreferensi yang Anda pilih, dengan tag kecocokan terhadap parameter perjalanan personal Anda:"
    display_candidates = []
    
    if len(perfect_matches) > 0:
        display_candidates = perfect_matches
    else:
        # Fallback 1: maksimal ada 1 kecocokan profil yang tidak cocok (artinya <= 1 mismatch)
        fallback_1 = [c for c in scored_candidates if c['num_mismatches'] <= 1]
        if len(fallback_1) > 0:
            display_candidates = fallback_1
            narrative_text = "Destinasi Wisata yang cocok dengan profil anda sangat terbatas. Berikut yang paling cocok: "
        else:
            # Fallback 2: maksimal ada 2 kecocokan profil yang tidak cocok (artinya <= 2 mismatch)
            fallback_2 = [c for c in scored_candidates if c['num_mismatches'] <= 2]
            if len(fallback_2) > 0:
                display_candidates = fallback_2
                narrative_text = "Destinasi Wisata yang cocok dengan profil anda sangat terbatas. Berikut yang paling cocok: "
            else:
                narrative_text = "Tidak ada destinasi wisata yang cocok dengan profil perjalanan Anda."
                
    st.write(narrative_text)
    
    if len(display_candidates) > 0:
        cols = st.columns(3)
        for idx, item in enumerate(display_candidates):
            col_target = cols[idx % 3]
            row = item['row']
            budget_matched = item['budget_matched']
            transport_matched = item['transport_matched']
            durasi_matched = item['durasi_matched']
            est_cost = item['est_cost']
            
            # CSS class untuk badge kecocokan
            b_class = "dest-badge badge-match" if budget_matched else "dest-badge"
            t_class = "dest-badge badge-match" if transport_matched else "dest-badge"
            d_class = "dest-badge badge-match" if durasi_matched else "dest-badge"
            
            with col_target:
                image_uri = get_dest_image_data_uri(row['Place_Name'])
                image_html = ""
                if image_uri:
                    image_html = f'<div class="dest-card-image"><img src="{image_uri}" alt="{row["Place_Name"]}"></div>'

                st.markdown(f"""
                <div class="dest-card" style="border-top: 4px solid {profile['color']};">
                    {image_html}
                    <div class="dest-card-body">
                        <div class="dest-title">{row['Place_Name']}</div>
                        <div class="dest-meta">📍 {row['City']}</div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px; margin-top: 12px;">
                            <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 8px;">Kecocokan Profil:</div>
                            <span class="{b_class}">💵 Cost: {format_rupiah(est_cost)}</span>
                            <span class="{d_class}">🕒 Durasi: {row['Durasi Perjalan']}</span>
                            <span class="{t_class}">🚗 Trans.: {", ".join(user_transport) if user_transport else "-"}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔍 Detail", key=f"detail_btn_{idx}", use_container_width=True):
                    show_dest_detail(row)
    else:
        st.info("Silakan sesuaikan pilihan Profil Perjalanan Anda untuk menemukan kecocokan yang lebih baik.")