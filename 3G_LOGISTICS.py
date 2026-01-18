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

# --- 2. FUNGSI ENCODE GAMBAR (Agar Responsif) ---
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. ULTIMATE NEON PRO CSS ---
st.markdown(f"""
    <style>
    /* Background Gradien Merah-Biru Menyala (Electric) */
    .stApp {{
        background: linear-gradient(135deg, #ff0000 0%, #0012ff 100%);
        background-attachment: fixed;
    }}

    /* Tampilan Logo Login & Header */
    .header-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }}
    .header-box img {{
        width: 100%;
        max-width: 700px;
        height: auto;
        filter: drop-shadow(0px 0px 15px rgba(255,255,255,0.5));
    }}

    /* Box Login Glassmorphism */
    .login-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        text-align: center;
    }}

    /* Tombol Pro Ultra Kontras */
    .stButton>button, .stDownloadButton>button {{
        background: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        font-size: 1.3rem !important;
        height: 3.8rem !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
        box-shadow: 0px 0px 20px rgba(255,255,255,0.2);
    }}
    
    .stButton>button:hover {{
        background: #ffffff !important;
        color: #ff0000 !important;
        box-shadow: 0px 0px 30px rgba(255,255,255,0.6);
        transform: scale(1.02);
    }}

    /* Teks dan Input */
    h1, h2, h3, label, p {{
        color: white !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        font-weight: 800 !important;
    }}
    
    .stTextInput>div>div>input {{
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 45px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. HALAMAN LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("#") # Spacer
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        logo_data = get_base64_img("FAVICON.png")
        if logo_data:
            st.markdown(f'<div class="header-box"><img src="data:image/png;base64,{logo_data}"></div>', unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align:center; font-size: 50px;'>3G LOGIN</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.write("---")
            pwd = st.text_input("PASSWORD AKSES", type="password", placeholder="Enter Password Here...")
            if st.button("UNLOCK DASHBOARD"):
                if pwd == PASSWORD_AKSES:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("AKSES DITOLAK: Password Salah!")
    st.stop()

# --- 5. DASHBOARD UTAMA (SETELAH LOGIN) ---
col_head, col_log = st.columns([0.8, 0.2])

with col_head:
    logo_data = get_base64_img("HEADER INVOICE.png")
    if logo_data:
        st.markdown(f'<div style="text-align:left;"><img src="data:image/png;base64,{logo_data}" style="width:400px;"></div>', unsafe_allow_html=True)
    else:
        st.title("3G LOGISTICS PRO")

with col_log:
    st.write("###")
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- 6. FUNGSI LOGIK & PDF ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    if n == 0: return "Rupiah"
    if n < 12: hasil = bilangan[n]
    elif n < 20: hasil = terbilang(n - 10).replace(" Rupiah", "") + " Belas"
    elif n < 100: hasil = terbilang(n // 10).replace(" Rupiah", "") + " Puluh " + terbilang(n % 10).replace(" Rupiah", "")
    elif n < 200: hasil = "Seratus " + terbilang(n - 100).replace(" Rupiah", "")
    elif n < 1000: hasil = terbilang(n // 100).replace(" Rupiah", "") + " Ratus " + terbilang(n % 100).replace(" Rupiah", "")
    elif n < 2000: hasil = "Seribu " + terbilang(n - 1000).replace(" Rupiah", "")
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
    pdf.set_font("Arial", size=9)
    pdf.cell(100, 6, f"No: {data['no_inv']}", 0)
    pdf.cell(90, 6, f"Date: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(10)
    
    # Table Header PDF
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

    pdf.ln(10)
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=155, y=pdf.get_y()+5, w=35)
    pdf.ln(25)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 7. TAMPILAN TAB ---
t1, t2 = st.tabs(["🚀 GENERATE INVOICE", "📊 TRANSACTION HISTORY"])

with t1:
    with st.form("main_form", clear_on_submit=True):
        st.markdown("### 📥 Input Data Pengiriman")
        c1, c2 = st.columns(2)
        cust = c1.text_input("NAMA CUSTOMER *")
        prod = c2.text_input("DESKRIPSI BARANG *")
        
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("ORIGIN *")
        dest = c4.text_input("DESTINATION *")
        hrg = c5.number_input("HARGA SATUAN *", min_value=0, value=0)
        wgt = c6.number_input("BERAT TOTAL (Kg) *", min_value=0.0)
        
        if st.form_submit_button("🔥 SIMPAN & TERBITKAN"):
            if not all([cust.strip(), prod.strip(), ori.strip(), dest.strip()]) or hrg <= 0 or wgt <= 0:
                st.error("⚠️ SEMUA DATA WAJIB DIISI!")
            else:
                st.session_state.preview = {
                    "no_inv": f"INV/{datetime.now().strftime('%Y%m%d/%H%M%S')}", 
                    "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview)
                st.success("✅ DATA BERHASIL DISIMPAN!")
                st.balloons()

    if "preview" in st.session_state and st.session_state.preview:
        p = st.session_state.preview
        st.divider()
        st.download_button("📥 DOWNLOAD PDF INVOICE", data=render_pdf(p), file_name=f"Invoice_{p['penerima']}.pdf", use_container_width=True)

with t2:
    if st.button("🔄 REFRESH DATABASE"):
        try:
            res = requests.get(API_URL).json()
            df = pd.DataFrame(res[1:], columns=res[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("Database Gagal Dimuat")

