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

# 2. CSS CUSTOM: HANYA UNTUK INPUT DATA (TIDAK GANGGU INVOICE)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; }

    /* PANEL INPUT DATA BERWARNA GELAP */
    [data-testid="stForm"] {
        background-color: #1A2A3A !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #B8860B !important;
    }

    /* TEKS LABEL JADI PUTIH TERANG */
    .stWidgetLabel p { 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        margin-bottom: -12px !important;
    }

    /* KOTAK INPUT TETAP PUTIH DENGAN TEKS HITAM */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 6px !important;
        height: 38px !important;
        font-weight: 700 !important;
    }
    
    /* FIX TEKS DALAM TANGGAL & SELECTBOX */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* TOMBOL SIMPAN EMAS */
    div.stButton > button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: #1A2A3A !important;
        font-weight: 900 !important;
        height: 45px;
        width: 100%;
        border: none !important;
    }

    /* Hapus Header Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    
    <div style="text-align: left; margin-bottom: 10px;">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="max-width: 250px;">
    </div>
    """, unsafe_allow_html=True)

# 3. LOGIC DATA (Sesuai Kode Bapak)
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
        col_f1, col_f2 = st.columns([1, 1.5]) 
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

            # --- INVOICE ASLI BAPAK (100% TIDAK DIUBAH) ---
            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <style>
                    body {{ background: #f0f0f0; padding: 10px; }}
                    #inv {{ background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial; }}
                    .header-img {{ width: 100%; height: auto; }}
                    .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px; }}
                    .info-table {{ width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold; }}
                    .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }}
                    .data-table th, .data-table td {{ border: 1px solid black; padding: 10px; }}
                    .data-table th {{ background-color: #f2f2f2; }}
                    .terbilang {{ border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px; font-style: italic; }}
                    .footer-table {{ width: 100%; margin-top: 30px; font-size: 12px; line-height: 1.5; }}
                    .btn-dl {{ width: 750px; display: block; margin: 20px auto; background: #1A2A3A; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }}
                </style>
            </head>
            <body>
                <div id="inv">
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="header-img">
                    <div class="title">INVOICE</div>
                    <table class="info-table">
                        <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                    </table>
                    <table class="data-table">
                        <thead>
                            <tr><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td>
                                <td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td>
                            </tr>
                            <tr style="font-weight:bold;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td></tr>
                        </tbody>
                    </table>
                    <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                    <table class="footer-table">
                        <tr>
                            <td style="width:65%; vertical-align:top;">
                                <b>TRANSFER TO :</b><br>
                                BCA <b>6720422334</b><br>
                                <b>ADITYA GAMA SAPUTRI</b><br>
                                NB: Jika sudah transfer mohon konfirmasi ke<br>
                                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Finance: <b>082179799200</b>
                            </td>
                            <td style="text-align:center; vertical-align:top;">
                                Sincerely,<br>
                                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px; margin: 5px 0;"><br>
                                <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                            </td>
                        </tr>
                    </table>
                </div>
                <button class="btn-dl" onclick="savePDF()">📥 DOWNLOAD PDF A5</button>
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
    st.markdown("<h4 style='text-align: center; color: #1A2A3A; margin: 0;'>NEW DISPATCH ENTRY</h4>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("📅 TANGGAL PENGIRIMAN")
        with c2: v_cust = st.text_input("🏢 NAMA CUSTOMER")
        v_desc = st.text_input("📦 KETERANGAN BARANG")
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("📍 ASAL (ORIGIN)")
        with c4: v_dest = st.text_input("🏁 TUJUAN (DESTINATION)")
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("📦 JUMLAH KOLLI")
        with c6: v_harga = st.text_input("💰 HARGA PER KG")
        with c7: v_weight = st.text_input("⚖️ BERAT TOTAL")
        v_status = st.selectbox("💳 STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])
        submit = st.form_submit_button("🚀 SIMPAN DATA KE GOOGLE SHEETS")
        if submit:
            if v_cust and v_harga:
                try:
                    payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": float(v_harga), "weight": float(v_weight), "total": float(v_harga) * float(v_weight), "status": v_status}
                    requests.post(API_URL, json=payload)
                    st.success("DATA BERHASIL DISIMPAN!")
                    st.rerun()
                except: st.error("CEK INPUT ANGKA!")
