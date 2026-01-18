import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# --- CSS DARK MODE KONTRAS TINGGI ---
st.markdown("""
    <style>
    /* Latar belakang utama aplikasi */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Mempertebal label dan warna putih cerah agar kontras */
    .stWidgetLabel p {
        font-weight: 900 !important;
        font-size: 16px !important;
        color: #00FF41 !important; /* Warna Hijau Matrix agar sangat kontras */
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Box Input: Latar Hitam, Border Abu Terang */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #161B22 !important;
        color: white !important;
        border: 2px solid #30363D !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* Saat kolom diklik (Focus) */
    .stTextInput input:focus {
        border-color: #00FF41 !important;
        background-color: #0D1117 !important;
    }

    /* Mempercantik Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0E1117;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #161B22;
        border-radius: 5px 5px 0px 0px;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF41 !important;
        color: black !important;
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

st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    data = get_data()
    if not data:
        st.info("Menunggu data...")
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
                body {{ font-family: Arial, sans-serif; background-color: #161B22; padding: 10px; }}
                .container {{ background: white; padding: 15px; max-width: 750px; margin: auto; border: 1px solid #ccc; color: black; }}
                .header-img {{ width: 100%; height: auto; }}
                .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 1.2rem; }}
                .info-table {{ width: 100%; margin-bottom: 10px; font-size: 12px; font-weight: bold; }}
                .data-table {{ width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; }}
                .data-table th, .data-table td {{ border: 1px solid black; padding: 8px; }}
                .data-table th {{ background-color: #eee; }}
                .terbilang {{ border: 1px solid black; padding: 8px; margin-top: 10px; font-size: 11px; font-style: italic; }}
                .footer {{ width: 100%; margin-top: 20px; font-size: 11px; }}
                .btn-download {{ width: 100%; background: #00FF41; color: black; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="container" id="invoice-card">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" class="header-img">
                <div class="title">INVOICE</div>
                <table class="info-table">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                </table>
                <div style="overflow-x: auto;">
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
                            <tr style="font-weight:bold; background:#f9f9f9;">
                                <td colspan="6" style="text-align:right;">YANG HARUS DIBAYAR</td><td>Rp {t_val:,}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                
                <table class="footer">
                    <tr>
                        <td style="width:60%; vertical-align: top;">
                            <b>TRANSFER TO :</b><br>
                            Bank Central Asia <b>6720422334</b><br>
                            A/N <b>ADITYA GAMA SAPUTRI</b><br><br>
                            <i>NB : Jika sudah transfer mohon konfirmasi ke<br>
                            Finance <b>082179799200</b></i>
                        </td>
                        <td style="text-align:center; vertical-align: top;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:110px;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            <button class="btn-download" onclick="downloadA5()">📥 DOWNLOAD INVOICE (A5)</button>

            <script>
                function downloadA5() {{
                    const element = document.getElementById('invoice-card');
                    const opt = {{
                        margin: 0.1,
                        filename: 'Invoice_{selected_cust}.pdf',
                        image: {{ type: 'jpeg', quality: 0.98 }},
                        html2canvas: {{ scale: 3, useCORS: true }},
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
    st.markdown("<h2 style='color: white;'>➕ DATA ENTRY</h2>", unsafe_allow_html=True)
    with st.form("form_db", clear_on_submit=True):
        col1, col2 = st.columns(2)
        v_tgl = col1.date_input("TANGGAL PENGIRIMAN", datetime.now())
        v_cust = col1.text_input("NAMA CUSTOMER")
        v_desc = col1.text_input("DESKRIPSI BARANG")
        v_orig = col2.text_input("ORIGIN (ASAL)", value="SBY")
        v_dest = col2.text_input("DESTINATION (TUJUAN)")
        v_kol = col2.text_input("JUMLAH KOLLI")
        v_kg = col2.text_input("WEIGHT / BERAT")
        v_hrg = col2.number_input("HARGA SATUAN", 0)
        
        st.markdown("---")
        if st.form_submit_button("💾 SIMPAN DATA KE SISTEM"):
            w_num = extract_number(v_kg)
            total_db = int(w_num * v_hrg) if w_num > 0 else int(v_hrg)
            payload = {
                "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                "harga": v_hrg, "weight": v_kg, "total": total_db
            }
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"✅ Tersimpan! Total: Rp {total_db:,}")
                st.cache_data.clear()
            except:
                st.error("❌ Koneksi Gagal.")
