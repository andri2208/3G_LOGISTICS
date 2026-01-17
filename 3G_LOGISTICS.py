import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import base64
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

# --- PASTE URL WEB APP DARI GOOGLE APPS SCRIPT DI SINI ---
URL_SCRIPT_GOOGLE = "ISI_DENGAN_URL_DARI_APPS_SCRIPT_ANDA"

# --- FUNGSI MUAT DATA (READ ONLY) ---
# Menggunakan link CSV untuk tampilan database yang ringan
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/export?format=csv"

def muat_data():
    try:
        return pd.read_csv(URL_SHEET_CSV).fillna('')
    except:
        return pd.DataFrame(columns=["Tanggal", "Resi", "Pengirim", "Penerima", "Produk", "Origin", "Destination", "Kolli", "Berat", "Harga", "Total"])

# --- FUNGSI TERBILANG ---
def terbilang(n):
    n = int(n)
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[n]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return "Angka terlalu besar"

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- APLIKASI UTAMA ---
st.title("🚚 3G LOGISTICS - Management System")

if 'df' not in st.session_state:
    st.session_state.df = muat_data()

tab1, tab2, tab3 = st.tabs(["➕ Input Pengiriman", "📋 Database (Google Sheets)", "📄 Cetak Invoice"])

with tab1:
    with st.form("form_input", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No. Resi")
            pengirim = st.text_input("Nama Customer (Pengirim)")
            produk = st.text_input("Deskripsi Produk")
            origin = st.text_input("Origin")
        with c2:
            penerima = st.text_input("Nama Penerima")
            destination = st.text_input("Destination")
            kolli = st.number_input("KOLLI", min_value=1, value=1)
            berat = st.number_input("Weight (Kg)", min_value=1, value=1)
            harga_satuan = st.number_input("Harga Satuan (Rp)", min_value=0, value=0)
        
        if st.form_submit_button("Simpan Data ke Cloud"):
            total = berat * harga_satuan
            data_json = {
                "Tanggal": datetime.now().strftime("%d-%b-%y"),
                "Resi": resi, "Pengirim": pengirim, "Penerima": penerima,
                "Produk": produk, "Origin": origin, "Destination": destination,
                "Kolli": kolli, "Berat": berat, "Harga": harga_satuan, "Total": total
            }
            
            try:
                # Mengirim data ke Google Sheets melalui Apps Script
                response = requests.post(https://script.google.com/macros/s/AKfycbz-bMYzT2f_WYvuM-2-Mo5D6KhPrwRwQMN9JhIC1dotbHtfGE9RNHMrSYNNxnvbitPr/exec, json=data_json)
                if response.status_code == 200:
                    st.success("✅ DATA BERHASIL DISIMPAN KE GOOGLE SHEETS!")
                    st.session_state.df = muat_data() # Refresh data
                    st.rerun()
                else:
                    st.error(f"Gagal Simpan. Status: {response.status_code}")
            except Exception as e:
                st.error(f"Koneksi Error: {e}")

with tab2:
    st.subheader("📋 Data Real-time dari Google Sheets")
    if st.button("Refresh Data"):
        st.session_state.df = muat_data()
        st.rerun()
    st.dataframe(st.session_state.df, use_container_width=True)

with tab3:
    # Bagian cetak invoice tetap sama seperti sebelumnya
    st.info("Pilih resi dari database untuk cetak invoice")
    if not st.session_state.df.empty:
        resi_sel = st.selectbox("Pilih Nomor Resi", st.session_state.df["Resi"].unique())
        # ... (Kode invoice Anda di sini)
