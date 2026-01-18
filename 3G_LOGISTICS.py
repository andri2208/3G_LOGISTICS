import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - Sistem Invoice", page_icon="FAVICON.png", layout="wide")

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
    st.error("Error: Pastikan 'api_url' sudah diisi di Secrets Streamlit Cloud!")
    st.stop()

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Monitoring Data", "📝 Buat Invoice Baru"])

with tab1:
    st.subheader("Data Pengiriman Terdaftar")
    try:
        res = requests.get(API_URL)
        if res.status_code == 200:
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
    except:
        st.info("Menunggu data dari Google Sheets...")

with tab2:
    st.subheader("Form Input Invoice")
    
    with st.form("invoice_form"):
        # Penentuan Tanggal Otomatis
        tgl_skrng = datetime.now()
        tgl_format = tgl_skrng.strftime("%d/%m/%Y") 
        tgl_load_format = tgl_skrng.strftime("%d-%b-%y") 
        
        st.info(f"📅 DATE : {tgl_format}")
        
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("CUSTOMER", placeholder="Contoh: BAPAK ANDI")
            produk = st.text_input("Product Description", placeholder="Contoh: SATU SET ALAT TAMBANG")
            origin = st.text_input("Origin", value="SBY")
            destination = st.text_input("Destination", value="MEDAN")
            
        with col2:
            kolli = st.text_input("KOLLI", placeholder="Contoh: 1")
            weight = st.text_input("WEIGHT", placeholder="Contoh: 290 Kg")
            total_bayar = st.number_input("HARGA / TOTAL BAYAR (Rp)", min_value=0, value=0, step=1000)
            
        # Terbilang Otomatis dari Total Bayar
        teks_terbilang = f"{terbilang(total_bayar)} rupiah" if total_bayar > 0 else ""
        
        st.markdown("---")
        st.markdown("**YANG HARUS DI BAYAR:**")
        st.subheader(f"Rp {total_bayar:,.0f}")
        st.write(f"**Terbilang :** *{teks_terbilang.lower()}*")

        submitted = st.form_submit_button("Simpan Data Invoice")

        if submitted:
            if not customer or total_bayar == 0:
                st.warning("Nama Customer dan Harga tidak boleh kosong!")
            else:
                payload = {
                    "date": tgl_format,
                    "date_load": tgl_load_format,
                    "customer": customer.upper(),
                    "description": produk.upper(),
                    "origin": origin.upper(),
                    "destination": destination.upper(),
                    "kolli": kolli,
                    "weight": weight,
                    "total": total_bayar,
                    "terbilang": teks_terbilang.lower()
                }
                
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("✅ Data Invoice Berhasil Disimpan!")
                        st.balloons()
                    else:
                        st.error("Gagal mengirim data. Cek Deployment Apps Script Anda.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- FOOTER ---
st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])
with col_f2:
    st.write("Sincerely,")
    st.image("STEMPEL TANDA TANGAN.png", width=150)
    st.write("**KELVINITO JAYADI**")
    st.caption("DIREKTUR")
