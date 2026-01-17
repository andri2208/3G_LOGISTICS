import streamlit as st
from PIL import Image
import os

# 1. Konfigurasi Halaman & Favicon (Ikon di Tab Browser)
# Pastikan file FAVICON.png ada di folder yang sama
try:
    img = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=img)
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚")

# 2. Sidebar - Menampilkan Logo di bagian atas menu
with st.sidebar:
    if os.path.exists("HEADER INVOICE.png"):
        st.image("HEADER INVOICE.png", width=300)
    else:
        st.write("🚚 **3G LOGISTICS**")
    
    st.divider()
    menu = st.selectbox("Pilih Menu", ["Cek Tarif", "Tracking Resi", "Tentang Kami"])

# 3. Header Utama (Mengganti Emoji Mobil dengan Gambar)
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("HEADER INVOICE.png"):
        st.image("HEADER INVOICE.png", width=200)
    else:
        st.title("🚚")
with col2:
    st.title("3G LOGISTICS")

st.markdown("### Solusi Pengiriman Cepat & Terpercaya")
st.divider()

# --- Database Sederhana ---
TARIF_KOTA = {
    "Jakarta": {"Bandung": 15000, "Surabaya": 35000, "Medan": 50000},
    "Bandung": {"Jakarta": 15000, "Surabaya": 30000, "Medan": 55000},
}

# --- Logika Menu ---
if menu == "Cek Tarif":
    st.subheader("📊 Hitung Estimasi Biaya")
    
    c1, c2 = st.columns(2)
    with c1:
        asal = st.selectbox("Kota Asal", list(TARIF_KOTA.keys()))
    with c2:
        tujuan = st.selectbox("Kota Tujuan", ["Jakarta", "Bandung", "Surabaya", "Medan"])
    
    berat = st.number_input("Berat Paket (kg)", min_value=1.0, step=0.5)
    
    if st.button("Hitung Sekarang"):
        harga_per_kg = TARIF_KOTA.get(asal, {}).get(tujuan, 0)
        if harga_per_kg > 0:
            total = harga_per_kg * berat
            st.success(f"Estimasi Biaya: **Rp {total:,.0f}**")
        else:
            st.error("Rute belum tersedia.")

elif menu == "Tracking Resi":
    st.subheader("🔍 Lacak Kiriman")
    resi_input = st.text_input("Masukkan Nomor Resi")
    if st.button("Lacak"):
        if resi_input == "3G12345":
            st.info("📦 **Status:** Paket sedang dalam perjalanan (Transit - Jakarta)")
        else:
            st.warning("Resi tidak ditemukan.")

else:
    st.write("3G LOGISTICS adalah layanan jasa logistik modern berbasis teknologi.")








