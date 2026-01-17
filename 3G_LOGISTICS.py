import streamlit as st
from PIL import Image
import os

# 1. Konfigurasi Halaman & Favicon (Ikon Tab Browser)
try:
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚")

# 2. Menampilkan Header Invoice di bagian paling atas
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)
else:
    st.title("🚚 3G LOGISTICS")

# 3. Sidebar dengan Logo
with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=100)
    st.title("Menu Utama")
    menu = st.radio("Pilih Layanan:", ["Cek Tarif", "Tracking Resi", "Kontak"])

# --- Database Tarif (Bisa kamu tambah sesuai kebutuhan) ---
TARIF_KOTA = {
    "JAKARTA": {"BANDUNG": 15000, "SURABAYA": 35000, "MEDAN": 50000},
    "BANDUNG": {"JAKARTA": 15000, "SURABAYA": 30000, "MEDAN": 55000},
}

# 4. Logika Menu
if menu == "Cek Tarif":
    st.subheader("📊 Estimasi Biaya Pengiriman")
    
    col1, col2 = st.columns(2)
    with col1:
        asal = st.selectbox("Kota Asal", list(TARIF_KOTA.keys())).upper()
    with col2:
        tujuan = st.selectbox("Kota Tujuan", ["JAKARTA", "BANDUNG", "SURABAYA", "MEDAN"]).upper()
    
    berat = st.number_input("Berat Paket (Kg)", min_value=1, value=1)
    
    if st.button("Cek Harga"):
        harga = TARIF_KOTA.get(asal, {}).get(tujuan, 0)
        if harga > 0:
            total = harga * berat
            st.success(f"### Total Biaya: Rp {total:,.0f}")
            st.caption(f"Tarif dasar: Rp {harga:,.0f}/Kg")
        else:
            st.error("Rute pengiriman belum tersedia.")

elif menu == "Tracking Resi":
    st.subheader("🔍 Lacak Posisi Paket")
    resi = st.text_input("Masukkan Nomor Resi (Contoh: 3G001)")
    if st.button("Lacak"):
        if resi:
            st.info(f"Paket dengan resi **{resi}** sedang dalam proses pengantaran.")
        else:
            st.warning("Silakan masukkan nomor resi.")

else:
    st.subheader("📞 Kontak Kami")
    st.write("PT. GAMA GEMAH GEMILANG")
    st.write("Hubungi kami untuk kerja sama logistik lebih lanjut.")
