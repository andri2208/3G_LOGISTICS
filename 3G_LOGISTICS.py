import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import os
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman
try:
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="wide")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

# 2. Banner Header
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

# 3. Koneksi ke Google Sheets
# Masukkan URL Google Sheet kamu di sini
URL_SHEET = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi mengambil data
def get_data():
    return conn.read(spreadsheet=URL_SHEET, usecols=[0,1,2,3,4])

# 4. Sidebar Navigasi
with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=120)
    menu = st.radio("Pilih Menu:", ["Dashboard", "Input Pengiriman", "Lacak Resi"])

# 5. Logika Menu
if menu == "Dashboard":
    st.subheader("🏠 Data Pengiriman Real-time")
    df = get_data()
    st.dataframe(df, use_container_width=True)

elif menu == "Input Pengiriman":
    st.subheader("📝 Input Paket Baru")
    with st.form("input_form"):
        resi = st.text_input("Nomor Resi", value=f"3G-{datetime.now().strftime('%d%H%M')}")
        nama = st.text_input("Nama Penerima")
        layanan = st.selectbox("Layanan", ["Regular", "Express", "Kargo"])
        status = "Sedang Diproses"
        
        submitted = st.form_submit_button("Simpan ke Cloud")
        
        if submitted:
            # Ambil data lama, tambah data baru
            df_lama = get_data()
            data_baru = pd.DataFrame([{
                "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Resi": resi,
                "Penerima": nama,
                "Layanan": layanan,
                "Status": status
            }])
            df_final = pd.concat([df_lama, data_baru], ignore_index=True)
            
            # Update ke Google Sheets
            conn.update(spreadsheet=URL_SHEET, data=df_final)
            st.success("Data berhasil tersimpan di Google Sheets!")

elif menu == "Lacak Resi":
    st.subheader("🔍 Tracking")
    cari = st.text_input("Masukkan No. Resi")
    if st.button("Cari"):
        df = get_data()
        hasil = df[df['Resi'] == cari]
        if not hasil.empty:
            st.success(f"Status Paket: {hasil.iloc[0]['Status']}")
            st.write(hasil)
        else:
            st.error("Resi tidak ditemukan.")

st.divider()
st.caption("© 2026 3G LOGISTICS - Sistem Terintegrasi Cloud")
