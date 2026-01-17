import streamlit as st
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

# 2. Menampilkan Header Banner
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)
else:
    st.title("🚚 3G LOGISTICS")

# 3. Sidebar Navigasi
with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=120)
    st.title("Sistem Logistik")
    st.write("PT. GAMA GEMAH GEMILANG")
    st.divider()
    menu = st.radio("Pilih Menu:", ["Dashboard", "Cek Tarif", "Input Pengiriman", "Lacak Resi"])

# Inisialisasi Database Sederhana di Memory (Session State)
if 'database_logistik' not in st.session_state:
    st.session_state.database_logistik = []

# --- LOGIKA MENU ---

if menu == "Dashboard":
    st.subheader("🏠 Ringkasan Pengiriman")
    if st.session_state.database_logistik:
        df = pd.DataFrame(st.session_state.database_logistik)
        st.table(df)
    else:
        st.info("Belum ada data pengiriman hari ini.")

elif menu == "Cek Tarif":
    st.subheader("📊 Estimasi Biaya")
    col1, col2 = st.columns(2)
    with col1:
        asal = st.text_input("Dari Kota (Asal)")
    with col2:
        tujuan = st.text_input("Ke Kota (Tujuan)")
    berat = st.number_input("Berat (Kg)", min_value=1)
    
    if st.button("Hitung Harga"):
        # Contoh logika hitung: 15.000 per kg
        total = berat * 15000
        st.success(f"Estimasi Biaya ke {tujuan}: **Rp {total:,.0f}**")

elif menu == "Input Pengiriman":
    st.subheader("📝 Form Input Paket Baru")
    with st.form("input_form"):
        resi = st.text_input("Nomor Resi", value=f"3G-{datetime.now().strftime('%d%H%M%S')}")
        nama_penerima = st.text_input("Nama Penerima")
        alamat = st.text_area("Alamat Lengkap")
        layanan = st.selectbox("Layanan", ["Regular", "Express", "Kargo"])
        
        submitted = st.form_submit_button("Simpan Data")
        if submitted:
            data_baru = {
                "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Resi": resi,
                "Penerima": nama_penerima,
                "Layanan": layanan,
                "Status": "Sedang Diproses"
            }
            st.session_state.database_logistik.append(data_baru)
            st.success(f"Data Resi {resi} berhasil disimpan!")

elif menu == "Lacak Resi":
    st.subheader("🔍 Tracking System")
    cari_resi = st.text_input("Masukkan No. Resi")
    if st.button("Cari"):
        # Mencari di database session
        hasil = [item for item in st.session_state.database_logistik if item["Resi"] == cari_resi]
        if hasil:
            st.json(hasil[0])
        else:
            st.error("Nomor resi tidak ditemukan dalam sistem.")

# Footer
st.divider()
st.caption("© 2026 PT. GAMA GEMAH GEMILANG - 3G LOGISTICS System")
