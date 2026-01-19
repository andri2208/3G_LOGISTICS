import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN (Update Favicon)
st.set_page_config(
    page_title="3G Logistics", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", # Link ke file favicon Bapak
    layout="wide"
)

# --- TAMBAHAN 1: SESSION STATE UNTUK KONTROL TAB ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0 # Default ke tab Invoice

# GANTI DENGAN URL BARU HASIL DEPLOY TADI
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1, show_spinner=False)
def get_data():
    try:
        # Menambahkan nocache agar data selalu ditarik yang paling baru
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            all_data = response.json()
            
            # CEK: Jika data kosong, beri tahu sistem
            if not all_data:
                return []
                
            # CEK: Pastikan setiap baris punya kolom 'status' agar tidak error saat difilter
            for item in all_data:
                if 'status' not in item:
                    item['status'] = "Belum Bayar" # Isi otomatis jika kosong
            
            return all_data
        else:
            return []
    except Exception as e:
        return []

# --- CSS: HEADER AMAN & TAMPILAN BERSIH ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .block-container { padding-top: 4rem !important; }
    .custom-header { text-align: left; /* PINDAH KE KIRI */ margin-bottom: 20px; }
    .custom-header img { width: 100%; max-width: 500px; height: auto; border-radius: 8px; }
    .stWidgetLabel p { font-weight: 900 !important; font-size: 14px !important; color: #1A2A3A !important; }
    .stTextInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #BCC6CC !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold !important; }
    /* Menyembunyikan indikator running di pojok kanan atas */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* MENGHILANGKAN TULISAN RUNNING GET_DATA */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* CSS Bapak yang sebelumnya tetap dipertahankan di bawah ini */
    .stApp { background-color: #FDFCF0; }
    .custom-header { text-align: left; margin-bottom: 20px; }
    .custom-header img { width: 100%; max-width: 400px; height: auto; border-radius: 8px; }
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# (Fungsi extract_number dan terbilang tetap sama seperti kode Bapak)
def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', '').replace('Kg', '').replace('kg', ''))
    if match: return float(match[0])
    return 0

def terbilang(n):
    bil = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return " Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return " Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return ""

# --- TAMBAHAN 2: GUNAKAN SESSION STATE PADA TABS ---
# Ini agar Streamlit tahu tab mana yang harus dibuka saat rerun
tab_list = ["📄 CETAK INVOICE", "➕ TAMBAH DATA"]
tab1, tab2 = st.tabs(tab_list)

with tab1:
    df = get_data() 

    # --- KODE CSS TETAP SAMA (UNTUK MERAPATKAN JARAK) ---
    st.markdown("""
        <style>
        .stRadio > div { margin-top: -30px; }
        .stSelectbox { margin-top: -30px; }
        </style>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- PERBAIKAN LOGIKA AGAR TIDAK ATTRIBUTE ERROR ---
    import pandas as pd # Pastikan pandas sudah di-import

    # Cek apakah df benar-benar sebuah tabel (DataFrame)
    if isinstance(df, pd.DataFrame) and not df.empty:
        col_kiri, col_kanan = st.columns([1, 2])
        
        with col_kiri:
            v_stat = st.radio("", ["Semua", "Belum Bayar", "Lunas"], 
                              horizontal=True, label_visibility="collapsed")

        with col_kanan:
            # Filter berdasarkan status
            df_f = df[df['status'] == v_stat] if v_stat != "Semua" else df
            
            if not df_f.empty:
                v_cust = st.selectbox("", sorted(df_f['customer'].unique()), 
                                      label_visibility="collapsed")
            else:
                v_cust = None
                st.caption("Data Status ini Kosong")
    else:
        v_cust = None
        st.error("⚠️ Data tidak dapat dimuat. Pastikan Google Sheets tidak kosong dan koneksi internet stabil.")

    st.write("---")
        
with tab2:
    st.subheader("➕ Input Pengiriman Baru")
    
    # Gunakan form agar bisa di-reset sekaligus
    with st.form("input_form", clear_on_submit=True):
        # Baris 1: Tanggal & Nama
        col1, col2 = st.columns(2)
        with col1:
            v_tgl = st.date_input("Tanggal", value=datetime.now())
        with col2:
            v_cust = st.text_input("Nama Customer")

        # Baris 2: Keterangan Barang (Full Width)
        v_desc = st.text_input("Keterangan Barang")

        # Baris 3: Asal & Tujuan
        col3, col4 = st.columns(2)
        with col3:
            v_orig = st.text_input("Asal (Origin)")
        with col4:
            v_dest = st.text_input("Tujuan (Destination)")

        # Baris 4: Kolli, Harga, Berat
        col5, col6, col7 = st.columns(3)
        with col5:
            v_kol = st.text_input("Kolli")
        with col6:
            v_harga = st.text_input("Harga/KG")
        with col7:
            v_weight = st.text_input("Berat (KG)")

        # Baris 5: Status Pembayaran
        v_status = st.selectbox("Status Pembayaran", ["Belum Bayar", "Lunas"])

        # Tombol Simpan
        submit = st.form_submit_button("🚀 SIMPAN & BERSIHKAN")

        if submit:
            if not v_cust or not v_harga:
                st.error("Nama Customer dan Harga tidak boleh kosong!")
            else:
                # Proses Hitung
                h_num = float(v_harga) if v_harga else 0
                w_num = float(v_weight) if v_weight else 0
                total_db = h_num * w_num

                payload = {
                    "date": str(v_tgl), 
                    "customer": v_cust.upper(), 
                    "description": v_desc.upper(),
                    "origin": v_orig.upper(), 
                    "destination": v_dest.upper(), 
                    "kolli": v_kol,
                    "harga": h_num, 
                    "weight": w_num, 
                    "total": total_db,
                    "status": v_status
                }

                # Kirim ke Sheets
                try:
                    resp = requests.post(API_URL, json=payload)
                    if resp.status_code == 200:
                        st.success(f"Data {v_cust.upper()} Berhasil Disimpan!")
                        # Memicu aplikasi untuk refresh dan mengosongkan form
                        st.rerun() 
                    else:
                        st.error("Gagal simpan ke server.")
                except:
                    st.error("Koneksi Error.")













































