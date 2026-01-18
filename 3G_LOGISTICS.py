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

# --- CSS: HEADER KECIL, AMAN DARI TAB, & RESPONSIVE ---
st.markdown("""
    <style>
    /* Latar belakang Ivory */
    .stApp { background-color: #FDFCF0; }
    
    /* Padding Atas diperbesar agar Header TIDAK tertutup Tab Streamlit */
    .block-container { 
        padding-top: 5rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }

    /* Perkecil Header Web & Buat Ramping */
    .custom-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .custom-header img {
        width: 100%;
        max-width: 450px; /* Ukuran diperkecil lagi agar ramping */
        height: auto;
        border-radius: 5px;
    }

    /* Styling Tab & Label agar Padat */
    .stTabs [data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: bold !important;
        padding: 10px 15px !important;
    }
    
    .stWidgetLabel p {
        font-weight: 800 !important;
        font-size: 13px !important;
        color: #1A2A3A !important;
        margin-bottom: 0px !important;
    }

    /* Input Fields Minimalis */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        padding: 5px 10px !important;
        font-size: 14px !important;
    }
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
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

# TAB MENU
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    data = get_data()
    if not data:
        st.info("Loading Data...")
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
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <style>
                body {{ font-family: Arial; margin: 0; padding: 0; }}
                .inv-card {{ background: white; padding: 15px; width: 95%; max-width: 700px; margin: 5px auto; border: 1px solid #ddd; color: black; }}
                .h-img {{ width: 100%; height: auto; }}
                .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 16px; }}
                .info {{ width: 100%; font-size: 12px; font-weight: bold; margin-bottom: 10px; }}
                .table-scroll {{ overflow-x: auto; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; }}
                th, td {{ border: 1px solid black; padding: 6px; }}
                th {{ background: #f2f2f2; }}
                .terbilang {{ border: 1px solid black; padding: 8px; margin-top: 8px; font-size: 10px; font-style: italic; }}
                .footer {{ width: 100%; margin-top: 15px; font-size: 10px; }}
                .btn {{ width: 100%; background: #1A2A3A; color: white; padding: 12px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div id="box" class="inv-card">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="h-img">
                <div class="title">INVOICE</div>
                <table class="info">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                </table>
                <div class="table-scroll">
                    <table>
                        <thead>
                            <tr><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td>
                                <td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td>Rp {t_val:,}</td>
                            </tr>
                            <tr style="font-weight:bold;">
                                <td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                <table class="footer">
                    <tr>
                        <td style="width:60%;"><b>TRANSFER TO:</b><br>BCA 6720422334<br>ADITYA GAMA SAPUTRI<br>Finance: 082179799200</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:80px;"><br><b><u>KELVINITO JAYADI</u></b></td>
                    </tr>
                </table>
            </div>
            <button class="btn" onclick="dl()">📥 DOWNLOAD PDF A5</button>
            <script>
                function dl() {{
                    const e = document.getElementById('box');
                    html2pdf().set({{ margin: 0.1, filename: 'Inv_{selected_cust}.pdf', image: {{ type: 'jpeg', quality: 0.98 }}, html2canvas: {{ scale: 3, useCORS: true }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
        </body>
        </html>
        """
        components.html(invoice_html, height=750, scrolling=True)

with tab2:
    with st.form("input_form", clear_on_submit=True):
        r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 2])
        v_tgl = r1_c1.date_input("TANGGAL", datetime.now())
        v_cust = r1_c2.text_input("NAMA CUSTOMER")
        v_desc = r1_c3.text_input("DESKRIPSI BARANG")
        
        r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns([1, 1, 1, 1, 1.5])
        v_orig = r2_c1.text_input("DARI", value="SBY")
        v_dest = r2_c2.text_input("TUJUAN")
        v_kol = r2_c3.text_input("KOLLI")
        v_kg = r2_c4.text_input("WEIGHT")
        v_hrg = r2_c5.number_input("HARGA", 0)
        
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
