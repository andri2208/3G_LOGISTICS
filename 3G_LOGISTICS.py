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
# Mengambil logo dan header dari folder project Anda
st.image("HEADER INVOICE.png", use_container_width=True)

# --- AMBIL URL DARI SECRETS ---
try:
    # Baris di bawah ini harus menjorok ke dalam (4 spasi)
    API_URL = st.secrets["general"]["api_url"]
except Exception as e:
    st.error("PENTING: Masukkan 'api_url' di Settings > Secrets Streamlit Cloud Anda!")
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

# TAB 1: DASHBOARD (Melihat data yang sudah ada di Google Sheets)
with tabs[0]:
    st.subheader("Data Pengiriman Terdaftar")
    df = get_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data atau koneksi Apps Script sedang bermasalah.")

# TAB 2: FORM INPUT (Sesuai format dokumen INVOICE PT HARVI)
with tabs[1]:
    st.subheader("Form Pembuatan Invoice")
    
    with st.form("invoice_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            customer = st.text_input("CUSTOMER", value="PT HARVI")
            tgl_muat = st.date_input("Date of Load", datetime.now())
            origin = st.text_input("Origin", value="TUAL")
            destination = st.text_input("Destination", value="LARAT")
            
        with col2:
            produk = st.text_input("Product Description", value="3 UNIT CDD")
            harga = st.number_input("Harga (Rp)", min_value=0, value=27000000, step=1000)
            terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah")
            tgl_invoice = st.date_input("DATE (Tanggal Invoice)", datetime.now())

        submitted = st.form_submit_button("Simpan Data ke Google Sheets")

        if submitted:
            # Data dikirim dalam format JSON ke Apps Script
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
                    st.success("✅ Data berhasil tersimpan ke Google Sheets!")
                    st.balloons()
                else:
                    st.error("Gagal mengirim data. Cek koneksi Web App Anda.")
            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {e}")

# --- FOOTER ---
st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])
with col_f2:
    st.write("Sincerely,")
    st.image("STEMPEL TANDA TANGAN.png", width=150)
    st.write("**KELVINITO JAYADI**")
    st.caption("DIREKTUR")


