import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import os
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman & Favicon
try:
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="wide")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

# 2. Banner Header
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)
else:
    st.title("🚚 3G LOGISTICS")

# 3. Koneksi Database Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data():
    # Mengambil data terbaru dari Google Sheets
    return conn.read(spreadsheet=SHEET_URL, ttl="0s") # ttl=0 agar data selalu paling baru

# 4. Sidebar Navigasi
with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=120)
    st.title("PT. GAMA GEMAH GEMILANG")
    st.divider()
    menu = st.radio("Pilih Menu:", ["🏠 Dashboard", "📝 Input Paket", "🔍 Lacak Resi"])

# 5. Logika Aplikasi
if menu == "🏠 Dashboard":
    st.subheader("Data Pengiriman Terkini")
    df = muat_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data di Google Sheets.")

elif menu == "📝 Input Paket":
    st.subheader("Input Data Pengiriman Baru")
    with st.form("form_logistik"):
        col1, col2 = st.columns(2)
        with col1:
            resi = st.text_input("Nomor Resi", value=f"3G-{datetime.now().strftime('%d%H%M')}")
            penerima = st.text_input("Nama Penerima")
        with col2:
            layanan = st.selectbox("Layanan", ["Regular", "Express", "Kargo"])
            status = st.selectbox("Status Awal", ["Booking", "Pick Up", "In Transit"])
        
        submit = st.form_submit_button("Simpan ke Database Cloud")
        
        if submit:
            # Ambil data lama
            df_lama = muat_data()
            # Buat data baru
            data_baru = pd.DataFrame([{
                "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Resi": resi,
                "Penerima": penerima,
                "Layanan": layanan,
                "Status": status
            }])
            # Gabungkan
            df_final = pd.concat([df_lama, data_baru], ignore_index=True)
            # Update ke Cloud
            conn.update(spreadsheet=SHEET_URL, data=df_final)
            st.success(f"Berhasil! Resi {resi} telah tersimpan di Google Sheets.")

elif menu == "🔍 Lacak Resi":
    st.subheader("Lacak Posisi Paket")
    cari_resi = st.text_input("Masukkan Nomor Resi")
    if st.button("Cari Sekarang"):
        df = muat_data()
        hasil = df[df['Resi'].astype(str) == cari_resi]
        
        if not hasil.empty:
            st.success(f"Status Saat Ini: **{hasil.iloc[0]['Status']}**")
            st.table(hasil)
        else:
            st.error("Nomor resi tidak ditemukan. Pastikan penulisan benar.")

st.divider()
st.caption("© 2026 3G LOGISTICS | Powered by Streamlit & Google Cloud")
