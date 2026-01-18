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

# --- 2. FUNGSI HELPER ---
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. CUSTOM CSS (MINIMALIS & RESPONSIF) ---
st.markdown(f"""
    <style>
    /* Tema Utama */
    .stApp {{
        background: linear-gradient(135deg, #ff0033 0%, #0044ff 100%);
        background-attachment: fixed;
    }}

    /* Container Login Minimalis */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 40px;
        width: 100%;
        max-width: 400px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        text-align: center;
    }}

    /* Input Minimalis */
    .stTextInput>div>div>input {{
        background-color: white !important;
        color: black !important;
        border-radius: 12px !important;
        height: 50px !important;
        text-align: center;
        font-weight: bold !important;
    }}

    /* Tombol Pro */
    .stButton>button {{
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        height: 50px !important;
        width: 100%;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background: #ffffff !important;
        color: #000000 !important;
        transform: translateY(-2px);
    }}

    /* Logo Responsive */
    .responsive-logo {{
        width: 100%;
        max-width: 300px;
        height: auto;
        margin-bottom: 20px;
    }}

    /* Sembunyikan Header Streamlit */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    logo_b64 = get_base64_img("HEADER INVOICE.png")
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="responsive-logo">', unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:white;'>3G LOGISTICS</h2>", unsafe_allow_html=True)
    
    pwd = st.text_input("ACCESS CODE", type="password", placeholder="••••", label_visibility="collapsed")
    
    if st.button("SIGN IN"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong Code")
            
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD UTAMA (SETELAH LOGIN) ---
# Tampilkan kembali scroll untuk dashboard
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

c_logo, c_out = st.columns([0.8, 0.2])
with c_logo:
    logo_dash = get_base64_img("HEADER INVOICE.png")
    if logo_dash:
        st.markdown(f'<img src="data:image/png;base64,{logo_dash}" style="width:250px;">', unsafe_allow_html=True)
with c_out:
    st.write("##")
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- 6. FUNGSI LOGIK & PDF (Sesuai Kode Anda) ---
def generate_inv():
    return f"INV/{datetime.now().strftime('%Y%m%d/%H%M%S')}"

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
    
    # Table
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    headers = [("Date Load", 25), ("Description", 50), ("Origin", 20), ("Dest", 25), ("Price", 20), ("Weight", 20), ("Total", 30)]
    for txt, w in headers:
        pdf.cell(w, 10, txt, 1, 0, 'C', True)
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
    pdf.cell(190, 12, f"TOTAL: Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"In Words: {terbilang(data['total'])}")

    pdf.ln(10)
    pdf.cell(190, 5, "SINCERELY,", 0, 1, 'R')
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=155, y=pdf.get_y()+2, w=35)
    pdf.ln(25)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 7. TAMPILAN TAB ---
t1, t2 = st.tabs(["💎 CREATE INVOICE", "📂 DATABASE"])

with t1:
    with st.form("main_form", clear_on_submit=True):
        st.markdown("### 📝 Shipment Data")
        c1, c2 = st.columns(2)
        cust = c1.text_input("Customer Name")
        prod = c2.text_input("Product Name")
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("Origin")
        dest = c4.text_input("Destination")
        hrg = c5.number_input("Price", min_value=0, value=0)
        wgt = c6.number_input("Weight (Kg)", min_value=0.0)
        
        if st.form_submit_button("🔥 SAVE & GENERATE"):
            if not all([cust, prod, ori, dest]) or hrg <= 0 or wgt <= 0:
                st.error("Fill all fields!")
            else:
                st.session_state.preview = {
                    "no_inv": generate_inv(), "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview)
                st.success("Invoice Saved!")
                st.balloons()

    if "preview" in st.session_state:
        pdf_data = render_pdf(st.session_state.preview)
        st.download_button("📥 DOWNLOAD PDF", data=pdf_data, file_name=f"3G_Invoice.pdf", use_container_width=True)

with t2:
    if st.button("🔄 REFRESH DATA"):
        try:
            res = requests.get(API_URL).json()
            df = pd.DataFrame(res[1:], columns=res[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("Database Error")
