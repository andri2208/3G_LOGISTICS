import streamlit as st
import os
import base64

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_img("FAVICON.png")

# --- CSS DEEP CLEAN (MENGHAPUS SEMUA KOTAK BAWAAN) ---
st.markdown(f"""
    <style>
    /* Menghilangkan paksa semua padding dan border container Streamlit */
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}

    .stApp {{ 
        background: #052222; /* Warna solid agar tidak ada distorsi gradasi */
    }}

    /* Container Login Utama */
    .login-frame {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 100px;
        width: 100%;
        height: 100vh;
    }}

    .logo-img {{
        width: 220px;
        margin-bottom: 20px;
    }}

    .login-title {{
        color: white;
        font-family: Arial, sans-serif;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 30px;
    }}

    /* Memaksa input password Streamlit menjadi kecil */
    div[data-baseweb="input"] {{
        width: 300px !important;
        margin: 0 auto !important;
    }}

    /* Menghilangkan header & footer */
    header, footer, .stDeployButton {{
        visibility: hidden;
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- AREA LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Kita buka pembungkus HTML
    st.markdown('<div class="login-frame">', unsafe_allow_html=True)
    
    # Render Logo & Judul
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">3G LOGISTICS SYSTEM</div>', unsafe_allow_html=True)
    
    # Input Password (Streamlit Component)
    pwd = st.text_input("PWD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
    
    # Tombol Masuk
    if st.button("MASUK SEKARANG"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Salah")
            
    st.markdown('</div>', unsafe_allow_html=True) # Tutup pembungkus
    st.stop()

# --- HALAMAN DASHBOARD KOSONG ---
st.title("Selamat Datang di Dashboard")
if st.button("Logout"):
    st.session_state.auth = False
    st.rerun()
