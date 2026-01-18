import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI API & PASSWORD ---
PASSWORD_AKSES = "3G2026"
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS PRO",
    page_icon="FAVICON.png", 
    layout="wide"
)

# --- 2. CUSTOM CSS (GRADIENT BACKGROUND & PRO STYLING) ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #991b1b 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #450a0a 100%);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: white !important;
    }
    h1, h2, h3, p, label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.write("#")
        st.write("#")
        with st.container(border=True):
            st.title("🔐 PRO LOGIN")
            pwd_input = st.text_input("Access Password", type="password")
            if st.button("Masuk ke Sistem", use_container_width=True):
                if pwd_input == PASSWORD_AKSES:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Akses Ditolak!")
    st.stop()

# --- 4. HEADER & LOGOUT (DI ATAS) ---
col_head, col_log = st.columns([0.85, 0.15])
with col_head:
    if os.path.exists("HEADER INVOICE.png"):
        st.image("HEADER INVOICE.png", width=400)
    else:
        st.header("PT. GAMA GEMAH GEMILANG")

with col_log:
    st.write("#")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- 5. FUNGSI TEKNIS ---
def generate_invoice_number():
    now = datetime.now()
    return f"INV/{now.strftime('%Y%m%d')}/{now.strftime('%H%M%S')}"

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
    elif n < 1000000000: hasil = terbilang(n // 1000000).replace(" Rupiah", "") + " Juta " + terbilang(n % 1000000).replace(" Rupiah", "")
    return hasil.strip() + " Rupiah"

def buat_pdf_custom(data):
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
    pdf.cell(90, 6, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(10)
    
    # Header Tabel PDF
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
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
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "TOTAL BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])}")

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "Bank BCA - 6720422334 - A/N ADITYA GAMA SAPUTRI", ln=True)
    pdf.ln(10)
    pdf.cell(190, 5, "Sincerely,", 0, 1, 'R')
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=150, y=pdf.get_y(), w=30)
    pdf.ln(20)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVIGASI TAB ---
tab1, tab2 = st.tabs(["🚀 GENERATE INVOICE", "📂 RIWAYAT DATABASE"])

with tab1:
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    with st.form("pro_form", clear_on_submit=True):
        st.write("### 📝 Masukkan Data Pengiriman")
        c1, c2 = st.columns(2)
        cust = c1.text_input("Nama Customer *")
        prod = c2.text_input("Deskripsi Barang *")
        
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("Origin *")
        dest = c4.text_input("Destination *")
        hrg = c5.number_input("Harga *", min_value=0, value=0)
        wgt = c6.number_input("Berat (Kg) *", min_value=0.0, value=0.0)
        
        btn = st.form_submit_button("SIMPAN & TERBITKAN INVOICE", use_container_width=True)

        if btn:
            if not all([cust.strip(), prod.strip(), ori.strip(), dest.strip()]) or hrg <= 0 or wgt <= 0:
                st.warning("Semua kolom bertanda * wajib diisi dengan benar!")
            else:
                inv_no = generate_invoice_number()
                st.session_state.preview_data = {
                    "no_inv": inv_no, "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview_data)
                st.success(f"Berhasil menyimpan {inv_no}")
                st.balloons()

    if st.session_state.preview_data:
        d = st.session_state.preview_data
        st.write("---")
        col_pre, col_close = st.columns([0.8, 0.2])
        col_pre.subheader(f"🔍 Preview: {d['no_inv']}")
        if col_close.button("Tutup Preview"):
            st.session_state.preview_data = None
            st.rerun()
        
        with st.container(border=True):
            st.write(f"**Customer:** {d['penerima']} | **Total:** Rp {d['total']:,}")
            st.write(f"**Terbilang:** {terbilang(d['total'])}")
            
        pdf_bytes = buat_pdf_custom(d)
        st.download_button("📥 DOWNLOAD PDF SEKARANG", data=pdf_bytes, 
                           file_name=f"Invoice_{d['no_inv']}.pdf", use_container_width=True)

with tab2:
    st.write("### 📊 Database Transaksi Terakhir")
    if st.button("🔄 Segarkan Data Database", use_container_width=True):
        try:
            res = requests.get(API_URL).json()
            if len(res) > 1:
                df = pd.DataFrame(res[1:], columns=res[0])
                st.dataframe(df.iloc[::-1], use_container_width=True)
            else:
                st.info("Belum ada data.")
        except:
            st.error("Koneksi Database Gagal.")
