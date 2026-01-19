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

# 2. CSS FINAL (STABIL & TIDAK BIKIN LAYAR PUTIH)
st.markdown("""
    <style>
    /* Sembunyikan Header Bawaan */
    header[data-testid="stHeader"] { visibility: hidden; }
    
    /* BUAT TAB STICKY DENGAN CARA LEBIH AMAN */
    div[data-testid="stTabs"] {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: white;
        padding-top: 5px;
        margin-top: -20px; /* Merapatkan ke logo di atasnya */
        border-bottom: 2px solid #B8860B;
    }

    /* Warna Teks Tab */
    .stTabs [data-baseweb="tab"] p {
        color: #1A2A3A !important;
        font-weight: 800 !important;
        font-size: 16px;
    }

    /* PAKSA KURSOR JADI JARI */
    button, [role="button"], [data-baseweb="select"], .stSelectbox, input, .stTabs [data-baseweb="tab"] {
        cursor: pointer !important;
    }

    /* TOMBOL SIMPAN HOVER HIJAU */
    button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: black !important;
        font-weight: 900 !important;
        border: 2px solid black !important;
    }

    button[kind="primaryFormSubmit"]:hover {
        background: #28a745 !important;
        color: white !important;
    }

    /* STYLE FORM INPUT */
    [data-testid="stForm"] {
        background-color: #719dc9 !important;
        padding: 2rem !important;
        border-radius: 15px !important;
        border: 4px solid #B8860B !important;
    }

    .stWidgetLabel p { color: white !important; font-weight: 900 !important; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER (Diletakkan di luar sticky agar stabil)
# Menggunakan col untuk logo di kiri
col_logo, col_text = st.columns([1, 2])
with col_logo:
    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=350)
with col_text:
    st.markdown("<h2 style='margin-top: 20px; color: #1A2A3A;'>3G LOGISTICS SYSTEM</h2>", unsafe_allow_html=True)

# 4. TAMPILAN TABS (Hanya Tab yang nempel saat scroll)
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

# --- LOGIC DATA ---
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

def get_data():
    try:
        response = requests.get(f"{API_URL}?t={datetime.now().timestamp()}")
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

with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.write("---")
        f_col1, f_col2, f_col3 = st.columns([1, 1.2, 1.5])
        with f_col1:
            status_filter = st.radio("**STATUS:**", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
            df_filtered = df[df['status'] == status_filter] if status_filter != "Semua" else df
        with f_col2:
            cust_list = sorted(df_filtered['customer'].unique()) if not df_filtered.empty else []
            selected_cust = st.selectbox("**NAMA CUSTOMER:**", cust_list)
        with f_col3:
            if selected_cust:
                sub_df = df_filtered[df_filtered['customer'] == selected_cust].copy()
                sub_df['label'] = sub_df['date'].astype(str).str.split('T').str[0] + " | " + sub_df['description']
                selected_label = st.selectbox("**TRANSAKSI:**", sub_df['label'].tolist())

        if selected_cust and selected_label:
            row = sub_df[sub_df['label'] == selected_label].iloc[-1]
            b_val, h_val = extract_number(row['weight']), extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            kata_terbilang = terbilang(t_val) + " Rupiah"

            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <style>
                    body {{ background: #f0f0f0; padding: 10px; margin: 0; }}
                    #inv {{ background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial; }}
                    .header-img {{ width: 100%; height: auto; }}
                    .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px; }}
                    .info-table {{ width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold; }}
                    .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }}
                    .data-table th, .data-table td {{ border: 1px solid black; padding: 10px; }}
                    .footer-table {{ width: 100%; margin-top: 30px; font-size: 12px; line-height: 1.5; }}
                    .btn-dl {{ width: 750px; display: block; margin: 20px auto; background: #49bf59; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div id="inv">
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="header-img">
                    <div class="title">INVOICE</div>
                    <table class="info-table"><tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr></table>
                    <table class="data-table">
                        <tr><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        <tr><td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td></tr>
                        <tr style="font-weight:bold;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td></tr>
                    </table>
                    <div style="border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px;"><b>Terbilang:</b> {kata_terbilang}</div>
                    <table class="footer-table">
                        <tr>
                            <td style="width:65%; vertical-align:top;">
                                <b>TRANSFER TO :</b><br>BCA <b>6720422334</b><br><b>ADITYA GAMA SAPUTRI</b><br>
                                NB: Jika sudah transfer mohon konfirmasi ke<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Finance: <b>082179799200</b>
                            </td>
                            <td style="text-align:center; vertical-align:top;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</td>
                        </tr>
                    </table>
                </div>
                <button class="btn-dl" onclick="savePDF()">📥 DOWNLOAD PDF</button>
                <script>
                    function savePDF() {{
                        const e = document.getElementById('inv');
                        html2pdf().set({{ margin: 0, filename: 'Inv_{selected_cust}.pdf', image: {{ type: 'jpeg', quality: 0.98 }}, html2canvas: {{ scale: 3, useCORS: true }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                    }}
                </script>
            </body>
            </html>
            """
            components.html(invoice_html, height=850, scrolling=True)

with tab2:
    st.markdown("<h2 style='text-align: center; color: #1A2A3A; font-weight: 900;'>TAMBAH DATA PENGIRIMAN</h2>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: v_tgl = st.date_input("📅 TANGGAL")
        with r1c2: v_cust = st.text_input("🏢 CUSTOMER")
        with r1c3: v_desc = st.text_input("📦 ITEM")
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: v_orig = st.text_input("📍 ORIGIN")
        with r2c2: v_dest = st.text_input("🏁 DESTINATION")
        with r2c3: v_kol = st.text_input("📦 KOLLI")
        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1: v_harga = st.text_input("💰 HARGA")
        with r3c2: v_weight = st.text_input("⚖️ BERAT")
        with r3c3: v_status = st.selectbox("💳 STATUS", ["Belum Bayar", "Lunas"])
        
        submit = st.form_submit_button("🚀 SIMPAN SEKARANG")
        if submit:
            if v_cust and v_harga:
                try:
                    payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": float(v_harga), "weight": float(v_weight), "total": float(v_harga) * float(v_weight), "status": v_status}
                    requests.post(API_URL, json=payload)
                    st.cache_data.clear()
                    st.success("DATA TERSIMPAN!")
                    st.rerun()
                except: st.error("ERROR!")
