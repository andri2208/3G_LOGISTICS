import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", layout="wide")

# 2. CSS FINAL (RESPONSIF & TEKS HITAM TEBAL)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1rem !important; }

    div[data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 10px !important;
        padding: 10px 0 !important;
        background-color: white !important;
        border-bottom: 4px solid #B8860B !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6 !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        border: 1px solid #ddd !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #719dc9 !important;
        border: 2px solid #B8860B !important;
    }

    .stTabs [data-baseweb="tab"] p { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 14px !important;
    }

    .stTabs [aria-selected="true"] p { color: white !important; }

    [data-testid="stForm"] { 
        background-color: #719dc9 !important; 
        padding: 1.5rem !important; 
        border-radius: 15px !important; 
        border: 5px solid #B8860B !important; 
    }

    [data-testid="stForm"] label p { color: #000000 !important; font-weight: 900 !important; }

    @media (max-width: 640px) {
        div[data-testid="stHorizontalBlock"] { flex-direction: column !important; }
    }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://script.google.com/macros/s/AKfycbwI8Ep0hTn2zoDOuYMpjvD4G_coxfBRr1MzAtOgCcI-5ufcR4CllgZsA__ekfDb_BP_/exec"

def get_data():
    st.cache_data.clear()
    try:
        response = requests.get(f"{API_URL}?t={datetime.now().timestamp()}")
        return response.json() if response.status_code == 200 else []
    except: return []

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

def extract_number(value):
    if value is None or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
    return float(match[0]) if match else 0

st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)
tab1, tab2, tab3 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA", "🎭 FAKE INVOICE"])

# --- TAB 1: CETAK INVOICE (SESUAI DATA ASLI) ---
with tab1:
    if st.button("🔄 REFRESH DATA"): st.rerun()
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
            
            # KEMBALI KE LOGIKA ASLI (TIDAK DIRUBAH)
            b_val = extract_number(row['weight'])
            h_val = extract_number(row['harga'])
            total_asli = int(b_val * h_val) if b_val > 0 else int(h_val)
            
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            
            invoice_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <div id="inv" style="background: white; padding: 20px; width: 700px; margin: auto; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 18px;">INVOICE</div>
                <table style="width: 100%; font-size: 12px; font-weight: bold; margin-bottom: 10px;">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">NO: {row.get('inv_no', '-')}</td></tr>
                    <tr><td>DATE: {tgl_indo}</td><td style="text-align:right;">STATUS: {row['status'].upper()}</td></tr>
                </table>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center;">
                    <tr style="border: 1px solid black;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr style="border: 1px solid black;"><td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {total_asli:,}</td></tr>
                    <tr style="font-weight:bold; border: 1px solid black;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {total_asli:,}</td></tr>
                </table>
                <div style="border: 1px solid black; padding: 5px; margin-top: 5px; font-size: 11px;"><b>Terbilang:</b> {terbilang(total_asli)} Rupiah</div>
                <table style="width: 100%; margin-top: 20px; font-size: 11px;">
                    <tr>
                        <td style="width:60%;"><b>TRANSFER TO :</b><br>BCA 6720422334<br>ADITYA GAMA SAPUTRI</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:80px;"><br><b><u>KELVINITO JAYADI</u></b></td>
                    </tr>
                </table>
            </div>
            <button style="width: 700px; display: block; margin: 10px auto; background: #49bf59; color: white; padding: 10px; border-radius: 5px; border: none; font-weight: bold; cursor: pointer;" onclick="savePDF()">📥 DOWNLOAD PDF</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('inv');
                    html2pdf().set({{ margin: 0.2, filename: 'Inv_{row.get("inv_no", "3G")}.pdf', html2canvas: {{ scale: 2 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
            """
            components.html(invoice_html, height=750, scrolling=True)

# --- TAB 2: TAMBAH DATA ---
with tab2:
    st.markdown("<h3 style='text-align: center; color: black;'>TAMBAH DATA PENGIRIMAN</h3>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        v_tgl, v_cust, v_desc = c1.date_input("TANGGAL"), c2.text_input("CUSTOMER"), c3.text_input("ITEM")
        c4, c5, c6 = st.columns(3)
        v_orig, v_dest, v_kol = c4.text_input("ORIGIN"), c5.text_input("DESTINATION"), c6.text_input("KOLLI")
        c7, c8, c9 = st.columns(3)
        v_harga, v_weight, v_status = c7.text_input("HARGA"), c8.text_input("WEIGHT"), c9.selectbox("STATUS", ["Belum Bayar", "Lunas"])
        if st.form_submit_button("🚀 SIMPAN DATA"):
            payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": v_harga, "weight": v_weight, "status": v_status}
            requests.post(API_URL, json=payload)
            st.success("DATA TERSIMPAN!"); st.rerun()

# --- TAB 3: FAKE INVOICE (KHUSUS UNTUK TEMBAKAN HARGA KOSONG) ---
with tab3:
    st.markdown("<h3 style='text-align: center; color: black;'>INVOICE MANUAL (FAKE)</h3>", unsafe_allow_html=True)
    with st.form("fake_form"):
        f1, f2, f3 = st.columns(3)
        fk_no, fk_cust, fk_tgl = f1.text_input("NOMOR INVOICE", "3G/INV/2026/000"), f2.text_input("NAMA CUSTOMER"), f3.date_input("TANGGAL", datetime.now())
        f4, f5, f6 = st.columns(3)
        fk_item, fk_orig, fk_dest = f4.text_input("ITEM"), f5.text_input("ORIGIN"), f6.text_input("DESTINATION")
        f7, f8, f9 = st.columns(3)
        fk_kol, fk_weight, fk_total = f7.text_input("KOLLI"), f8.text_input("WEIGHT"), f9.number_input("TOTAL BAYAR (Rp)", value=6071000)
        if st.form_submit_button("✨ CETAK FAKE INVOICE"):
            terbilang_f = terbilang(fk_total) + " Rupiah"
            fake_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <div id="f-inv" style="background: white; padding: 20px; width: 700px; margin: auto; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 18px;">INVOICE</div>
                <table style="width: 100%; font-size: 12px; font-weight: bold; margin-bottom: 10px;">
                    <tr><td>CUSTOMER: {fk_cust.upper()}</td><td style="text-align:right;">NO: {fk_no}</td></tr>
                    <tr><td>DATE: {fk_tgl.strftime('%d/%m/%Y')}</td><td style="text-align:right;">STATUS: BELUM BAYAR</td></tr>
                </table>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center;">
                    <tr style="border: 1px solid black;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr style="border: 1px solid black;"><td>{fk_item.upper()}</td><td>{fk_orig.upper()}</td><td>{fk_dest.upper()}</td><td>{fk_kol}</td><td> </td><td>{fk_weight}</td><td style="font-weight:bold;">Rp {fk_total:,}</td></tr>
                    <tr style="font-weight:bold; border: 1px solid black;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {fk_total:,}</td></tr>
                </table>
                <div style="border: 1px solid black; padding: 5px; margin-top: 5px; font-size: 11px;"><b>Terbilang:</b> {terbilang_f}</div>
                <table style="width: 100%; margin-top: 20px; font-size: 11px;">
                    <tr>
                        <td style="width:60%;"><b>TRANSFER TO :</b><br>BCA 6720422334<br>ADITYA GAMA SAPUTRI</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:80px;"><br><b><u>KELVINITO JAYADI</u></b></td>
                    </tr>
                </table>
            </div>
            <button style="width: 700px; display: block; margin: 10px auto; background: #49bf59; color: white; padding: 10px; border-radius: 5px; border: none; font-weight: bold; cursor: pointer;" onclick="savePDF()">📥 DOWNLOAD FAKE PDF</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('f-inv');
                    html2pdf().set({{ margin: 0.2, filename: 'Fake_Inv_{fk_cust}.pdf', html2canvas: {{ scale: 2 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
            """
            components.html(fake_html, height=750, scrolling=True)
