import streamlit as st
import requests
import json
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# GANTI URL DI BAWAH INI DENGAN URL DEPLOY TERBARU BAPAK
API_URL = "https://script.google.com/macros/s/AKfycby3wvU4wURslcvwHRi7VVi7PYsdxT21yCtibIGsNr72YKJMH6xUGUTmxKC0oIQRn4zs5Q/exec"

# 2. FUNGSI AMBIL DATA
@st.cache_data(ttl=1)
def get_data():
    try:
        r = requests.get(f"{API_URL}?t={datetime.now().timestamp()}", timeout=15)
        return r.json() if r.status_code == 200 else []
    except:
        return []

# 3. PENGATURAN TAB (OTOMATIS)
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📄 CETAK INVOICE"

# Fungsi untuk pindah tab
def pindah_ke_invoice():
    st.session_state.active_tab = "📄 CETAK INVOICE"

# Membuat Tab
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

# --- TAB 2: TAMBAH DATA ---
with tab2:
    st.subheader("Input Data Pengiriman Baru")
    with st.form("form_input", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            v_tgl = st.date_input("Tanggal", datetime.now())
            v_cust = st.text_input("Nama Customer")
            v_desc = st.text_input("Keterangan Barang")
        with col2:
            v_orig = st.text_input("Asal (Origin)")
            v_dest = st.text_input("Tujuan (Destination)")
            col_a, col_b, col_c = st.columns(3)
            v_kol = col_a.text_input("Kolli")
            v_kg = col_b.text_input("Weight (Kg)")
            v_hrg = col_c.text_input("Harga Satuan")

        if st.form_submit_button("💾 SIMPAN DATA"):
            if v_cust and v_hrg:
                # Logika hitung total sederhana
                try:
                    h_num = int(''.join(filter(str.isdigit, v_hrg)))
                    w_num = int(''.join(filter(str.isdigit, v_kg))) if v_kg else 1
                    total_val = h_num * w_num
                except:
                    total_val = 0

                payload = {
                    "date": v_tgl.strftime("%Y-%m-%d"),
                    "customer": v_cust.upper(),
                    "description": v_desc.upper(),
                    "origin": v_orig.upper(),
                    "destination": v_dest.upper(),
                    "kolli": v_kol,
                    "harga": h_num,
                    "weight": f"{v_kg} Kg",
                    "total": total_val
                }
                
                res = requests.post(API_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("Data Berhasil Disimpan! Mengalihkan...")
                    st.cache_data.clear() # Hapus cache agar data baru masuk
                    st.rerun() # Refresh & pindah otomatis
                else:
                    st.error("Gagal Simpan ke Google Sheets")
            else:
                st.warning("Nama Customer dan Harga wajib diisi!")

# --- TAB 1: CETAK INVOICE ---
with tab1:
    st.subheader("Pilih Data Untuk Dicetak")
    data_sheets = get_data()
    
    if not data_sheets:
        st.info("Menunggu data dari Google Sheets... Jika sudah input, tunggu 2 detik.")
    else:
        # Ambil daftar nama customer untuk dropdown
        list_cust = [f"{d.get('customer', 'N/A')} - {d.get('date', '')}" for d in data_sheets[::-1]]
        pilihan = st.selectbox("PILIH DATA CUSTOMER", list_cust)
        
        st.write("---")
        st.write(f"### INVOICE UNTUK: {pilihan}")
        st.info("Tombol Download PDF akan muncul di sini sesuai desain A5 Bapak.")
        # (Di sini Bapak bisa teruskan kode desain Invoice PDF Bapak)
