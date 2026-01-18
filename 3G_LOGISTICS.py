import streamlit as st
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - LOGIN",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNGSI ENCODE GAMBAR ---
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. CSS LUXURY RESPONSIVE (TANPA KOTAK KOSONG) ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Background Utama */
    .stApp {{
        background: linear-gradient(135deg, #4b0000 0%, #000000 100%);
        background-attachment: fixed;
    }}

    /* Container Utama untuk Responsivitas */
    .main-login-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 90vh;
        padding: 20px;
    }}

    /* Card Login Elegan */
    .login-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 50px 30px;
        width: 100%;
        max-width: 450px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        text-align: center;
    }}

    /* Logo Pro */
    .logo-img {{
        width: 100%;
        max-width: 280px;
        height: auto;
        margin-bottom: 20px;
    }}

    /* Teks Deskripsi */
    .brand-text {{
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }}

    .sub-text {{
        color: rgba(255,255,255,0.6);
        font-size: 0.9rem;
        margin-bottom: 30px;
    }}

    /* Styling Input */
    .stTextInput > div > div > input {{
        background-color: rgba(255,255,255,0.9) !important;
        color: #1a1a1a !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        border: none !important;
    }}

    /* Styling Button */
    .stButton > button {{
        background: linear-gradient(90deg, #cc0000 0%, #800000 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        width: 100% !important;
        height: 50px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all ease;
        margin-top: 10px;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(204, 0, 0, 0.4);
        background: #ff0000 !important;
    }}

    /* Sembunyikan Elemen Streamlit */
    header, footer, #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* Responsivitas Layar HP */
    @media (max-width: 480px) {{
        .login-card {{
            padding: 30px 20px;
        }}
        .logo-img {{
            max-width: 200px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Menggunakan HTML murni untuk wrapper agar center sempurna
    st.markdown('<div class="main-login-container">', unsafe_allow_html=True)
    
    # Memulai Card
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Menampilkan Logo jika ada
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    
    st.markdown('<div class="brand-text">PT. GAMA GEMAH GEMILANG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Cargo & Logistics Management System</div>', unsafe_allow_html=True)
    
    # Input Password menggunakan Streamlit
    # Kita gunakan container kosong agar form streamlit masuk ke dalam div login-card
    with st.container():
        pwd = st.text_input("PASSWORD", type="password", placeholder="ENTER ACCESS CODE", label_visibility="collapsed")
        
        if st.button("UNLOCK SYSTEM"):
            if pwd == "2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Access Code")
                
    st.markdown('</div>', unsafe_allow_html=True) # Tutup login-card
    st.markdown('</div>', unsafe_allow_html=True) # Tutup main-login-container
    st.stop()

# --- 5. HALAMAN DASHBOARD (SETELAH LOGIN) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)
st.success("Login Berhasil! Selamat Datang di Dashboard.")

# Tombol Logout sederhana di pojok
if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()
