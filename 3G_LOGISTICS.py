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
    page_title="3G LOGISTICS - PRO DASHBOARD",
    page_icon="🚚", 
    layout="wide"
)

# --- 2. ULTIMATE PRO CSS (GLASSMORPHISM & HIGH CONTRAST) ---
st.markdown("""
    <style>
    /* Main Background Gradien Merah-Biru Menyala */
    .stApp {
        background: linear-gradient(135deg, #e11d48 0%, #2563eb 100%);
    }

    /* Styling Teks Utama */
    h1, h2, h3, label, .stMarkdown {
        color: white !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }

    /* Glassmorphism Container */
    div[data-testid="stForm"], .stTable, .stDataFrame {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 25px;
    }

    /* TOMBOL PRO (NAVY DARK - TEKS PUTIH MURNI) */
    .stButton>button, .stDownloadButton>button {
        background-color: #0f172a !important; /* Navy Sangat Gelap */
        color: #ffffff !important; /* Teks Putih Murni */
        border: 2px solid rgba(255,255,255,0.5) !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        height: 3.5rem !important;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Paksa teks di dalam tombol tetap putih */
    .stButton>button div p, .stDownloadButton>button div p {
        color: white !important;
    }

    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #0f172a !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }

    /* Styling Input Fields */
    input {
        background-color: white !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px 10px 0 0;
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.write("#")
        st.write("#")
        with st.container():
            st.markdown("<h1 style='text-align:center;'>🔒 ACCESS CONTROL</h1>", unsafe_allow_html=True)
            pwd = st.text_input("Enter Admin Password", type="password")
            if st.button("UNLOCK SYSTEM"):
                if pwd == PASSWORD_AKSES:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid Access!")
    st.stop()

# --- 4. HEADER ---
c_logo, c_empty, c_logout = st.columns([0.4, 0.4, 0.2])
with c_logo:
    if os.path.exists("HEADER INVOICE.png"):
        st.image("HEADER INVOICE.png", width=450)
    else:
        st.title("3G LOGISTICS")

with c_logout:
    st.write("##")
    if st.button("🚪 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("---")

# --- 5. FUNGSI INTI ---
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
    elif n < 1000000000: hasil = terbilang(n // 1000000).replace(" Rupiah", "") + " Juta " + terbilang(n % 1000000).replace(" Rupiah", "")
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
    
    # PDF TABLE
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    cols = [("Date Load", 25), ("Description", 50), ("Origin", 20), ("Dest", 25), ("Price", 20), ("Weight", 20), ("Total", 30)]
    for head, width in cols:
        pdf.cell(width, 10, head, 1, 0, 'C', True)
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
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 12, "TOTAL AMOUNT PAYABLE", 0, 0, 'R')
    pdf.cell(50, 12, f"Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"In Words: {terbilang(data['total'])}")

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "SINCERELY,", 0, 1, 'R')
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=155, y=pdf.get_y()+2, w=35)
    pdf.ln(25)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    pdf.set_font("Arial", size=8)
    pdf.cell(190, 5, "DIRECTOR", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- 6. TAMPILAN TAB ---
t1, t2 = st.tabs(["💎 CREATE NEW INVOICE", "📂 ARCHIVE DATABASE"])

with t1:
    with st.form("pro_form", clear_on_submit=True):
        st.markdown("### 📝 Shipment Details")
        c1, c2 = st.columns(2)
        cust = c1.text_input("Customer Name")
        prod = c2.text_input("Product Description")
        
        c3, c4, c5, c6 = st.columns(4)
        ori = c3.text_input("Origin")
        dest = c4.text_input("Destination")
        hrg = c5.number_input("Unit Price", min_value=0, value=0)
        wgt = c6.number_input("Total Weight (Kg)", min_value=0.0, format="%.2f")
        
        submit = st.form_submit_button("🔥 SAVE & GENERATE INVOICE")

        if submit:
            if not all([cust, prod, ori, dest]) or hrg <= 0 or wgt <= 0:
                st.error("🚨 Please fill all required fields correctly!")
            else:
                inv_no = generate_inv()
                st.session_state.preview = {
                    "no_inv": inv_no, "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                    "penerima": cust, "deskripsi": prod, "asal": ori, "tujuan": dest,
                    "harga": hrg, "berat": wgt, "total": int(hrg * wgt)
                }
                requests.post(API_URL, json=st.session_state.preview)
                st.success(f"Success! Invoice {inv_no} has been recorded.")
                st.balloons()

    if "preview" in st.session_state and st.session_state.preview:
        p = st.session_state.preview
        st.write("---")
        st.markdown(f"### 📄 Preview Invoice: `{p['no_inv']}`")
        st.write(f"**Customer:** {p['penerima']} | **Total:** Rp {p['total']:,}")
        
        pdf_data = render_pdf(p)
        st.download_button("📥 DOWNLOAD OFFICIAL PDF", data=pdf_data, file_name=f"3G_{p['penerima']}.pdf")
        if st.button("❌ Close Preview"):
            st.session_state.preview = None
            st.rerun()

with t2:
    st.markdown("### 📊 Transaction History")
    if st.button("🔄 REFRESH DATABASE"):
        try:
            res = requests.get(API_URL).json()
            if len(res) > 1:
                df = pd.DataFrame(res[1:], columns=res[0])
                st.dataframe(df.iloc[::-1], use_container_width=True, height=500)
            else:
                st.info("No records found.")
        except:
            st.error("Connection failed.")
