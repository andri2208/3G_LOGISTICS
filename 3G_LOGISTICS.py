import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import base64
from fpdf import FPDF

# --- 1. KONFIGURASI ---
PASSWORD_AKSES = "2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 2. CSS CUSTOM (MINIMALIS & RESPONSIVE) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(145deg, #4b0000 0%, #000000 100%);
    }}
    .login-wrapper {{
        display: flex; justify-content: center; align-items: center; min-height: 80vh;
    }}
    .login-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 40px; border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        width: 100%; max-width: 450px; text-align: center;
    }}
    .login-logo {{ width: 100%; max-width: 350px; margin-bottom: 20px; }}
    .stButton>button {{
        background: white !important; color: black !important;
        font-weight: bold !important; border-radius: 10px !important; width: 100%;
    }}
    header, footer, .stDeployButton {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA DATASET (TERBILANG) ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    hasil = "" # Inisialisasi untuk mencegah UnboundLocalError
    if n < 12:
        hasil = bilangan[n]
    elif n < 20:
        hasil = terbilang(n - 10).replace(" Rupiah", "") + " Belas"
    elif n < 100:
        hasil = terbilang(n // 10).replace(" Rupiah", "") + " Puluh " + terbilang(n % 10).replace(" Rupiah", "")
    elif n < 200:
        hasil = "Seratus " + terbilang(n - 100).replace(" Rupiah", "")
    elif n < 1000:
        hasil = terbilang(n // 100).replace(" Rupiah", "") + " Ratus " + terbilang(n % 100).replace(" Rupiah", "")
    elif n < 2000:
        hasil = "Seribu " + terbilang(n - 1000).replace(" Rupiah", "")
    elif n < 1000000:
        hasil = terbilang(n // 1000).replace(" Rupiah", "") + " Ribu " + terbilang(n % 1000).replace(" Rupiah", "")
    elif n < 1000000000:
        hasil = terbilang(n // 1000000).replace(" Rupiah", "") + " Juta " + terbilang(n % 1000000).replace(" Rupiah", "")
    
    return (hasil.strip() + " rupiah") if n != 0 else "rupiah"

# --- 4. TAMPILAN INVOICE PDF (SESUAI GAMBAR) ---
def render_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Header Logo & Alamat (Sesuai image_35d824.png)
    if os.path.exists("FAVICON.png"):
        pdf.image("FAVICON.png", x=15, y=10, w=40)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 153) # Biru PT
    pdf.set_xy(60, 10)
    pdf.cell(0, 5, "PT. GAMA GEMAH GEMILANG", 0, 1)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(204, 0, 0) # Merah Alamat
    pdf.set_x(60)
    pdf.multi_cell(0, 4, "Ruko Paragon Plaza Blok D - 6 Jalan Ngasinan, Kepatihan, Menganti, Gresik,\nJawa Timur. Telp 031-79973432")
    
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, 32, 200, 32) # Garis Header
    
    # Info Customer & Tanggal
    pdf.ln(5)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 6, "INVOICE", 1, 1, 'C', True)
    
    pdf.ln(2)
    pdf.cell(95, 6, f"CUSTOMER : {data['penerima'].upper()}", 0, 0)
    pdf.cell(95, 6, f"DATE : {data['waktu_tgl']}", 0, 1, 'R')
    
    # Tabel Data
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(51, 122, 183) # Biru Tabel
    pdf.set_text_color(255, 255, 255)
    cols = [("Date of Load", 25), ("Product Description", 55), ("Origin", 20), ("Destination", 30), ("KOLLI", 15), ("HARGA", 20), ("WEIGHT", 25)]
    for txt, w in cols:
        pdf.cell(w, 8, txt, 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(25, 8, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(55, 8, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 8, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(30, 8, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(15, 8, "", 1, 0, 'C') # Kolli Kosong
    pdf.cell(20, 8, f"Rp {data['harga']:,}", 1, 0, 'C')
    pdf.cell(25, 8, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.ln()
    
    # Total
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(145, 7, "YANG HARUS DI BAYAR", 1, 0, 'C', True)
    pdf.cell(45, 7, f"Rp {data['total']:,}", 1, 1, 'R')
    
    # Terbilang
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(25, 8, "Terbilang :", "LTB", 0)
    pdf.set_font("Arial", 'BI', 9)
    pdf.cell(165, 8, terbilang(data['total']), "RTB", 1, 'C', True)
    
    # Footer (Transfer Info & Signature)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(100, 5, "TRANSFER TO :", 0, 0)
    pdf.cell(90, 5, "Sincerely,", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(100, 5, "Bank Central Asia", 0, 0)
    pdf.set_xy(10, pdf.get_y()+5)
    pdf.cell(100, 5, "6720422334", 0, 0)
    pdf.set_xy(10, pdf.get_y()+5)
    pdf.cell(100, 5, "A/N ADITYA GAMA SAPUTRI", 0, 0)
    
    # Signature box
    pdf.set_xy(140, pdf.get_y()-5)
    if os.path.exists("FAVICON.png"): # Ganti stempel jika ada file khusus
        pdf.image("FAVICON.png", x=155, y=pdf.get_y(), w=20)
    
    pdf.set_xy(140, pdf.get_y()+15)
    pdf.set_font("Arial", 'BU', 10)
    pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    pdf.set_font("Arial", 'B', 9)
    pdf.set_x(140)
    pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        logo_b64 = get_base64_img("FAVICON.png")
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="login-logo">', unsafe_allow_html=True)
        
        pwd = st.text_input("PASSWORD", type="password", placeholder="Access Code", label_visibility="collapsed")
        if st.button("AUTHENTICATE"):
            if pwd == PASSWORD_AKSES:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Code")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6. TAMPILAN DASHBOARD ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)
# ... Lanjutkan dengan tab Create Invoice dan Database seperti kode Anda sebelumnya ...
