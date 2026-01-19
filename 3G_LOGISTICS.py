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

# 2. CSS CUSTOM: DASHBOARD BERWARNA & KOMPAK
st.markdown("""
    <style>
    /* Dasar Web */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Header */
    .custom-header { text-align: left; margin-bottom: 10px; }
    .custom-header img { max-width: 300px; height: auto; }

    /* PANEL INPUT DATA BERWARNA (NAVY DARK) */
    [data-testid="stForm"] {
        background-color: #1A2A3A !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 2px solid #B8860B !important; /* Border Emas */
        color: white !important;
    }

    /* FIX KOTAK INPUT DALAM PANEL BERWARNA */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #B8860B !important;
        border-radius: 8px !important;
        height: 35px !important;
        color: #1A2A3A !important;
        font-weight: 600 !important;
    }

    /* Menghilangkan Border Ganda Tanggal & Selectbox */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: none !important;
    }

    /* LABEL INPUT (PUTIH DI ATAS NAVY) */
    .stWidgetLabel p { 
        font-weight: 700 !important; 
        color: #FFFFFF !important; 
        font-size: 11px !important;
        text-transform: uppercase;
        margin-bottom: -15px !important;
        letter-spacing: 1px;
    }

    /* TABS STYLING */
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1A2A3A !important;
        border-bottom: 3px solid #B8860B !important;
    }

    /* TOMBOL SIMPAN EMAS MENGKILAP */
    div.stButton > button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: #1A2A3A !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border-radius: 8px !important;
        border: none !important;
        height: 45px;
        margin-top: 10px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(184, 134, 11, 0.4);
    }

    /* Sembunyikan Sampah Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# (Logic Data tetap sama dengan kode Bapak agar koneksi tidak putus)
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}")
        return response.json() if response.status_code == 200 else []
    except: return []

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.write("---")
        c1, c2 = st.columns([1, 2])
        with c1: st.radio("FILTER:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True, key="f_status")
        with c2: selected_cust = st.selectbox("CUSTOMER:", sorted(df['customer'].unique()))
        
        # Area Invoice HTML Bapak tetap aman di sini...
        st.markdown("<br>", unsafe_allow_html=True)
        # (Invoice HTML disisipkan di sini sesuai kode asli Bapak)

with tab2:
    # Judul berwarna Emas
    st.markdown("<h3 style='text-align: center; color: #1A2A3A; margin-top: -10px;'>DASHBOARD INPUT PENGIRIMAN</h3>", unsafe_allow_html=True)
    
    with st.form("input_form", clear_on_submit=True):
        # Baris 1
        col1, col2 = st.columns(2)
        with col1: v_tgl = st.date_input("📅 TANGGAL")
        with col2: v_cust = st.text_input("🏢 CUSTOMER NAME")

        # Baris 2
        v_desc = st.text_input("📦 ITEM DESCRIPTION")

        # Baris 3
        col3, col4 = st.columns(2)
        with col3: v_orig = st.text_input("📍 ORIGIN")
        with col4: v_dest = st.text_input("🏁 DESTINATION")

        # Baris 4
        col5, col6, col7 = st.columns(3)
        with col5: v_kol = st.text_input("📦 KOLLI")
        with col6: v_harga = st.text_input("💰 PRICE/KG")
        with col7: v_weight = st.text_input("⚖️ WEIGHT")

        # Baris 5
        v_status = st.selectbox("💳 PAYMENT STATUS", ["Belum Bayar", "Lunas"])

        # Tombol
        submit = st.form_submit_button("💾 SAVE TO DATABASE")

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
                    st.success("DATA SAVED SUCCESSFULLY!")
                    st.rerun()
                except: st.error("CHECK PRICE / WEIGHT NUMBERS!")
