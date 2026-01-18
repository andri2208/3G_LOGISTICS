import streamlit as st
import requests
from datetime import datetime

# --- FUNGSI TERBILANG OTOMATIS ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12:
        return bilangan[n]
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

# --- TAMPILAN FORM ---
with st.form("invoice_form", clear_on_submit=True):
    st.subheader("📝 Input Invoice Baru")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tanggal Otomatis dari Sistem 
        tgl_skrng = datetime.now()
        st.info(f"Tanggal Hari Ini: {tgl_skrng.strftime('%d-%b-%Y')}")
        
        customer = st.text_input("Customer", placeholder="Contoh: PT HARVI") [cite: 3]
        produk = st.text_area("Product Description", placeholder="Contoh: 3 UNIT CDD") [cite: 5]
        kolli = st.number_input("KOLLI", min_value=0, step=1) [cite: 5]
        berat = st.text_input("WEIGHT", placeholder="Contoh: 10 Ton atau -") [cite: 5]
        
    with col2:
        origin = st.text_input("Origin", value="TUAL") [cite: 5]
        destination = st.text_input("Destination", value="LARAT") [cite: 5]
        harga = st.number_input("Harga Satuan (Rp)", min_value=0, value=0, step=1000) [cite: 5]
        
        # Kalkulasi Otomatis: Yang Harus Dibayar 
        total_bayar = harga # Anda bisa ubah menjadi (harga * kolli) jika diperlukan
        st.markdown(f"**YANG HARUS DIBAYAR:**")
        st.subheader(f"Rp {total_bayar:,.0f}")
        
        # Terbilang Otomatis 
        hasil_terbilang = f"{terbilang(total_bayar)} Rupiah" if total_bayar > 0 else "-"
        st.write(f"*Terbilang: {hasil_terbilang}*")

    submitted = st.form_submit_button("Simpan & Kirim Invoice")

    if submitted:
        payload = {
            "date": tgl_skrng.strftime("%d-%b-%Y"),
            "customer": customer,
            "description": produk,
            "origin": origin,
            "destination": destination,
            "kolli": kolli,
            "weight": berat,
            "total": total_bayar,
            "terbilang": hasil_terbilang
        }
        
        # Mengirim ke Apps Script
        try:
            res = requests.post(st.secrets["general"]["api_url"], json=payload)
            if res.status_code == 200:
                st.success("✅ Invoice Berhasil Dicatat!")
            else:
                st.error("Gagal mengirim ke Google Sheets.")
        except Exception as e:
            st.error(f"Error: {e}")
