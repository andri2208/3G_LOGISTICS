import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - LOGIN", page_icon="🚚", layout="wide")

# API & PASSWORD
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 2. CSS CUSTOM (EMERALD & CENTERED) ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Background Emerald Gelap */
    .stApp {{ 
        background: linear-gradient(135deg, #062c2c 0%, #101010 100%); 
    }}
    
    /* Container Utama untuk Menengahkan */
    .login-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 85vh;
        width: 100%;
    }}

    /* Card Login Tanpa Kotak Kosong */
    .login-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        width: 100%;
        max-width: 380px; /* Card Mungil */
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }}
    
    /* Logo */
    .logo-img {{
        width: 220px;
        margin-bottom: 20px;
    }}

    /* Menghilangkan label input dan mengecilkan kotak password */
    div[data-baseweb="input"] {{
        width: 100% !important;
        max-width: 280px !important;
        margin: 0 auto !important;
    }}

    .stTextInput > div > div > input {{
        text-align: center !important;
        border-radius: 8px !important;
        height: 40px !important;
        font-size: 14px !important;
    }}

    /* Tombol Masuk */
    .stButton > button {{
        background: #cc0000 !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100% !important;
        max-width: 280px !important;
        height: 40px !important;
        font-weight: bold;
        border: none;
        margin-top: 15px;
        transition: 0.3s;
    }}

    .stButton > button:hover {{
        background: #ff0000 !important;
        transform: scale(1.02);
    }}
    
    /* Sembunyikan elemen bawaan Streamlit */
    header, footer, .stDeployButton {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Wrapper untuk memastikan posisi di tengah layar
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Menampilkan Logo
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    
    st.markdown("<h4 style='color:white; margin-bottom:20px;'>3G LOGISTICS LOGIN</h4>", unsafe_allow_html=True)
    
    # Form Login mungil
    pwd = st.text_input("PASSWORD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
    
    if st.button("MASUK SISTEM"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Kode Salah!")
            
    st.markdown('</div>', unsafe_allow_html=True) # Tutup card
    st.markdown('</div>', unsafe_allow_html=True) # Tutup container
    st.stop()

# --- 4. DASHBOARD (SAMA SEPERTI SEBELUMNYA) ---
# Tambahkan fungsi terbilang, render_pdf, dan tab input di bawah sini
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

# Notifikasi sukses yang elegan
st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; margin-bottom: 20px;">
        <p style="color: white; margin: 0; font-weight: bold;">✅ Login Berhasil! Selamat Datang di Dashboard.</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()

st.title("🚀 Dashboard 3G Logistics")
# ... lanjutkan tab input Anda ...
