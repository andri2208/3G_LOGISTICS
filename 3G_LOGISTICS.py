import streamlit as st
import pd as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# --- CSS: HEADER AMAN, BACKGROUND ELEGAN, LABEL TEBAL ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .block-container { padding-top: 4rem !important; }

    /* Header Image Tengah */
    [data-testid="stImage"] img {
        max-width: 550px !important; 
        margin: 0 auto;
        display: block;
        border-radius: 8px;
    }

    /* Label Input Sangat Tebal */
    .stWidgetLabel p {
        font-weight: 900 !important;
        font-size: 14px !important;
        color: #1A2A3A !important;
    }
    
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #BCC6CC !important;
        border-radius: 8px !important;
    }

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

# Header Utama Web
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png")

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

        # HTML INVOICE DENGAN PERBAIKAN LINK GAMBAR
        invoice_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <style>
                .container {{ background: white; padding: 20px; max-width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial, sans-serif; }}
                .header-img {{ width: 100%; height: auto; display: block; }}
                .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 20px; }}
                .info-table {{ width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold; }}
                .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }}
                .data-table th, .data-table td {{ border: 1px solid black; padding: 8px; }}
                .data-table th {{ background-color: #f2f2f2; }}
                .terbilang {{ border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px; font-style: italic; }}
                .footer-table {{ width: 100%; margin-top: 30px; font-size: 12px; }}
                .btn-dl {{ width: 100%; background: #1A2A3A; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div id="invoice-box" class="container">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" class="header-img">
                <div class="title">INVOICE</div>
                <table class="info-table">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                </table>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td>
                            <td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td>Rp {t_val:,}</td>
                        </tr>
                        <tr style="font-weight:bold;">
                            <td colspan="6" style="text-align:right;">YANG HARUS DIBAYAR</td><td>Rp {t_val:,}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                <table class="footer-table">
                    <tr>
                        <td style="width:60%; vertical-align:top;">
                            <b>TRANSFER TO :</b><br>Bank Central Asia <b>6720422334</b><br>A/N <b>ADITYA GAMA SAPUTRI</b><br><br>
                            <i>NB : Jika sudah transfer mohon konfirmasi ke Finance <b>082179799200</b></i>
                        </td>
                        <td style="text-align:center;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:130px; margin: 10px 0;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            <button class="btn-dl" onclick="generatePDF()">📥 DOWNLOAD INVOICE (UKURAN A5)</button>
            <script>
                function generatePDF() {{
                    const element = document.getElementById('invoice-box');
                    const opt = {{
                        margin: 0,
                        filename: 'Inv_{selected_cust}.pdf',
                        image: {{ type: 'jpeg', quality: 0.98 }},
                        html2canvas: {{ scale: 3, useCORS: true, logging: false }},
                        jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }}
                    }};
                    html2pdf().set(opt).from(element).save();
                }}
            </script>
        </body>
        </html>
        """
        components.html(invoice_html, height=850, scrolling=True)

with tab2:
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 2, 2])
        v_tgl = c1.date_input("TANGGAL", datetime.now())
        v_cust = c2.text_input("NAMA CUSTOMER")
        v_desc = c3.text_input("DESKRIPSI BARANG")
        
        c4, c5, c6, c7, c8 = st.columns([1, 1, 1, 1, 1.5])
        v_orig = c4.text_input("DARI", value="SBY")
        v_dest = c5.text_input("TUJUAN")
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
                st.success(f"Berhasil Simpan! Rp {total_db:,}")
                st.cache_data.clear()
            except:
                st.error("Gagal!")
