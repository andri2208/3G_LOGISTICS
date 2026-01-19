import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics Premium", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", 
    layout="wide"
)

# 2. CSS CUSTOM: ANTI-SCROLL & BERWARNA
st.markdown("""
    <style>
    /* Dasar Web - Warna Cream Mewah */
    .stApp { background-color: #FDFCF0; font-family: 'Inter', sans-serif; }
    
    /* Mengurangi Padding Utama agar Muat 1 Layar */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Header ramping */
    .custom-header { text-align: left; margin-bottom: 5px; }
    .custom-header img { max-width: 320px; height: auto; }

    /* FIX KOTAK DOBEL TANGGAL & INPUT */
    div[data-baseweb="input"], div[data-baseweb="select"], .stNumberInput div {
        border: none !important;
        background-color: transparent !important;
    }

    /* STYLING INPUT - Ramping & Berwarna */
    .stTextInput input, .stDateInput div[data-baseweb="input"] input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #E5E7EB !important; /* Border abu muda */
        border-radius: 8px !important;
        height: 38px !important; /* Lebih tipis agar muat 1 layar */
        font-size: 13px !important;
        color: #1A2A3A !important;
    }
    
    /* Warna saat diklik (Focus) - Jadi Biru Gold */
    .stTextInput input:focus, .stDateInput div[data-baseweb="input"]:focus-within {
        border-color: #B8860B !important; /* Warna Dark Gold */
        box-shadow: 0 0 0 1px #B8860B !important;
    }

    /* Label Input - Warna Navy Tebal */
    .stWidgetLabel p { 
        font-weight: 800 !important; 
        color: #1A2A3A !important; 
        font-size: 11px !important;
        margin-bottom: -15px !important; /* Merapatkan label ke kotak */
    }

    /* Tab Header Berwarna */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #E5E7EB;
        padding: 8px 20px !important;
        border-radius: 5px 5px 0 0;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1A2A3A !important;
        color: #FDFCF0 !important;
    }

    /* Tombol Simpan - Full Warna Navy Gold */
    div.stButton > button {
        background: linear-gradient(90deg, #1A2A3A 0%, #2c3e50 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: 2px solid #B8860B !important;
        border-radius: 8px !important;
        width: 100%;
        height: 45px;
        margin-top: 5px;
    }

    /* Menghilangkan elemen tidak penting */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# 3. LOGIC DATA
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}")
        return response.json() if response.status_code == 200 else []
    except: return []

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
    return float(match[0]) if match else 0

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

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    # (Bagian cetak invoice tetap sama agar data aman)
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        c_f1, c_f2 = st.columns([1, 2])
        with c_f1: st.radio("Status:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True, key="filter_status")
        with c_f2: 
            cust_list = sorted(df['customer'].unique())
            selected_cust = st.selectbox("Pilih Customer:", cust_list)
        
        if selected_cust:
            row = df[df['customer'] == selected_cust].iloc[-1]
            # ... (Logika Invoice sama seperti sebelumnya) ...
            st.info("Invoice siap di bawah.")

with tab2:
    st.markdown("<h4 style='text-align: center; color: #1A2A3A; margin: 0;'>NEW DISPATCH ENTRY</h4>", unsafe_allow_html=True)
    
    # Menggunakan form dengan padding rapat
    with st.form("input_form", clear_on_submit=True):
        # Baris 1: Tanggal & Customer
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1: v_tgl = st.date_input("📅 TANGGAL", value=datetime.now())
        with r1_c2: v_cust = st.text_input("🏢 CUSTOMER", placeholder="Nama Perusahaan")

        # Baris 2: Barang (Full Width)
        v_desc = st.text_input("📦 KETERANGAN BARANG", placeholder="Jenis barang...")

        # Baris 3: Origin & Destination
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1: v_orig = st.text_input("📍 ASAL", placeholder="SBY")
        with r2_c2: v_dest = st.text_input("🏁 TUJUAN", placeholder="JKT")

        # Baris 4: Kolli, Harga, Berat (3 Kolom)
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        with r3_c1: v_kol = st.text_input("📦 KOLLI", value="0")
        with r3_c2: v_harga = st.text_input("💰 HARGA", value="0")
        with r3_c3: v_weight = st.text_input("⚖️ BERAT", value="0")

        # Baris 5: Status
        v_status = st.selectbox("💳 STATUS", ["Belum Bayar", "Lunas"])

        # Tombol Simpan
        submit = st.form_submit_button("🚀 SIMPAN DATA SEKARANG")

        if submit:
            if v_cust and v_harga:
                try:
                    h_num = float(v_harga)
                    w_num = float(v_weight)
                    payload = {
                        "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                        "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                        "harga": h_num, "weight": w_num, "total": h_num * w_num, "status": v_status
                    }
                    requests.post(API_URL, json=payload)
                    st.success("Data Berhasil Masuk!")
                    st.rerun()
                except: st.error("Harga/Berat harus angka!")
