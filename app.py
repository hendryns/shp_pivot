import streamlit as st
import geopandas as gpd
import pandas as pd
import pygwalker as pyg
import zipfile
import os
import tempfile
import shutil

# Konfigurasi Halaman menjadi lebar penuh
st.set_page_config(page_title="SHP Pivot Tool", layout="wide")

st.title("🗺️ SHP Pivot & Analysis Tool")
st.markdown("""
Aplikasi ini mengubah data Shapefile (.shp) menjadi interaktif Pivot Table dengan sistem **Drag & Drop**.
Silakan upload file SHP anda yang sudah di-kompres menjadi **.zip**.
""")

# --- Fungsi Helper untuk Ekstrak ZIP ---
def load_shp_from_zip(zip_file):
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            z.extractall(temp_dir)
        
        # Mencari file .shp di dalam folder hasil ekstrak
        shp_file = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".shp"):
                    shp_file = os.path.join(root, file)
                    break
        
        if shp_file:
            # Membaca data menggunakan Geopandas
            gdf = gpd.read_file(shp_file)
            return gdf
        else:
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
        return None

# --- Upload Area ---
uploaded_file = st.file_uploader("Upload File ZIP (berisi .shp, .shx, .dbf)", type="zip")

if uploaded_file is not None:
    with st.spinner('Membaca data SHP...'):
        gdf = load_shp_from_zip(uploaded_file)

    if gdf is not None:
        # Konversi geometri ke string (opsional, agar tidak berat di pivot jika kompleks)
        # Atau kita bisa drop geometry jika hanya butuh data atribut untuk pivot
        st.success("File berhasil dimuat!")
        
        # Opsi: Gunakan hanya data atribut (tanpa peta) atau tetap dengan Geometri
        use_geometry = st.checkbox("Sertakan Data Geometri (Peta)", value=False)
        
        if not use_geometry:
            df = pd.DataFrame(gdf.drop(columns='geometry'))
            st.info("Mode Data Atribut: Kolom geometri dihilangkan untuk performa pivot lebih cepat.")
        else:
            df = gdf
            st.info("Mode Geospasial: Anda bisa drag-and-drop koordinat untuk membuat peta.")

        st.markdown("---")
        st.subheader("🛠️ Ruang Kerja Analisis (Drag & Drop)")
        st.markdown("Geser kolom dari kiri ke sumbu X/Y atau Rows/Columns untuk membuat Pivot Table atau Grafik.")

        # --- INI ADALAH BAGIAN UTAMA (PyGWalker) ---
        # Ini akan merender HTML interaktif untuk pivot table
        walker = pyg.walk(df, env='Streamlit', dark='light')
        
    else:
        st.error("Tidak ditemukan file .shp di dalam ZIP tersebut.")

else:
    st.info("Silakan upload file .zip untuk memulai.")
