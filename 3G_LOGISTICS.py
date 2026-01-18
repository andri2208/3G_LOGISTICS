import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# --- CSS MINIMALIS & HEADER KECIL ---
st.markdown("""
    <style>
    /* Latar Belakang Ivory */
    .stApp { background-color: #FDFCF0; }
    
    /* Memperkecil Margin Atas agar Header naik */
    .block-container { padding-top: 1rem !important; }

    /* Mengecilkan Header Image */
    [data-testid="stImage"] img {
        max-width: 400px !important; /* Header diperkecil ke 400px */
        margin: 0 auto;
        display: block;
    }

    /* Label Tebal Minimalis */
    .stWidgetLabel p {
        font-weight: 800 !important;
        font-size: 13px !important; /* Font lebih kecil tapi tebal */
        color: #1A2A3A !important;
        margin-bottom: 2px !important;
    }
    
    /* Kolom Input Lebih Pendek (Minimalis) */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #BCC6CC !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
    }

    /* Form Minimalis */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin-top: -20px;
    }

    /* Button Simpan Kecil */
    .stButton button {
        width: 100%;
        background-color: #1A2A3A !important;
        color: white !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
    if match: return float(match[0])
    return 0

def terbilang(n):
    bil = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return " Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return " Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return ""

@st.cache_data(ttl=2)
def get_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except: return []

# HEADER WEB DIPERKECIL
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png")

tab1, tab2 = st.tabs(["📄 CETAK", "➕ INPUT"])

with tab1:
    data = get_data()
    if not data:
        st.info("Loading...")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("PILIH CUSTOMER:", sorted(df['customer'].unique()))
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        b_val = extract_number(row['weight'])
        h_val = extract_number(row['harga'])
        t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
        
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        kata_terbilang = terbilang(t_val) + " Rupiah"

        invoice_html = f"""
        <div id="invoice-card" style="background:white; padding:15px; max-width:700px; margin:auto; border:1px solid #ddd; color:black; font-family:Arial;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold;">INVOICE</div>
            <table style="width:100%; font-size:12px; font-weight:bold; margin-bottom:10px;">
                <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
            </table>
            <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size:10px; text-align:center;">
                <tr style="background:#f8f9fa;">
                    <th style="border:1px solid black; padding:5px;">Description</th><th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Dest</th><th style="border:1px solid black;">KOLLI</th>
                    <th style="border:1px solid black;">HARGA</th><th style="border:1px solid black;">WEIGHT</th><th style="border:1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:8px;">{row['description']}</td><td style="border:1px solid black;">{row['origin']}</td>
                    <td style="border:1px solid black;">{row['destination']}</td><td style="border:1px solid black;">{row['kolli']}</td>
                    <td style="border:1px solid black;">Rp {int(h_val):,}</td><td style="border:1px solid black;">{row['weight']}</td>
                    <td style="border:1px solid black; font-weight:bold;">Rp {t_val:,}</td>
                </tr>
                <tr style="font-weight:bold;">
                    <td colspan="6" style="border:1px solid black; text-align:right; padding:5px;">TOTAL BAYAR</td>
                    <td style="border:1px solid black;">Rp {t_val:,}</td>
                </tr>
            </table>
            <div style="border:1px solid black; padding:5px; margin-top:10px; font-size:10px; font-style:italic;"><b>Terbilang:</b> {kata_terbilang}</div>
            <table style="width:100%; margin-top:15px; font-size:10px;">
                <tr>
                    <td><b>TRANSFER TO:</b><br>BCA 6720422334<br>A/N ADITYA GAMA SAPUTRI<br>Finance: 082179799200</td>
                    <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:90px;"><br><b><u>KELVINITO JAYADI</u></b></td>
                </tr>
            </table>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <button onclick="downloadPDF()" style="width:100%; background:#1A2A3A; color:white; padding:10px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px;">📥 DOWNLOAD PDF A5</button>
        <script>
        function downloadPDF() {{
            const element = document.getElementById('invoice-card');
            const opt = {{ margin: 0.1, filename: 'Inv_{selected_cust}.pdf', html2canvas: {{ scale: 3 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }};
            html2pdf().set(opt).from(element).save();
        }}
        </script>
        """
        components.html(invoice_html, height=750, scrolling=True)

with tab2:
    with st.form("form_db", clear_on_submit=True):
        # Baris 1
        c1, c2, c3 = st.columns([1.5, 2, 2])
        v_tgl = c1.date_input("TANGGAL", datetime.now())
        v_cust = c2.text_input("CUSTOMER")
        v_desc = c3.text_input("BARANG")
        
        # Baris 2
        c4, c5, c6, c7, c8 = st.columns([1, 1, 1, 1, 1.5])
        v_orig = c4.text_input("ORIGIN", value="SBY")
        v_dest = c5.text_input("DEST")
        v_kol = c6.text_input("KOLLI")
        v_kg = c7.text_input("WEIGHT")
        v_hrg = c8.number_input("HARGA", 0)
        
        if st.form_submit_button("💾 SIMPAN DATA"):
            w_num = extract_number(v_kg)
            total_db = int(w_num * v_hrg) if w_num > 0 else int(v_hrg)
            payload = {
                "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                "harga": v_hrg, "weight": v_kg, "total": total_db
            }
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"Tersimpan! Rp {total_db:,}")
                st.cache_data.clear()
            except:
                st.error("Gagal!")
