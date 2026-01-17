import streamlit as st

# Konfigurasi Halaman
st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚")

# Header
st.title("🚚 3G LOGISTICS")
st.markdown("### Solusi Pengiriman Cepat & Terpercaya")
st.divider()

# Sidebar untuk Navigasi
menu = st.sidebar.selectbox("Pilih Menu", ["Cek Tarif", "Tracking Resi", "Tentang Kami"])

# Database Sederhana (Bisa dikembangkan nanti)
TARIF_KOTA = {
    "Jakarta": {"Bandung": 15000, "Surabaya": 35000, "Medan": 50000},
    "Bandung": {"Jakarta": 15000, "Surabaya": 30000, "Medan": 55000},
}

if menu == "Cek Tarif":
    st.subheader("📊 Hitung Estimasi Biaya")
    
    col1, col2 = st.columns(2)
    with col1:
        asal = st.selectbox("Kota Asal", list(TARIF_KOTA.keys()))
    with col2:
        tujuan = st.selectbox("Kota Tujuan", ["Jakarta", "Bandung", "Surabaya", "Medan"])
    
    berat = st.number_input("Berat Paket (kg)", min_value=1.0, step=0.5)
    
    if st.button("Hitung Sekarang"):
        # Logika hitung tarif
        harga_per_kg = TARIF_KOTA.get(asal, {}).get(tujuan, 0)
        
        if harga_per_kg > 0:
            total = harga_per_kg * berat
            st.success(f"Estimasi Biaya: **Rp {total:,.0f}**")
            st.info(f"Tarif per kg: Rp {harga_per_kg:,.0f}")
        else:
            st.error("Maaf, rute pengiriman belum tersedia.")

elif menu == "Tracking Resi":
    st.subheader("🔍 Lacak Kiriman")
    resi_input = st.text_input("Masukkan Nomor Resi")
    
    if st.button("Lacak"):
        if resi_input == "3G12345": # Contoh simulasi
            st.write("📦 **Status:** Paket sedang dalam perjalanan (Transit - Jakarta)")
        else:
            st.warning("Nomor resi tidak ditemukan. Silakan cek kembali.")

else:
    st.write("3G LOGISTICS adalah layanan jasa logistik modern berbasis teknologi.")
