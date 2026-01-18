import streamlit as st
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_img("FAVICON.png")

# --- 2. CSS "TOTAL CLEAN" (MENGHAPUS SEMUA ELEMEN STREAMLIT) ---
st.markdown(f"""
    <style>
    /* Hilangkan semua container, padding, dan garis bawaan Streamlit */
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"],
    .stVerticalBlock {{
        gap: 0 !important;
        padding: 0 !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* Sembunyikan Header, Footer, dan Menu */
    header, footer, .stDeployButton, [data-testid="stHeader"] {{
        display: none !important;
    }}

    /* Background Full Screen */
    .stApp {{ 
        background: #052222 !important; 
    }}

    /* Layout Login Custom - Rapi di Atas */
    .login-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 60px; /* Jarak pas dari atas */
        z-index: 9999;
        background: #052222;
    }}

    .logo-img {{
        width: 250px;
        margin-bottom: 5px;
    }}

    .title-text {{
        color: white;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 30px;
    }}

    /* Paksa input password jadi kecil & rapi */
    div[data-baseweb="input"] {{
        width: 300px !important;
        margin: 0 auto !important;
        border-radius: 8px !important;
    }}

    .stTextInput > div > div > input {{
        text-align: center !important;
        height: 45px !important;
        font-size: 16px !important;
        background-color: white !important;
        color: black !important;
    }}

    /* Tombol Merah Solid */
    .stButton > button {{
        background: #cc0000 !important;
        color: white !important;
        width: 300px !important;
        border-radius: 8px !important;
        height: 45px !important;
        font-weight: bold;
        border: none !important;
        margin-top: 20px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Menggunakan Container HTML murni untuk membungkus login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    
    st.markdown('<div class="title-text">3G LOGISTICS LOGIN</div>', unsafe_allow_html=True)
    
    # Input Streamlit tetap digunakan tapi sudah "dijinakkan" oleh CSS di atas
    pwd = st.text_input("PASSWORD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
    
    if st.button("MASUK SISTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. AREA DASHBOARD (MUNCUL SETELAH LOGIN) ---
st.markdown("<style>.stApp { background: white !important; }</style>", unsafe_allow_html=True) # Ganti bg putih saat masuk
st.title("🚀 Dashboard Utama PT. GGG")
st.write("Kotak login sudah hilang. Dashboard siap diisi.")

if st.button("Logout"):
    st.session_state.auth = False
    st.rerun()
