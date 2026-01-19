import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics Pro", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", 
    layout="wide"
)

# 2. CSS CUSTOM: FULL COLOR DENGAN TEKS PUTIH TERANG
st.markdown("""
    <style>
    /* Dasar Web */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* PANEL INPUT DATA (NAVY DARK) */
    [data-testid="stForm"] {
        background-color: #1A2A3A !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 2px solid #B8860B !important; 
    }

    /* LABEL INPUT (SEKARANG PUTIH TERANG & TEBAL) */
    .stWidgetLabel p { 
        font-weight: 800 !important; 
        color: #FFFFFF !important; /* Teks Label Putih */
        font-size: 13px !important;
        text-transform: uppercase;
        margin-bottom: -10px !important;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5); /* Biar makin tegas */
    }

    /* KOTAK INPUT (PUTIH BERSIH) */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #B8860B !important;
        border-radius: 8px !important;
        height: 40px !important;
        color: #000000 !important; /* Teks di dalam kotak Hitam Pekat */
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    /* Perbaikan Khusus Input Tanggal & Selectbox agar teksnya Hitam */
    div[data-baseweb="input"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Menghilangkan Border Ganda */
    div[data-baseweb="input"], div[data-baseweb="select"] { border: none !important; }

    /* TOMBOL SIMPAN EMAS */
    div.stButton > button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: #1A2A3A !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border-radius: 8px !important;
        height: 50px;
        width: 100%;
        border: none !important;
        margin-top: 15px;
    }

    /* Header & Tabs */
    .custom-header { text-align: left; margin-bottom: 10px; }
    .custom-header img { max-width: 280px; height: auto; }
    .stTabs [aria-selected="true"] { color: #1A2A3A !important; border-bottom: 3px solid #B8860B !important; }
    
    #MainMenu, footer, header {visibility: hidden;}
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

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab2:
    st.markdown("<h3 style='text-align: center; color: #1A2A3A; margin-top: -10px;'>DASHBOARD INPUT PENGIRIMAN</h3>", unsafe_allow_html=True)
    
    with st.form("input_form", clear_on_submit=True):
        # Baris 1
        col1, col2 = st.columns(2)
        with col1: v_tgl = st.date_input("📅 TANGGAL PENGIRIMAN")
        with col2: v_cust = st.text_input("🏢 NAMA CUSTOMER")

        # Baris 2
        v_desc = st.text_input("📦 KETERANGAN BARANG")

        # Baris 3
        col3, col4 = st.columns(2)
        with col3: v_orig = st.text_input("📍 ASAL (ORIGIN)")
        with col4: v_dest = st.text_input("🏁 TUJUAN (DESTINATION)")

        # Baris 4
        col5, col6, col7 = st.columns(3)
        with col5: v_kol = st.text_input("📦 JUMLAH KOLLI")
        with col6: v_harga = st.text_input("💰 HARGA PER KG")
        with col7: v_weight = st.text_input("⚖️ BERAT TOTAL")

        # Baris 5
        v_status = st.selectbox("💳 STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])

        # Tombol
        submit = st.form_submit_button("🚀 SIMPAN DATA KE GOOGLE SHEETS")

        if submit:
            if v_cust and v_harga:
                try:
                    payload = {
                        "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                        "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                        "harga": float(v_harga), "weight": float(v_weight), 
                        "total": float(v_harga) * float(v_weight), "status": v_status
                    }
                    requests.post(API_URL, json=payload)
                    st.success("DATA BERHASIL DISIMPAN!")
                    st.rerun()
                except: st.error("HARGA & BERAT HARUS ANGKA!")
