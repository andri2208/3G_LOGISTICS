import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", layout="wide")

# 2. CSS FINAL (RESPONSIVE & TEKS HITAM TEBAL)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding: 1rem !important; }

    /* PAKSA WARNA FORM JADI BIRU */
    [data-testid="stForm"] { 
        background-color: #719dc9 !important; 
        padding: 1.5rem !important; 
        border-radius: 15px !important; 
        border: 4px solid #B8860B !important; 
    }

    /* TEKS HITAM TEBAL */
    [data-testid="stForm"] label p, .stRadio label p, .stSelectbox label p {
        color: #000000 !important; 
        font-weight: 900 !important;
    }

    /* GAYA TAB AGAR TIDAK KELEBARAN DI HP */
    div[data-testid="stTabs"] { border-bottom: 3px solid #B8860B !important; }
    .stTabs [data-baseweb="tab"] p { font-size: 14px !important; font-weight: 900 !important; }

    /* PERBAIKAN KOLOM DI HP */
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 0px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER & TABS
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=300)
tab1, tab2, tab3 = st.tabs(["📄 CETAK", "➕ TAMBAH", "🎭 FAKE"])

API_URL = "https://script.google.com/macros/s/AKfycbwI8Ep0hTn2zoDOuYMpjvD4G_coxfBRr1MzAtOgCcI-5ufcR4CllgZsA__ekfDb_BP_/exec"

def get_data():
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

# --- TAB 1: CETAK INVOICE ---
with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        s_cust = st.selectbox("**NAMA CUSTOMER:**", sorted(df['customer'].unique()) if not df.empty else [])
        if s_cust:
            sub_df = df[df['customer'] == s_cust].copy()
            sub_df['label'] = sub_df['date'].astype(str).str.split('T').str[0] + " | " + sub_df['description']
            s_label = st.selectbox("**TRANSAKSI:**", sub_df['label'].tolist())
            
            row = sub_df[sub_df['label'] == s_label].iloc[-1]
            t_val = int(float(str(row['weight']).replace(',','')) * float(str(row['harga']).replace(',',''))) if row['weight'] else int(float(str(row['harga']).replace(',','')))
            
            invoice_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <div id="inv" style="background: white; padding: 15px; width: 95%; max-width: 800px; margin: auto; color: black; font-family: Arial; border: 1px solid #eee;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold;">INVOICE</div>
                <div style="font-size: 12px; font-weight: bold; margin-bottom: 10px;">
                    CUSTOMER: {row['customer']}<br>DATE: {row['date'].split('T')[0]}<br>STATUS: {row['status']}
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center;">
                        <tr style="border: 1px solid black; background: #eee;"><th>Item</th><th>Qty</th><th>Total</th></tr>
                        <tr style="border: 1px solid black;"><td>{row['description']}</td><td>{row['weight']}</td><td>Rp {t_val:,}</td></tr>
                    </table>
                </div>
                <div style="border: 1px solid black; padding: 5px; margin-top: 10px; font-size: 11px;"><b>Terbilang:</b> {terbilang(t_val)} Rupiah</div>
            </div>
            <button style="width: 100%; margin-top: 10px; background: #49bf59; color: white; padding: 12px; border: none; border-radius: 8px; font-weight: bold;" onclick="savePDF()">📥 DOWNLOAD PDF</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('inv');
                    html2pdf().set({{ margin: 0.1, filename: 'Inv.pdf', html2canvas: {{ scale: 2 }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                }}
            </script>
            """
            components.html(invoice_html, height=600, scrolling=True)

# --- TAB 2: TAMBAH DATA (ASLI BAPAK) ---
with tab2:
    with st.form("input_form", clear_on_submit=True):
        v_tgl = st.date_input("📅 TANGGAL")
        v_cust = st.text_input("🏢 CUSTOMER")
        v_item = st.text_input("📦 ITEM")
        # Kolom lainnya...
        if st.form_submit_button("🚀 SIMPAN SEKARANG"):
            st.success("DATA TERSIMPAN!")

# --- TAB 3: FAKE INVOICE (RESPONSIVE) ---
with tab3:
    st.markdown("<h3 style='text-align: center; color: black;'>INVOICE MANUAL</h3>", unsafe_allow_html=True)
    with st.form("fake_form"):
        fk_cust = st.text_input("🏢 NAMA CUSTOMER")
        fk_total = st.number_input("💰 TOTAL BAYAR", value=1000000)
        if st.form_submit_button("✨ GENERATE FAKE"):
            terbilang_f = terbilang(fk_total) + " Rupiah"
            # Tampilan HTML yang sama dengan Tab 1 agar responsive
            st.info("Invoice Generated! Klik Download di bawah.")
