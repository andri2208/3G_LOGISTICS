import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI API & PASSWORD ---
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS - PRO DASHBOARD",
    page_icon="🚚", 
    layout="wide"
)

# --- 2. ULTIMATE RESPONSIVE CSS ---
st.markdown("""
    <style>
    /* Background Gradien Merah-Biru */
    .stApp {
        background: linear-gradient(135deg, #e11d48 0%, #2563eb 100%);
    }

    /* CONTAINER LOGO RESPONSIVE */
    .logo-box {
        display: flex;
        justify-content: flex-start; /* Logo di kiri, ganti 'center' jika ingin di tengah */
        align-items: center;
        padding: 20px 0;
    }
    
    .logo-box img {
        width: 100%; /* Mengikuti container */
        max-width: 800px; /* Batas ukuran maksimal di laptop agar tidak terlalu raksasa */
        height: auto;
        border-radius: 10px;
    }

    /* Glassmorphism Styling */
    div[data-testid="stForm"], .stTable, .stDataFrame {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 20px;
    }

    /* TOMBOL HIGH-CONTRAST (NAVY) */
    .stButton>button, .stDownloadButton>button {
        background-color: #0f172a !important; /* Navy Gelap */
        color: #ffffff !important; /* Teks Putih */
        border: 2px solid white !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }

    .stButton>button div p, .stDownloadButton>button div p {
        color: white !important;
    }

    /* Memperbaiki tampilan input agar kontras */
    input {
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
    }

    /* Tampilan Mobile - Logout Button */
    @media (max-width: 640px) {
        .logo-box img {
            max-width: 100%; /* Full di layar HP */
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("#")
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.container():
            st.markdown("<h1 style='text-align:center;'>🔐 SECURE LOGIN</h1>", unsafe_allow_html=True)
            pwd = st.text_input("Password", type="password")
            if st.button("UNLOCK"):
                if pwd == PASSWORD_AKSES:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Access Denied!")
    st.stop()

# --- 4. HEADER RESPONSIVE ---
col_logo, col_logout = st.columns([0.8, 0.2])

with col_logo:
    if os.path.exists("HEADER INVOICE.png"):
        # Menggunakan HTML agar bisa dikontrol oleh CSS .logo-box di atas
        import base64
        with open("HEADER INVOICE.png", "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        st.markdown(f'<div class="logo-box"><img src="data:image/png;base64,{encoded}"></div>', unsafe_allow_html=True)
    else:
        st.title("3G LOGISTICS PRO")

with col_logout:
    st.write("###")
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- 5. FUNGSI LOGIK ---
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
    
    # PDF Table
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(25, 10, "Date Load", 1, 0, 'C', True)
    pdf.cell(50, 10, "Description", 1, 0, 'C', True)
    pdf.cell(20, 10, "Origin", 1, 0, 'C', True)
    pdf.cell(25, 10, "Dest", 1, 0, 'C', True)
    pdf.cell(20, 10, "Price", 1, 0, 'C', True)
    pdf.cell(20, 10, "Weight", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    
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

# --- 6. TAMPILAN TAB ---
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

    if "preview" in st.session_state and st.session_state.preview:
        p = st.session_state.preview
        st.write("---")
        pdf_data = render_pdf(p)
        st.download_button("📥 DOWNLOAD PDF INVOICE", data=pdf_data, file_name=f"3G_{p['no_inv']}.pdf", use_container_width=True)

with t2:
    if st.button("🔄 REFRESH DATA"):
        try:
            res = requests.get(API_URL).json()
            df = pd.DataFrame(res[1:], columns=res[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("Database Error")
