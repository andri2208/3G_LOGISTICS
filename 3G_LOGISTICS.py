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

# --- 2. CSS ANTI-KOTAK KOSONG (FRESH) ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Hilangkan paksa semua border container bawaan Streamlit */
    [data-testid="stVerticalBlock"] > div:empty {{
        display: none !important;
    }}
    
    .stApp {{ 
        background: linear-gradient(135deg, #052222 0%, #000000 100%); 
    }}

    /* Layout Login Atas */
    .login-box {{
        text-align: center;
        padding: 40px 20px;
        margin: 0 auto;
        max-width: 400px;
    }}

    .logo-img {{
        width: 200px;
        margin-bottom: 10px;
    }}

    /* Input Password Mungil */
    div[data-baseweb="input"] {{
        width: 250px !important;
        margin: 10px auto !important;
    }}

    .stTextInput > div > div > input {{
        text-align: center !important;
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 40px !important;
    }}

    /* Tombol Merah */
    .stButton > button {{
        background-color: #cc0000 !important;
        color: white !important;
        width: 250px !important;
        border-radius: 10px !important;
        border: none !important;
        height: 40px !important;
        font-weight: bold;
    }}

    /* Sembunyikan elemen sampah */
    header, footer, .stDeployButton, [data-testid="stHeader"] {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Menggunakan kolom untuk memastikan posisi di tengah atas
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:white;'>3G LOGISTICS LOGIN</h3>", unsafe_allow_html=True)
        
        pwd = st.text_input("PASSWORD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
        
        if st.button("MASUK SISTEM"):
            if pwd == PASSWORD_AKSES:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Akses Ditolak!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DASHBOARD (MUNCUL JIKA SUDAH LOGIN) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

# Fungsi Terbilang & PDF sama seperti sebelumnya
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    hasil = ""
    if n < 12: hasil = bilangan[n]
    elif n < 20: hasil = terbilang(n - 10).replace(" rupiah", "") + " Belas"
    elif n < 100: hasil = terbilang(n // 10).replace(" rupiah", "") + " Puluh " + terbilang(n % 10).replace(" rupiah", "")
    elif n < 200: hasil = "Seratus " + terbilang(n - 100).replace(" rupiah", "")
    elif n < 1000: hasil = terbilang(n // 100).replace(" rupiah", "") + " Ratus " + terbilang(n % 100).replace(" rupiah", "")
    elif n < 2000: hasil = "Seribu " + terbilang(n - 1000).replace(" rupiah", "")
    elif n < 1000000: hasil = terbilang(n // 1000).replace(" rupiah", "") + " Ribu " + terbilang(n % 1000).replace(" rupiah", "")
    elif n < 1000000000: hasil = terbilang(n // 1000000).replace(" rupiah", "") + " Juta " + terbilang(n % 1000000).replace(" rupiah", "")
    return (hasil.strip() + " rupiah") if n != 0 else "Nol rupiah"

def render_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("FAVICON.png"):
        pdf.image("FAVICON.png", x=15, y=10, w=35)
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 51, 153)
    pdf.set_xy(55, 10); pdf.cell(0, 5, "PT. GAMA GEMAH GEMILANG", 0, 1)
    pdf.set_font("Arial", '', 8); pdf.set_text_color(204, 0, 0)
    pdf.set_x(55); pdf.multi_cell(0, 4, "Ruko Paragon Plaza Blok D - 6 Jalan Ngasinan, Kepatihan, Menganti, Gresik,\nJawa Timur. Telp 031-79973432")
    pdf.line(10, 32, 200, 32)
    pdf.ln(10); pdf.set_font("Arial", 'B', 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, "INVOICE", 1, 1, 'C', True)
    pdf.cell(95, 8, f"CUSTOMER : {data['penerima'].upper()}", 0, 0)
    pdf.cell(95, 8, f"DATE : {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(2); pdf.set_fill_color(51, 122, 183); pdf.set_text_color(255, 255, 255)
    heads = [("Date Load", 25), ("Description", 55), ("Origin", 20), ("Dest", 30), ("Price", 25), ("Weight", 35)]
    for txt, w in heads: pdf.cell(w, 10, txt, 1, 0, 'C', True)
    pdf.ln(); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(55, 10, data['deskripsi'][:25], 1, 0, 'C')
    pdf.cell(20, 10, data['asal'], 1, 0, 'C')
    pdf.cell(30, 10, data['tujuan'], 1, 0, 'C')
    pdf.cell(25, 10, f"{data['harga']:,}", 1, 0, 'C')
    pdf.cell(35, 10, f"{data['berat']} Kg", 1, 1, 'C')
    pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(230, 230, 230)
    pdf.cell(145, 10, "YANG HARUS DIBAYAR", 1, 0, 'C', True)
    pdf.cell(45, 10, f"Rp {data['total']:,}", 1, 1, 'R')
    pdf.set_font("Arial", 'BI', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])}", 1, 'C')
    pdf.ln(5); pdf.set_font("Arial", '', 9)
    pdf.cell(100, 5, "TRANSFER TO: BCA 6720422334 A/N ADITYA GAMA SAPUTRI", 0, 1)
    pdf.set_xy(150, pdf.get_y()+5); pdf.cell(40, 5, "Sincerely,", 0, 1, 'C')
    pdf.ln(15); pdf.set_font("Arial", 'BU', 10); pdf.set_x(150); pdf.cell(40, 5, "KELVINITO JAYADI", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# Navbar Sederhana
c_logo, c_btn = st.columns([0.8, 0.2])
with c_btn:
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

tab1, tab2 = st.tabs(["📝 INPUT INVOICE", "📂 DATABASE"])

with tab1:
    with st.form("main_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        cust = c1.text_input("Nama Customer")
        prod = c2.text_input("Nama Barang")
        c3, c4 = st.columns(2)
        ori = c3.text_input("Asal")
        dest = c4.text_input("Tujuan")
        c5, c6 = st.columns(2)
        prc = c5.number_input("Harga", min_value=0)
        wgt = c6.number_input("Berat (Kg)", min_value=0.0)
        
        b1, b2 = st.columns(2)
        submit = b1.form_submit_button("✅ SIMPAN DATA")
        reset = b2.form_submit_button("♻️ RESET FORM")

    if reset:
        st.rerun()

    if submit:
        if cust and prod and ori and dest and prc > 0:
            inv_data = {
                "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                "harga": prc, "berat": wgt, "total": int(prc * wgt)
            }
            requests.post(API_URL, json=inv_data)
            st.success("Berhasil!")
            st.download_button("📥 DOWNLOAD PDF", render_pdf(inv_data), f"{cust}.pdf")

with tab2:
    if st.button("🔄 REFRESH"):
        resp = requests.get(API_URL).json()
        st.dataframe(pd.DataFrame(resp[1:], columns=resp[0]).iloc[::-1], use_container_width=True)
