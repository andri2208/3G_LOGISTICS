import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - SYSTEM", page_icon="🚚", layout="wide")

# API & PASSWORD
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 2. CSS CUSTOM (EMERALD CONTRAST) ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Background Utama */
    .stApp {{ 
        background: linear-gradient(135deg, #0A4A4A 0%, #1A1A1A 100%); 
    }}
    
    /* Container Login agar tetap di tengah & mungil */
    .login-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        width: 100%;
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 40px;
        width: 100%;
        max-width: 350px; /* MEMBATASI LEBAR CARD DI PC */
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }}
    
    /* Mengecilkan Kotak Input secara paksa */
    div[data-baseweb="input"] {{
        width: 100% !important;
        max-width: 280px !important; /* UKURAN INPUT DIKUNCI DI SINI */
        margin: 0 auto !important;
    }}

    .stTextInput > div > div > input {{
        text-align: center;
        border-radius: 10px !important;
        height: 42px !important;
        background-color: white !important;
        color: black !important;
    }}

    /* Tombol mengikuti lebar input */
    .stButton > button {{
        background: linear-gradient(90deg, #FF0000 0%, #CC0000 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        width: 100% !important;
        max-width: 280px !important; /* LEBAR TOMBOL SAMA DENGAN INPUT */
        height: 42px !important;
        font-weight: bold;
        border: none;
        margin-top: 10px;
    }}
    
    /* Sembunyikan elemen bawaan */
    header, footer, .stDeployButton {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA DATA & INVOICE ---
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
    
    # Header PT
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 51, 153)
    pdf.set_xy(55, 10)
    pdf.cell(0, 5, "PT. GAMA GEMAH GEMILANG", 0, 1)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(204, 0, 0)
    pdf.set_x(55)
    pdf.multi_cell(0, 4, "Ruko Paragon Plaza Blok D - 6 Jalan Ngasinan, Kepatihan, Menganti, Gresik,\nJawa Timur. Telp 031-79973432")
    pdf.line(10, 32, 200, 32)

    # Info Inv
    pdf.ln(10)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, "INVOICE", 1, 1, 'C', True)
    pdf.cell(95, 8, f"CUSTOMER : {data['penerima'].upper()}", 0, 0)
    pdf.cell(95, 8, f"DATE : {data['waktu_tgl']}", 0, 1, 'R')

    # Table
    pdf.set_fill_color(51, 122, 183)
    pdf.set_text_color(255, 255, 255)
    headers = [("Date Load", 25), ("Description", 55), ("Origin", 20), ("Dest", 30), ("Price", 25), ("Weight", 35)]
    for txt, w in headers: pdf.cell(w, 10, txt, 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(55, 10, data['deskripsi'][:25], 1, 0, 'C')
    pdf.cell(20, 10, data['asal'], 1, 0, 'C')
    pdf.cell(30, 10, data['tujuan'], 1, 0, 'C')
    pdf.cell(25, 10, f"{data['harga']:,}", 1, 0, 'C')
    pdf.cell(35, 10, f"{data['berat']} Kg", 1, 1, 'C')

    # Total & Terbilang
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(145, 10, "YANG HARUS DIBAYAR", 1, 0, 'C', True)
    pdf.cell(45, 10, f"Rp {data['total']:,}", 1, 1, 'R')
    pdf.set_font("Arial", 'BI', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])}", 1, 'C')

    # Footer
    pdf.ln(5)
    pdf.set_font("Arial", '', 9)
    pdf.cell(100, 5, "TRANSFER TO: BCA 6720422334 A/N ADITYA GAMA SAPUTRI", 0, 1)
    pdf.set_xy(150, pdf.get_y()+5)
    pdf.cell(40, 5, "Sincerely,", 0, 1, 'C')
    pdf.ln(15)
    pdf.set_font("Arial", 'BU', 10)
    pdf.set_x(150)
    pdf.cell(40, 5, "KELVINITO JAYADI", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. LOGIKA LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("##")
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="250">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:white;'>3G LOGISTICS LOGIN</h3>", unsafe_allow_html=True)
    pwd = st.text_input("PWD", type="password", placeholder="KODE AKSES", label_visibility="collapsed")
    if st.button("MASUK SISTEM"):
        if pwd == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Akses Ditolak")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD UTAMA ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)
col_head, col_out = st.columns([0.8, 0.2])
with col_out: 
    if st.button("🚪 LOGOUT"): 
        st.session_state.authenticated = False
        st.rerun()

tab1, tab2 = st.tabs(["💎 BUAT INVOICE", "📂 DATABASE SPREADSHEET"])

with tab1:
    with st.form("inv_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        cust = c1.text_input("Nama Customer")
        prod = c2.text_input("Nama Barang")
        c3, c4 = st.columns(2)
        ori = c3.text_input("Asal (Origin)")
        dest = c4.text_input("Tujuan (Destination)")
        c5, c6 = st.columns(2)
        prc = c5.number_input("Harga Satuan", min_value=0)
        wgt = c6.number_input("Berat Total (Kg)", min_value=0.0)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("🔥 PROSES & SIMPAN")
        with col_btn2:
            reset = st.form_submit_button("♻️ RESET FORM")

    if reset:
        st.rerun()

    if submit:
        if not all([cust, prod, ori, dest]) or prc <= 0:
            st.warning("Mohon lengkapi semua data!")
        else:
            inv_data = {
                "no_inv": f"INV-{datetime.now().strftime('%H%M%S')}",
                "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                "harga": prc, "berat": wgt, "total": int(prc * wgt)
            }
            try:
                requests.post(API_URL, json=inv_data)
                st.success("Data Berhasil Disimpan ke Spreadsheet!")
                pdf_bytes = render_pdf(inv_data)
                st.download_button("📥 CETAK INVOICE (PDF)", pdf_bytes, f"Invoice_{cust}.pdf", "application/pdf")
            except:
                st.error("Gagal terhubung ke Database!")

with tab2:
    if st.button("🔄 REFRESH DATABASE"):
        try:
            resp = requests.get(API_URL).json()
            df = pd.DataFrame(resp[1:], columns=resp[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.info("Klik tombol refresh untuk menarik data.")





