import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - Sistem Invoice", 
    page_icon="FAVICON.png", 
    layout="wide"
)

# --- LOAD ASET GAMBAR ---
# Menampilkan Header dari file GitHub Anda
st.image("HEADER INVOICE.png", use_container_width=True)

# --- AMBIL URL DARI SECRETS ---
# Pastikan Anda sudah mengisi api_url di Streamlit Cloud Secrets
try:
    API_URL = st.secrets["general"]["api_url"]
except:
    st.error("Error: 'api_url' tidak ditemukan di Streamlit Secrets.")
    st.stop()

# --- FUNGSI AMBIL DATA ---
def get_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- TAMPILAN UTAMA ---
st.title("Sistem Logistik PT. GAMA GEMAH GEMILANG")

tabs = st.tabs(["📊 Dashboard Data", "📝 Input Invoice Baru"])

# TAB 1: DASHBOARD
with tabs[0]:
    st.subheader("Data Pengiriman Terdaftar")
    df = get_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data atau koneksi Apps Script bermasalah.")

# TAB 2: FORM INPUT (Sesuai PDF Invoice)
with tabs[1]:
    [cite_start]st.subheader("Form Pembuatan Invoice") [cite: 4]
    
    with st.form("invoice_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            [cite_start]customer = st.text_input("CUSTOMER", value="PT HARVI") [cite: 3]
            [cite_start]tgl_muat = st.date_input("Date of Load", datetime.now()) [cite: 5]
            [cite_start]origin = st.text_input("Origin", value="TUAL") [cite: 5]
            [cite_start]destination = st.text_input("Destination", value="LARAT") [cite: 5]
            
        with col2:
            [cite_start]produk = st.text_input("Product Description", value="3 UNIT CDD") [cite: 5]
            [cite_start]harga = st.number_input("Harga (Rp)", min_value=0, value=27000000, step=1000) [cite: 5]
            [cite_start]terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah") [cite: 6]
            [cite_start]tgl_invoice = st.date_input("DATE (Tanggal Invoice)", datetime.now()) [cite: 13]

        submitted = st.form_submit_button("Simpan Data ke Google Sheets")

        if submitted:
            # Data dikirim dalam format JSON
            payload = {
                "date_load": tgl_muat.strftime("%d-%b-%y"),
                "customer": customer,
                "description": produk,
                "origin": origin,
                "destination": destination,
                "harga": harga,
                "terbilang": terbilang,
                "date_invoice": tgl_invoice.strftime("%d/%m/%Y")
            }
            
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    st.success("✅ Data berhasil tersimpan!")
                    st.balloons()
                else:
                    st.error("Gagal mengirim data.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# --- FOOTER ---
st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])
with col_f2:
    [cite_start]st.write("Sincerely,") [cite: 14]
    st.image("STEMPEL TANDA TANGAN.png", width=150)
    [cite_start]st.write("**KELVINITO JAYADI**") [cite: 16]
    [cite_start]st.caption("DIREKTUR") [cite: 17]
