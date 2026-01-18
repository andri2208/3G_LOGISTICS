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

# --- CSS PERBAIKAN HEADER & KONTRAS ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    /* Memberi ruang di atas agar header tidak tertutup TAB Streamlit */
    .block-container { padding-top: 3.5rem !important; }

    /* Ukuran Header yang Pas (Tidak kekecilan, tidak tertutup) */
    [data-testid="stImage"] img {
        max-width: 600px !important; 
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* Label Input Tebal & Jelas */
    .stWidgetLabel p {
        font-weight: 900 !important;
        font-size: 14px !important;
        color: #1A2A3A !important;
        margin-bottom: 2px !important;
    }
    
    /* Input Field Putih Bersih */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #BCC6CC !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }

    /* Tab Menu Lebih Menonjol */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
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

# Header diletakkan di tengah dengan margin atas yang aman
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png")

tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    data = get_data()
    if not data:
        st.info("Menunggu Data...")
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
        <div id="inv" style="background:white; padding:15px; max-width:700px; margin:auto; border:1px solid #ddd; color:black; font-family:Arial;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold;">INVOICE</div>
            <table style="width:100%; font-size:12px; font-weight:bold; margin-bottom:5px;">
                <tr><td>CUST: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
            </table>
            <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size:10px; text-align:center;">
                <tr style="background:#f0f0f0;">
                    <th style="border:1px solid black; padding:5px;">Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:8px;">{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td>
                    <td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td>
                </tr>
                <tr style="font-weight:bold; background:#f9f9f9;">
                    <td colspan="6" style="border:1px solid black; text-align:right; padding:5px;">TOTAL BAYAR</td><td style="border:1px solid black;">Rp {t_val:,}</td>
                </tr>
            </table>
            <div style="border:1px solid black; padding:5px; margin-top:8px; font-size:10px; font-style:italic;"><b>Terbilang:</b> {kata_terbilang}</div>
            <table style="width:100%; margin-top:15px; font-size:10px;">
                <tr>
                    <td><b>TRANSFER TO:</b><br>BCA 6720422334<br>A/N ADITYA GAMA SAPUTRI<br>Finance: 082179799200</td>
                    <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:85px;"><br><b><u>KELVINITO JAYADI</u></b></td>
                </tr>
            </table>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <button onclick="savePDF()" style="width:100%; background:#1A2A3A; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px;">📥 DOWNLOAD PDF A5</button>
        <script>
        function savePDF() {{
            const element = document.getElementById('inv');
            const opt = {{ margin: 0.1, filename: 'Inv_{selected_cust}.pdf', html2canvas: {{ scale: 3 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }};
            html2pdf().set(opt).from(element).save();
        }}
        </script>
        """
        components.html(invoice_html, height=800, scrolling=True)

with tab2:
    with st.form("f_input", clear_on_submit=True):
        # Susunan Minimalis 2 Baris
        r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 2])
        v_tgl = r1_c1.date_input("TGL")
        v_cust = r1_c2.text_input("CUSTOMER")
        v_desc = r1_c3.text_input("BARANG")
        
        r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns([1, 1, 1, 1, 1.5])
        v_orig = r2_c1.text_input("DARI", value="SBY")
        v_dest = r2_c2.text_input("KE")
        v_kol = r2_c3.text_input("KOLLI")
        v_kg = r2_c4.text_input("KG")
        v_hrg = r2_c5.number_input("HARGA", 0)
        
        st.write("")
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
                st.success(f"Tersimpan: Rp {total_db:,}")
                st.cache_data.clear()
            except:
                st.error("Gagal!")
