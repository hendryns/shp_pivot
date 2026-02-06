import streamlit as st
import geopandas as gpd
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer # Import Renderer Khusus
import zipfile
import os
import tempfile
import shutil

# Konfigurasi Halaman
st.set_page_config(page_title="SHP Pivot Tool", layout="wide")

st.title("🗺️ SHP Pivot & Analysis Tool")
st.markdown("""
Aplikasi ini mengubah data Shapefile (.shp) menjadi interaktif Pivot Table.
""")

# --- Fungsi Helper dengan Caching (Agar tidak loading ulang terus) ---
@st.cache_data(show_spinner=False)
def load_shp_from_zip(zip_file, use_geometry):
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            z.extractall(temp_dir)
        
        shp_file = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".shp"):
                    shp_file = os.path.join(root, file)
                    break
        
        if shp_file:
            # Jika user tidak butuh peta, kita ignore geometry biar RAM hemat
            if not use_geometry:
                gdf = gpd.read_file(shp_file, ignore_geometry=True)
            else:
                gdf = gpd.read_file(shp_file)
            return gdf
        else:
            return None
    except Exception as e:
        st.error(f"Error membaca file: {e}")
        return None
    finally:
        # Bersihkan folder temp (opsional, hati-hati jika OS lock file)
        pass

# --- Fungsi Caching untuk Renderer PyGWalker ---
@st.cache_resource
def get_pyg_renderer(dataframe):
    # Menggunakan StreamlitRenderer khusus agar lebih stabil
    return StreamlitRenderer(dataframe, spec="./gw_config.json", spec_io_mode="rw")

# --- Interface Utama ---
uploaded_file = st.file_uploader("Upload File ZIP (Limit file besar tergantung RAM PC Anda)", type="zip")

# Checkbox opsi geometri ditaruh di luar agar user bisa set sebelum upload/proses
use_geometry = st.checkbox("Sertakan Data Geometri/Peta (Berat untuk file >100MB)", value=False)

if uploaded_file is not None:
    with st.spinner('Sedang memproses data... (File besar mungkin butuh waktu)'):
        # Load data
        df = load_shp_from_zip(uploaded_file, use_geometry)

    if df is not None:
        st.success(f"Data berhasil dimuat! Total Baris: {len(df):,}")
        
        # 1. Tampilkan Preview Data (Untuk memastikan data terbaca)
        with st.expander("🔍 Lihat Preview Data Mentah (5 Baris Pertama)"):
            st.dataframe(df.head())

        st.markdown("---")
        st.subheader("🛠️ Ruang Kerja Analisis")
        
        # 2. Render PyGWalker dengan cara yang lebih stabil
        try:
            renderer = get_pyg_renderer(df)
            renderer.explorer()
        except Exception as e:
            st.error(f"Gagal memuat visualisasi: {e}")
            st.warning("Coba kurangi ukuran file atau jalankan tanpa opsi Geometri.")
            
    else:
        st.error("Tidak ditemukan file .shp valid dalam ZIP.")
