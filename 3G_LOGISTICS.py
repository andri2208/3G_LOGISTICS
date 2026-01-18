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
st.image("HEADER INVOICE.png", use_container_width=True)

# --- AMBIL URL API ---
try:
    API_URL = st.secrets["general"]["api_url"]
except:
    st.error("Pastikan 'api_url' sudah diisi di Secrets Streamlit Cloud!")
    st.stop()

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Data Monitoring", "📝 Buat Invoice"])

with tab1:
    st.subheader("Database Pengiriman")
    try:
        res = requests.get(API_URL)
        if res.status_code == 200:
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
    except:
        st.info("Belum ada data yang ditampilkan.")

with tab2:
    st.subheader("Form Input Invoice")
    
    # Form harus diakhiri dengan st.form_submit_button
    with st.form("my_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Tanggal otomatis sistem 
            tgl_otomatis = datetime.now().strftime("%d-%b-%Y")
            st.write(f"📅 **Tanggal:** {tgl_otomatis}")
            
            customer = st.text_input("Customer", placeholder="Contoh: PT HARVI") [cite: 3]
            produk = st.text_area("Produk Deskripsi", placeholder="Contoh: 3 UNIT CDD") [cite: 5]
            kolli = st.number_input("Kolli", min_value=0, step=1) [cite: 5]
            berat = st.text_input("Berat (Weight)", placeholder="Contoh: 20 Ton") [cite: 5]
            
        with col2:
            origin = st.text_input("Origin", value="TUAL") [cite: 5]
            destinasi = st.text_input("Destination", value="LARAT") [cite: 5]
            harga = st.number_input("Harga (Rp)", min_value=0, value=0, step=1000) [cite: 5]
            
            # Kalkulasi otomatis
            total_bayar = harga
            teks_terbilang = f"{terbilang(total_bayar)} Rupiah" if total_bayar > 0 else "-"
            
            st.write("---")
            st.write(f"💰 **Yang Harus Dibayar:** Rp {total_bayar:,.0f}") [cite: 5]
            st.write(f"🗣️ **Terbilang:** *{teks_terbilang}*") [cite: 6]

        # TOMBOL SUBMIT (Wajib ada di dalam blok 'with st.form')
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
                    # Kirim ke Apps Script
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("✅ Data Berhasil Disimpan!")
                        st.balloons()
                    else:
                        st.error("Gagal mengirim data.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- FOOTER ---
st.markdown("---")
st.image("STEMPEL TANDA TANGAN.png", width=150)
st.write("**KELVINITO JAYADI**") [cite: 16]
st.caption("DIREKTUR") [cite: 17]
