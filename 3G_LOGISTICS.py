import streamlit as st
import requests
from datetime import datetime

# URL Apps Script dari Secrets Anda
API_URL = st.secrets["general"]["api_url"]

st.subheader("📝 Buat Invoice Baru")

with st.form("invoice_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        customer = st.text_input("Nama Customer", value="PT HARVI")
        tgl_muat = st.date_input("Tanggal Muat", datetime.now())
        origin = st.text_input("Asal (Origin)", value="TUAL")
        destination = st.text_input("Tujuan (Destination)", value="LARAT")
        
    with col2:
        produk = st.text_area("Deskripsi Produk", value="3 UNIT CDD")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)
        tgl_invoice = st.date_input("Tanggal Invoice", datetime.now())
        terbilang = st.text_input("Terbilang", placeholder="Contoh: Dua puluh tujuh juta rupiah")

    submitted = st.form_submit_button("Simpan & Kirim ke Google Sheets")

    if submitted:
        # Data yang akan dikirim ke Apps Script
        payload = {
            "tanggal_muat": tgl_muat.strftime("%Y-%m-%d"),
            "customer": customer,
            "produk": produk,
            "origin": origin,
            "destination": destination,
            "harga": harga,
            "terbilang": terbilang,
            "tanggal_invoice": tgl_invoice.strftime("%Y-%m-%d")
        }
        
        try:
            # Mengirim data menggunakan metode POST
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                st.success("✅ Data Invoice berhasil disimpan ke Google Sheets!")
            else:
                st.error("❌ Gagal menyimpan data ke server.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
