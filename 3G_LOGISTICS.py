import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI ---
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS",
    page_icon="🚚", 
    layout="wide"
)

# --- 2. FUNGSI ENCODE GAMBAR ---
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. CSS LUXURY MINIMALIST (ANTI KOTAK KOSONG) ---
st.markdown(f"""
    <style>
    /* Background Premium Dark */
    .stApp {{
        background: linear-gradient(145deg, #4b0000 0%, #000000 100%);
    }}

    /* Container Login */
    .login-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 85vh;
    }}

    /* Card Login Transparan */
    .login-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 40px;
        width: 100%;
        max-width: 450px;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }}

    /* Logo Styling */
    .login-logo {{
        width: 100%;
        max-width: 320px;
        margin-bottom: 30px;
    }}

    /* Input Password */
    .stTextInput>div>div>input {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 45px !important;
        text-align: center;
        font-size: 18px !important;
        border: none !important;
    }}

    /* Button Sign In */
    .stButton>button {{
        background: #ffffff !important;
        color: #4b0000 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        width: 100%;
        height: 45px !important;
        margin-top: 20px;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background: #ff0000 !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(255,0,0,0.4);
    }}

    /* Hilangkan Elemen Sampah */
    header, footer, #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Pastikan file logo Anda dinamai FAVICON.png atau sesuaikan di sini
    logo_file = "FAVICON.png" 
    logo_b64 = get_base64_img(logo_file)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="login-logo">', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color:white;'>3G LOGISTICS</h1>", unsafe_allow_html=True)
    
    pwd = st.text_input("PASSWORD", type="password", placeholder="ENTER ACCESS CODE", label_visibility="collapsed")
    
    if st.button("AUTHENTICATE"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Code")
            
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD (SAMA SEPERTI SEBELUMNYA) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

c1, c2 = st.columns([0.8, 0.2])
with c1:
    logo_dash = get_base64_img("FAVICON.png")
    if logo_dash:
        st.markdown(f'<img src="data:image/png;base64,{logo_dash}" style="width:200px;">', unsafe_allow_html=True)
with c2:
    st.write("##")
    if st.button("LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# TAB & FUNGSI LAINNYA LANJUTKAN DI SINI...
st.info("Selamat Datang di Panel Dashboard PT. Gama Gemah Gemilang")
