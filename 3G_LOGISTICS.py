import streamlit as st
import pandas as pd  # <--- INI SUDAH SAYA PERBAIKI
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", layout="wide")

# 2. CSS FINAL (Sesuai permintaan Bapak)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 2rem !important; }
    [data-testid="stImage"] { margin-bottom: 10px !important; margin-top: -10px !important; }
    div[data-testid="stTabs"] { position: sticky; top: 0; z-index: 999; background: white; padding-top: 15px; border-bottom: 3px solid #B8860B; }
    .stTabs [data-baseweb="tab"] p { color: #1A2A3A !important; font-weight: 800 !important; font-size: 18px; }
    [data-testid="stForm"] { background: #719dc9 !important; padding: 3rem !important; border-radius: 20px !important; border: 4px solid #B8860B !important; margin-top: 20px !important; }
    .stWidgetLabel p { color: white !important; font-weight: 900 !important; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. AREA HEADER
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

# GANTI DENGAN URL DEPLOY TERBARU BAPAK
API_URL = "https://script.google.com/macros/s/AKfycbzQYctEFdKCwonDhbn7fOVtXKTiI9i53HBa-q0BzNc8F9aevvo0et-NAM4p-GGHqREUvw/exec"

def get_data():
    try:
        response = requests.get(f"{API_URL}?t={datetime.now().timestamp()}")
        return response.json() if response.status_code == 200 else []
    except: return []

def extract_number(value):
    if value is None or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
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
        st.write("###")
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
            b_val = extract_number(row['weight'])
            h_val = extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
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
                    <table class="info-table"><tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_raw}</td></tr></table>
                    <table class="data-table">
                        <tr><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        <tr><td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td></tr>
                        <tr style="font-weight:bold;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td></tr>
                    </table>
                    <div style="border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px;"><b>Terbilang:</b> {kata_terbilang}</div>
                  <table class="footer-table">
    <tr>
        <td style="width:65%; vertical-align:top;">
            <b>TRANSFER TO :</b><br>
            BCA <b>6720422334</b><br>
            <b>ADITYA GAMA SAPUTRI</b><br><br>
            <i>NB: Jika sudah transfer mohon konfirmasi ke<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Finance: <b>082179799200</b></i>
        </td>
        <td style="text-align:center; vertical-align:top;">
            Sincerely,<br>
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px;"><br>
            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
        </td>
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
    st.markdown("<h2 style='text-align: center; color: white; font-weight: 900;'>TAMBAH DATA PENGIRIMAN</h2>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        r1, r2, r3 = st.columns(3)
        v_tgl = r1.date_input("📅 TANGGAL")
        v_cust = r2.text_input("🏢 CUSTOMER")
        v_desc = r3.text_input("📦 ITEM")
        r4, r5, r6 = st.columns(3)
        v_orig = r4.text_input("📍 ORIGIN")
        v_dest = r5.text_input("🏁 DESTINATION")
        v_kol = r6.text_input("📦 KOLLI")
        r7, r8, r9 = st.columns(3)
        v_harga = r7.text_input("💰 HARGA (Angka saja)")
        v_weight = r8.text_input("⚖️ BERAT (Angka saja)")
        v_status = r9.selectbox("💳 STATUS", ["Belum Bayar", "Lunas"])
        
        if st.form_submit_button("🚀 SIMPAN SEKARANG"):
            if v_cust and v_harga:
                payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": v_harga, "weight": v_weight, "status": v_status}
                requests.post(API_URL, json=payload)
                st.cache_data.clear()
                st.success("DATA TERSIMPAN!")
                st.rerun()



