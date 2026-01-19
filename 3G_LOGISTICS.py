import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", layout="wide")

# 2. CSS FINAL (KODE ASLI BAPAK)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.5rem !important; }

    /* PAKSA WARNA FORM JADI BIRU */
    [data-testid="stForm"] { 
        background-color: #719dc9 !important; 
        padding: 2.5rem !important; 
        border-radius: 20px !important; 
        border: 5px solid #B8860B !important; 
    }

    /* TEKS LABEL DI DALAM FORM: HITAM & TEBAL */
    [data-testid="stForm"] label p, 
    [data-testid="stForm"] .stMarkdown p { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 15px !important;
        text-shadow: none !important; 
        margin-bottom: 5px !important;
    }

    /* TEKS FILTER DI TAB CETAK */
    .stRadio label p, .stSelectbox label p {
        color: #000000 !important;
        font-weight: 900 !important;
        text-shadow: none !important;
    }

    /* GAYA TAB */
    div[data-testid="stTabs"] { 
        position: sticky; top: 0; z-index: 999; 
        background-color: white !important; 
        padding-top: 10px; 
        border-bottom: 4px solid #B8860B !important; 
        margin-bottom: 20px !important;
    }
    
    .stTabs [data-baseweb="tab"] p { 
        color: #1A2A3A !important; 
        font-weight: 900 !important; 
        font-size: 18px; 
    }

    /* TOMBOL SIMPAN */
    button[kind="primaryFormSubmit"] {
        background-color: #B8860B !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)

# 4. TABS (Menambahkan Tab Fake Invoice)
tab1, tab2, tab3 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA", "🎭 FAKE INVOICE"])

API_URL = "https://script.google.com/macros/s/AKfycbwI8Ep0hTn2zoDOuYMpjvD4G_coxfBRr1MzAtOgCcI-5ufcR4CllgZsA__ekfDb_BP_/exec"

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
        f1, f2, f3 = st.columns([1, 1.2, 1.5])
        with f1:
            st_filter = st.radio("**STATUS:**", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
            df_f = df[df['status'] == st_filter] if st_filter != "Semua" else df
        with f2:
            c_list = sorted(df_f['customer'].unique()) if not df_f.empty else []
            s_cust = st.selectbox("**NAMA CUSTOMER:**", c_list)
        with f3:
            if s_cust:
                sub_df = df_f[df_f['customer'] == s_cust].copy()
                sub_df['label'] = sub_df['date'].astype(str).str.split('T').str[0] + " | " + sub_df['description']
                s_label = st.selectbox("**TRANSAKSI:**", sub_df['label'].tolist())

        if s_cust and s_label:
            row = sub_df[sub_df['label'] == s_label].iloc[-1]
            b_val, h_val = extract_number(row['weight']), extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            
            invoice_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <div id="inv" style="background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                <table style="width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold;">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">NO: {row.get('inv_no', '-')}</td></tr>
                    <tr><td>DATE: {tgl_indo}</td><td style="text-align:right;">STATUS: {row['status'].upper()}</td></tr>
                </table>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center;">
                    <tr style="border: 1px solid black;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr><td style="border: 1px solid black;">{row['description']}</td><td style="border: 1px solid black;">{row['origin']}</td><td style="border: 1px solid black;">{row['destination']}</td><td style="border: 1px solid black;">{row['kolli']}</td><td style="border: 1px solid black;">Rp {int(h_val):,}</td><td style="border: 1px solid black;">{row['weight']}</td><td style="border: 1px solid black; font-weight:bold;">Rp {t_val:,}</td></tr>
                    <tr style="font-weight:bold;"><td colspan="6" style="border: 1px solid black; text-align:right;">TOTAL BAYAR</td><td style="border: 1px solid black;">Rp {t_val:,}</td></tr>
                </table>
                <div style="border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px;"><b>Terbilang:</b> {terbilang(t_val)} Rupiah</div>
                <table style="width: 100%; margin-top: 30px; font-size: 12px;">
                    <tr>
                        <td style="width:65%;"><b>TRANSFER TO :</b><br>BCA <b>6720422334</b><br><b>ADITYA GAMA SAPUTRI</b><br><br>NB: Konfirmasi Finance: 082179799200</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</td>
                    </tr>
                </table>
            </div>
            <button style="width: 750px; display: block; margin: 20px auto; background: #49bf59; color: white; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer;" onclick="savePDF()">📥 DOWNLOAD PDF</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('inv');
                    html2pdf().set({{ margin: 0, filename: 'Inv_{row.get("inv_no", "3G")}.pdf', html2canvas: {{ scale: 3 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
            """
            components.html(invoice_html, height=850, scrolling=True)

with tab2:
    st.markdown("<h2 style='text-align: center; color: #1A2A3A; font-weight: 900; margin-top: -10px;'>TAMBAH DATA PENGIRIMAN</h2>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        r1, r2, r3 = st.columns(3)
        v_tgl, v_cust, v_desc = r1.date_input("📅 TANGGAL"), r2.text_input("🏢 CUSTOMER"), r3.text_input("📦 ITEM")
        r4, r5, r6 = st.columns(3)
        v_orig, v_dest, v_kol = r4.text_input("📍 ORIGIN"), r5.text_input("🏁 DESTINATION"), r6.text_input("📦 KOLLI")
        r7, r8, r9 = st.columns(3)
        v_harga, v_weight, v_status = r7.text_input("💰 HARGA"), r8.text_input("⚖️ BERAT"), r9.selectbox("💳 STATUS", ["Belum Bayar", "Lunas"])
        if st.form_submit_button("🚀 SIMPAN SEKARANG"):
            payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": v_harga, "weight": v_weight, "status": v_status}
            requests.post(API_URL, json=payload)
            st.cache_data.clear()
            st.success("DATA TERSIMPAN!"); st.rerun()

# --- TAB 3: FAKE INVOICE (BARU) ---
with tab3:
    st.markdown("<h2 style='text-align: center; color: #1A2A3A; font-weight: 900; margin-top: -10px;'>INVOICE MANUAL (FAKE)</h2>", unsafe_allow_html=True)
    with st.form("fake_form"):
        f1, f2, f3 = st.columns(3)
        fk_no = f1.text_input("📄 NOMOR INVOICE", "3G/INV/2026/XXX")
        fk_cust = f2.text_input("🏢 NAMA CUSTOMER")
        fk_tgl = f3.date_input("📅 TANGGAL")
        f4, f5, f6 = st.columns(3)
        fk_item = f4.text_input("📦 ITEM")
        fk_orig = f5.text_input("📍 ORIGIN")
        fk_dest = f6.text_input("🏁 DESTINATION")
        f7, f8, f9 = st.columns(3)
        fk_kol = f7.text_input("📦 KOLLI")
        fk_weight = f8.text_input("⚖️ WEIGHT")
        fk_total = f9.number_input("💰 TOTAL BAYAR (Isi Manual)", value=6071000)
        
        if st.form_submit_button("✨ GENERATE FAKE INVOICE"):
            terbilang_f = terbilang(fk_total) + " Rupiah"
            fake_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <div id="f-inv" style="background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                <table style="width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold;">
                    <tr><td>CUSTOMER: {fk_cust.upper()}</td><td style="text-align:right;">NO: {fk_no}</td></tr>
                    <tr><td>DATE: {fk_tgl.strftime('%d/%m/%Y')}</td><td style="text-align:right;">STATUS: BELUM BAYAR</td></tr>
                </table>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center;">
                    <tr style="border: 1px solid black;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr><td style="border: 1px solid black;">{fk_item.upper()}</td><td style="border: 1px solid black;">{fk_orig.upper()}</td><td style="border: 1px solid black;">{fk_dest.upper()}</td><td style="border: 1px solid black;">{fk_kol}</td><td style="border: 1px solid black;"> </td><td style="border: 1px solid black;">{fk_weight}</td><td style="border: 1px solid black; font-weight:bold;">Rp {fk_total:,}</td></tr>
                    <tr style="font-weight:bold;"><td colspan="6" style="border: 1px solid black; text-align:right;">TOTAL BAYAR</td><td style="border: 1px solid black;">Rp {fk_total:,}</td></tr>
                </table>
                <div style="border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px;"><b>Terbilang:</b> {terbilang_f}</div>
                <table style="width: 100%; margin-top: 30px; font-size: 12px;">
                    <tr>
                        <td style="width:65%;"><b>TRANSFER TO :</b><br>BCA <b>6720422334</b><br><b>ADITYA GAMA SAPUTRI</b><br><br>NB: Konfirmasi Finance: 082179799200</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</td>
                    </tr>
                </table>
            </div>
            <button style="width: 750px; display: block; margin: 20px auto; background: #49bf59; color: white; padding: 15px; border-radius: 8px; font-weight: bold;" onclick="saveFakePDF()">📥 DOWNLOAD FAKE PDF</button>
            <script>
                function saveFakePDF() {{
                    const e = document.getElementById('f-inv');
                    html2pdf().set({{ margin: 0, filename: 'Fake_Inv.pdf', html2canvas: {{ scale: 3 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
            """
            components.html(fake_html, height=850, scrolling=True)
