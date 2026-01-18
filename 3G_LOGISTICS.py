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

# --- 2. CUSTOM CSS (WARNA KONTRAS TINGGI) ---
st.markdown("""
    <style>
    /* Background Gradien Merah Biru Terang */
    .stApp {
        background: linear-gradient(135deg, #ff4b4b 0%, #1c92ff 100%);
    }
    
    /* Memaksa Semua Label Input Jadi Putih Tebal agar Terbaca */
    label, .stMarkdown, p, h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* FIX TOMBOL: Background Gelap, Teks Putih Terang */
    .stButton>button {
        background-color: #002d5e !important; /* Biru Tua Gelap */
        color: #ffffff !important; /* Teks Putih Murni */
        border-radius: 10px;
        border: 2px solid #ffffff;
        font-weight: 900 !important;
        font-size: 18px !important;
        height: 3.5em;
        width: 100%;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
        text-transform: uppercase;
    }
    
    .stButton>button:hover {
        background-color: #ff1f1f !important; /* Merah Menyala saat Hover */
        color: white !important;
        border: 2px solid #002d5e;
    }

    /* Kolom Input agar Kontras */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold !important;
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
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🔐 LOGIN ADMIN</h1>", unsafe_allow_html=True)
            pwd_input = st.text_input("PASSWORD AKSES", type="password")
            if st.button("MASUK SISTEM"):
                if pwd_input == PASSWORD_AKSES:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("PASSWORD SALAH!")
    st.stop()

# --- 4. HEADER & LOGOUT ATAS ---
col_head, col_log = st.columns([0.8, 0.2])
with col_head:
    if os.path.exists("HEADER INVOICE.png"):
        st.image("HEADER INVOICE.png", width=300)
    else:
        st.title("PT. GAMA GEMAH GEMILANG")

with col_log:
    st.write("##") 
    if st.button("🚪 LOGOUT"):
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

# --- Fungsi PDF Sederhana ---
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
    
    # Tabel
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
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, f"TOTAL BAYAR: Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])}")

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "SINCERELY,", 0, 1, 'R')
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=155, y=pdf.get_y(), w=30)
    pdf.ln(20)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 6. TAB CONTENT ---
tab1, tab2 = st.tabs(["📝 BUAT INVOICE", "📊 DATABASE"])

with tab1:
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    with st.form("main_form", clear_on_submit=True):
        st.markdown("### 📝 DATA PENGIRIMAN")
        c1, c2 = st.columns(2)
        cust = c1.text_input("NAMA CUSTOMER *")
        prod = c2.text_input("DESKRIPSI BARANG *")
        
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("ORIGIN *")
        dest = c4.text_input("DESTINATION *")
        hrg = c5.number_input("HARGA *", min_value=0, value=0)
        wgt = c6.number_input("BERAT (Kg) *", min_value=0.0, value=0.0)
        
        if st.form_submit_button("SIMPAN & TERBITKAN"):
            if not all([cust.strip(), prod.strip(), ori.strip(), dest.strip()]) or hrg <= 0 or wgt <= 0:
                st.warning("⚠️ HARAP ISI SEMUA KOLOM!")
            else:
                inv_no = generate_invoice_number()
                st.session_state.preview_data = {
                    "no_inv": inv_no, "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview_data)
                st.success("DATA TERSIMPAN!")
                st.balloons()

    if st.session_state.preview_data:
        d = st.session_state.preview_data
        st.write("---")
        if st.button("❌ TUTUP PREVIEW"):
            st.session_state.preview_data = None
            st.rerun()
        
        pdf_bytes = buat_pdf_custom(d)
        st.download_button("📥 DOWNLOAD PDF INVOICE", data=pdf_bytes, file_name=f"Invoice_{d['no_inv']}.pdf")

with tab2:
    st.markdown("### 📊 RIWAYAT TRANSAKSI")
    if st.button("🔄 REFRESH DATA"):
        try:
            res = requests.get(API_URL).json()
            df = pd.DataFrame(res[1:], columns=res[0])
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except:
            st.error("GAGAL MEMUAT DATA.")
