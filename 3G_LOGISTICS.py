import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 2. CSS FINAL: ZERO EMPTY BOX & PERFECT PRECISION ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Hapus paksa semua container kosong bawaan Streamlit */
    [data-testid="stVerticalBlock"] > div {{
        padding: 0px !important;
        margin: 0px !important;
    }}
    
    /* Hilangkan background kotak abu-abu/transparan yang mengganggu */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }}

    .stApp {{ 
        background: linear-gradient(135deg, #052222 0%, #000000 100%); 
    }}

    /* Container Utama di Tengah Atas */
    .main-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        padding-top: 60px;
    }}

    .logo-img {{
        width: 200px;
        margin-bottom: 5px;
    }}

    .title-text {{
        color: white;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 25px;
        font-family: 'Inter', sans-serif;
    }}

    /* Input Password Super Presisi */
    div[data-baseweb="input"] {{
        width: 280px !important;
        margin: 0 auto !important;
        border: none !important;
    }}

    .stTextInput > div > div > input {{
        text-align: center !important;
        background-color: #f0f2f6 !important;
        color: #000 !important;
        border-radius: 5px !important;
        height: 42px !important;
        font-size: 16px !important;
        border: none !important;
    }}

    /* Tombol Masuk Merah Padat */
    .stButton > button {{
        background-color: #cc0000 !important;
        color: white !important;
        width: 280px !important;
        border-radius: 5px !important;
        border: none !important;
        height: 45px !important;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 15px;
        transition: 0.3s;
    }}

    .stButton > button:hover {{
        background-color: #ff0000 !important;
        box-shadow: 0px 4px 15px rgba(255, 0, 0, 0.3);
    }}

    /* Sembunyikan Header & Footer Streamlit */
    header, footer, .stDeployButton {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Menggunakan HTML murni untuk membungkus agar tidak ada elemen 'ghost' dari Streamlit
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    
    st.markdown('<div class="title-text">3G LOGISTICS LOGIN</div>', unsafe_allow_html=True)
    
    # Input Password
    pwd = st.text_input("PWD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
    
    # Tombol Authenticate
    if st.button("MASUK SISTEM"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Akses Ditolak!")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DASHBOARD & DATASET (SAMA DENGAN SEBELUMNYA) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

# Tambahkan Fungsi Terbilang, Cetak PDF, dan Tab Input di sini...
st.success("Akses Diberikan. Selamat Datang di Dashboard.")

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()
