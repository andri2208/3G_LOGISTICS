import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", page_icon="FAVICON.png", layout="wide")

# --- FUNGSI TERBILANG INDONESIA ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12:
        return bilangan[int(n)]
    elif n < 20:
        return terbilang(n - 10) + " Belas"
    elif n < 100:
        return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        return "Seratus " + terbilang(n - 100)
    elif n < 1000:
        return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        return "Seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return "Angka Terlalu Besar"

# --- TAMPILAN HEADER ---
# Memastikan header invoice muncul di paling atas [cite: 1, 4]
st.image("HEADER INVOICE.png", use_container_width=True)

# --- AMBIL URL API DARI SECRETS ---
try:
    API_URL = st.secrets["general"]["api_url"]
except Exception:
    st.error("Error: Masukkan 'api_url' di Settings > Secrets Streamlit Cloud!")
    st.stop()

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Data Monitoring", "📝 Buat Invoice"])

with tab1:
    st.subheader("Database Pengiriman")
    try:
        res = requests.get(API_URL)
        if res.status_code == 200:
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
    except Exception:
        st.info("Koneksi ke Google Sheets belum tersedia.")

with tab2:
    st.subheader("Form Input Invoice")
    
    with st.form("invoice_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Tanggal otomatis sistem hari ini [cite: 5, 13]
            tgl_otomatis = datetime.now().strftime("%d-%b-%Y")
            st.info(f"📅 Tanggal Sistem: {tgl_otomatis}")
            
            # Input data customer dan produk [cite: 3, 5]
            customer = st.text_input("Customer", placeholder="Contoh: PT HARVI")
            produk = st.text_area("Produk Deskripsi", placeholder="Contoh: 3 UNIT CDD")
            kolli = st.number_input("Kolli", min_value=0, step=1)
            berat = st.text_input("Berat (Weight)", placeholder="Contoh: 20 Ton")
            
        with col2:
            # Input rute pengiriman 
            origin = st.text_input("Origin", value="TUAL")
            destinasi = st.text_input("Destination", value="LARAT")
            harga = st.number_input("Harga (Rp)", min_value=0, value=0, step=1000)
            
            # Kalkulasi otomatis untuk pembayaran 
            total_bayar = harga
            teks_terbilang = f"{terbilang(total_bayar)} Rupiah" if total_bayar > 0 else "-"
            
            st.markdown("---")
            st.markdown(f"**YANG HARUS DIBAYAR:**")
            st.subheader(f"Rp {total_bayar:,.0f}")
            st.write(f"*Terbilang: {teks_terbilang}*")

        # Tombol untuk mengirim data ke Google Sheets
        submitted = st.form_submit_button("Simpan & Kirim Invoice")

        if submitted:
            if not customer or harga == 0:
                st.warning("Mohon isi Nama Customer dan Harga!")
            else:
                payload = {
                    "tanggal": tgl_otomatis,
                    "customer": customer,
                    "produk": produk,
                    "origin": origin,
                    "destinasi": destinasi,
                    "kolli": kolli,
                    "berat": berat,
                    "harga": total_bayar,
                    "terbilang": teks_terbilang
                }
                
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("✅ Data Berhasil Disimpan!")
                        st.balloons()
                    else:
                        st.error("Gagal mengirim data ke Google Sheets.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- FOOTER ---
# Bagian tanda tangan direktur [cite: 15, 16, 17]
st.markdown("---")
st.write("Sincerely,")
st.image("STEMPEL TANDA TANGAN.png", width=150)
st.write("**KELVINITO JAYADI**")
st.caption("DIREKTUR")
