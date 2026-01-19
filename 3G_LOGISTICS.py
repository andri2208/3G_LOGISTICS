import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics Pro", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", 
    layout="wide"
)

# 2. CSS CUSTOM RESPONSIVE (TIDAK MERUSAK STRUKTUR INVOICE)
st.markdown("""
    <style>
    /* Dasar Web agar pas di semua layar */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* PANEL INPUT RESPONSIVE */
    [data-testid="stForm"] {
        background-color: #719dc9 !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border: 2px solid #B8860B !important;
        width: 100% !important;
    }

    /* TEKS LABEL PUTIH (Tetap Tajam) */
    .stWidgetLabel p { 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        margin-bottom: -10px !important;
    }

    /* INPUT BOX (Lebar Otomatis) */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    
    /* Fix Teks Hitam di Dropdown & Tanggal */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* TOMBOL SIMPAN (Lebar Penuh di Mobile) */
    div.stButton > button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: #1A2A3A !important;
        font-weight: 900 !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }

    /* Responsive Header Image */
    .header-logo {
        max-width: 250px;
        width: 100%;
        height: auto;
    }

    /* Sembunyikan Header Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    
    <div style="text-align: left; margin-bottom: 10px;">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

# 3. LOGIC DATA
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}")
        return response.json() if response.status_code == 200 else []
    except: return []

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', '').replace('Kg', '').replace('kg', ''))
    return float(match[0]) if match else 0

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

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.write("---")
        # Kolom Filter dibuat Responsive
        col_f1, col_f2 = st.columns([1, 1]) 
        with col_f1:
            status_filter = st.radio("Status:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
        with col_f2:
            df_filtered = df[df['status'] == status_filter] if status_filter != "Semua" else df
            selected_cust = st.selectbox("Pilih Customer:", sorted(df_filtered['customer'].unique())) if not df_filtered.empty else None
        
        if selected_cust and not df_filtered.empty:
            row = df_filtered[df_filtered['customer'] == selected_cust].iloc[-1]
            b_val = extract_number(row['weight'])
            h_val = extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            kata_terbilang = terbilang(t_val) + " Rupiah"

            # INVOICE DENGAN CSS RESPONSIVE (MAX-WIDTH 100%)
            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <style>
                    body {{ background: #f0f0f0; padding: 5px; margin: 0; }}
                    #inv {{ 
                        background: white; 
                        padding: 15px; 
                        max-width: 750px; 
                        width: 95%; 
                        margin: auto; 
                        border: 1px solid #ccc; 
                        color: black; 
                        font-family: Arial, sans-serif; 
                    }}
                    .header-img {{ width: 100%; height: auto; }}
                    .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 18px; }}
                    .info-table {{ width: 100%; margin-bottom: 10px; font-size: 12px; font-weight: bold; }}
                    .data-table {{ width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; }}
                    .data-table th, .data-table td {{ border: 1px solid black; padding: 6px; }}
                    .data-table th {{ background-color: #f2f2f2; }}
                    .terbilang {{ border: 1px solid black; padding: 8px; margin-top: 10px; font-size: 11px; font-style: italic; }}
                    .footer-table {{ width: 100%; margin-top: 20px; font-size: 11px; line-height: 1.4; }}
                    .btn-dl {{ 
                        max-width: 750px; 
                        width: 95%; 
                        display: block; 
                        margin: 15px auto; 
                        background: #49bf59; 
                        color: white; 
                        padding: 12px; 
                        border: none; 
                        border-radius: 8px; 
                        font-weight: bold; 
                        cursor: pointer; 
                        font-size: 14px; 
                    }}
                </style>
            </head>
            <body>
                <div id="inv">
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="header-img">
                    <div class="title">INVOICE</div>
                    <table class="info-table">
                        <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                    </table>
                    <div style="overflow-x:auto;">
                        <table class="data-table">
                            <thead>
                                <tr><th>Desc</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td>
                                    <td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td>
                                </tr>
                                <tr style="font-weight:bold;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                    <table class="footer-table">
                        <tr>
                            <td style="width:60%; vertical-align:top;">
                                <b>TRANSFER TO :</b><br>
                                BCA <b>6720422334</b><br>
                                <b>ADITYA GAMA SAPUTRI</b><br>
                                NB: Jika sudah transfer mohon konfirmasi ke<br>
                                Finance: <b>082179799200</b>
                            </td>
                            <td style="text-align:center; vertical-align:top;">
                                Sincerely,<br>
                                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:90px; margin: 5px 0;"><br>
                                <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                            </td>
                        </tr>
                    </table>
                </div>
                <button class="btn-dl" onclick="savePDF()">📥 DOWNLOAD PDF</button>
                <script>
                    function savePDF() {{
                        const e = document.getElementById('inv');
                        const opt = {{
                            margin: 0.2,
                            filename: 'Inv_{selected_cust}.pdf',
                            image: {{ type: 'jpeg', quality: 0.98 }},
                            html2canvas: {{ scale: 2, useCORS: true }},
                            jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }}
                        }};
                        html2pdf().set(opt).from(e).save();
                    }}
                </script>
            </body>
            </html>
            """
            components.html(invoice_html, height=800, scrolling=True)

with tab2:
    st.markdown("<h4 style='text-align: center; color: #1A2A3A; margin-top: -10px;'>NEW ENTRY</h4>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        # Column otomatis jadi baris jika di layar kecil (HP)
        c1, c2 = st.columns([1, 1])
        with c1: v_tgl = st.date_input("📅 TANGGAL PENGIRIMAN")
        with c2: v_cust = st.text_input("🏢 NAMA CUSTOMER")
        
        v_desc = st.text_input("📦 KETERANGAN BARANG")
        
        c3, c4 = st.columns([1, 1])
        with c3: v_orig = st.text_input("📍 ASAL (ORIGIN)")
        with c4: v_dest = st.text_input("🏁 TUJUAN (DESTINATION)")
        
        c5, c6, c7 = st.columns([1, 1, 1])
        with c5: v_kol = st.text_input("📦 KOLLI")
        with c6: v_harga = st.text_input("💰 HARGA")
        with c7: v_weight = st.text_input("⚖️ BERAT")
        
        v_status = st.selectbox("💳 STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])
        
        submit = st.form_submit_button("🚀 SIMPAN DATA")
        
        if submit:
            if v_cust and v_harga:
                try:
                    payload = {
                        "date": str(v_tgl), 
                        "customer": v_cust.upper(), 
                        "description": v_desc.upper(), 
                        "origin": v_orig.upper(), 
                        "destination": v_dest.upper(), 
                        "kolli": v_kol, 
                        "harga": float(v_harga), 
                        "weight": float(v_weight), 
                        "total": float(v_harga) * float(v_weight), 
                        "status": v_status
                    }
                    requests.post(API_URL, json=payload)
                    st.success("DATA BERHASIL DISIMPAN!")
                    st.rerun()
                except: st.error("CEK INPUT ANGKA PADA HARGA/BERAT!")
