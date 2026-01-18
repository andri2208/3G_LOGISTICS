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

# --- 2. DEEP CLEAN CSS (ANTI KOTAK KOSONG) ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* 1. Hapus Background & Border Bawaan Streamlit secara Total */
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlock"] > div {{
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        gap: 0 !important;
    }}

    /* 2. Background Utama */
    .stApp {{ 
        background: linear-gradient(135deg, #052222 0%, #000000 100%); 
    }}

    /* 3. Wrapper Utama untuk Presisi */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-top: 80px; /* Atur jarak dari atas layar di sini */
        width: 100%;
    }}

    .logo-container {{
        margin-bottom: 20px;
    }}

    /* 4. Teks Brand */
    .brand-title {{
        color: white;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }}

    /* 5. Styling Input Password agar Mungil & Clean */
    div[data-baseweb="input"] {{
        width: 300px !important;
        margin: 0 auto !important;
    }}

    .stTextInput > div > div > input {{
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
        height: 45px !important;
        text-align: center !important;
        font-size: 16px !important;
        border: 2px solid transparent !important;
    }}

    /* 6. Tombol Masuk Merah Menyala */
    .stButton > button {{
        background: #cc0000 !important;
        color: white !important;
        width: 300px !important;
        border-radius: 8px !important;
        height: 45px !important;
        font-weight: bold;
        border: none !important;
        margin-top: 20px !important;
        cursor: pointer;
    }}

    /* 7. Hilangkan Header & Footer Streamlit */
    header, footer, .stDeployButton, [data-testid="stHeader"] {{
        visibility: hidden;
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Menggunakan wrapper HTML murni agar tidak terpengaruh grid Streamlit
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    # Logo Section
    if logo_b64:
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" width="220"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="brand-title">3G LOGISTICS LOGIN</div>', unsafe_allow_html=True)
    
    # Elemen Input
    # Gunakan container kosong agar CSS kita bisa menargetkan dengan tepat
    pwd = st.text_input("PASSWORD", type="password", placeholder="MASUKKAN KODE AKSES", label_visibility="collapsed")
    
    if st.button("AUTHENTICATE SYSTEM"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Kode Akses Salah")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DASHBOARD (MUNCUL JIKA SUDAH LOGIN) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

# Lanjutkan dengan Tab Input dan Database seperti sebelumnya...
st.success("Login Berhasil.")
if st.sidebar.button("LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()
