import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI API & PASSWORD ---
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS - PRO DASHBOARD",
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

# --- 3. ULTIMATE SINGLE-SCREEN PRO CSS ---
st.markdown(f"""
    <style>
    /* Background & Menghilangkan Scroll pada Login */
    .stApp {{
        background: linear-gradient(135deg, #ff0000 0%, #0012ff 100%);
        background-attachment: fixed;
        overflow: hidden;
    }}

    /* Container Login agar Center Sempurna */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 30px;
        padding: 40px;
        width: 100%;
        max-width: 500px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        text-align: center;
    }}

    /* Logo Login Ramping */
    .login-logo {{
        width: 100%;
        max-width: 350px;
        height: auto;
        margin-bottom: 10px;
        filter: drop-shadow(0px 0px 10px rgba(255,255,255,0.4));
    }}

    /* Tombol Ultra Pro */
    .stButton>button {{
        background: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px;
        transition: 0.3s ease;
        width: 100%;
        height: 3.2rem;
    }}
    
    .stButton>button:hover {{
        background: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0px 0px 20px rgba(255,255,255,0.8);
    }}

    /* Teks Header */
    .login-title {{
        color: white;
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 20px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }}

    /* Sembunyikan Header Streamlit yang tidak perlu */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. HALAMAN LOGIN (NO SCROLL) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Menggunakan HTML khusus untuk layout yang presisi
    logo_base64 = get_base64_img("HEADER INVOICE.png")
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if logo_base64:
            st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="login-logo">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">3G LOGIN</div>', unsafe_allow_html=True)
        
        # Form Login
        pwd = st.text_input("ADMIN ACCESS CODE", type="password", label_visibility="collapsed", placeholder="Enter Password...")
        st.write("") # Spacer kecil
        if st.button("UNLOCK SYSTEM"):
            if pwd == PASSWORD_AKSES:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Password")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD UTAMA (SETELAH LOGIN) ---
# Tampilkan kembali scroll untuk dashboard data
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

col_h, col_l = st.columns([0.8, 0.2])
with col_h:
    logo_data = get_base64_img("HEADER INVOICE.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" style="width:300px;">', unsafe_allow_html=True)
with col_l:
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- FUNGSI PDF & TERBILANG (Tetap Sama) ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    if n == 0: return "Rupiah"
    if n < 12: hasil = bilangan[n]
    elif n < 20: hasil = terbilang(n - 10).replace(" Rupiah", "") + " Belas"
    elif n < 100: hasil = terbilang(n // 10).replace(" Rupiah", "") + " Puluh " + terbilang(n % 10).replace(" Rupiah", "")
    elif n < 200: hasil = "Seratus " + terbilang(n - 100).replace(" Rupiah", "")
    elif n < 1000: hasil = terbilang(n // 100).replace(" Rupiah", "") + " Ratus " + terbilang(n % 100).replace(" Rupiah", "")
    elif n < 1000000: hasil = terbilang(n // 1000).replace(" Rupiah", "") + " Ribu " + terbilang(n % 1000).replace(" Rupiah", "")
    return hasil.strip() + " Rupiah"

def render_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("HEADER INVOICE.png"):
        pdf.image("HEADER INVOICE.png", x=10, y=8, w=190)
        pdf.ln(35)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 6, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 6, "INVOICE", 0, 1, 'R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    for h, w in [("Date Load", 25), ("Description", 50), ("Origin", 20), ("Dest", 25), ("Price", 20), ("Weight", 20), ("Total", 30)]:
        pdf.cell(w, 10, h, 1, 0, 'C', True)
    pdf.ln()
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(50, 10, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(25, 10, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['harga']:,}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,}", 1, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 12, f"TOTAL AMOUNT: Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"In Words: {terbilang(data['total'])}")
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=155, y=pdf.get_y()+5, w=35)
    pdf.ln(25)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 6. TAMPILAN TAB ---
t1, t2 = st.tabs(["🚀 GENERATE INVOICE", "📊 TRANSACTION HISTORY"])

with t1:
    with st.form("main_form", clear_on_submit=True):
        st.markdown("### 📥 Input Data Pengiriman")
        c1, c2 = st.columns(2)
        cust = c1.text_input("NAMA CUSTOMER")
        prod = c2.text_input("DESKRIPSI BARANG")
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("ORIGIN")
        dest = c4.text_input("DESTINATION")
        hrg = c5.number_input("HARGA", min_value=0)
        wgt = c6.number_input("BERAT (Kg)", min_value=0.0)
        if st.form_submit_button("🔥 SIMPAN & TERBITKAN"):
            if not all([cust, prod, ori, dest]) or hrg <= 0 or wgt <= 0:
                st.error("Lengkapi data!")
            else:
                st.session_state.preview = {
                    "no_inv": f"INV/{datetime.now().strftime('%Y%m%d/%H%M%S')}", 
                    "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview)
                st.success("Tersimpan!")
                st.balloons()
    if "preview" in st.session_state:
        st.download_button("📥 DOWNLOAD PDF", data=render_pdf(st.session_state.preview), file_name="Invoice.pdf", use_container_width=True)

with t2:
    if st.button("🔄 REFRESH"):
        try:
            res = requests.get(API_URL).json()
            df = pd.DataFrame(res[1:], columns=res[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("Error")
