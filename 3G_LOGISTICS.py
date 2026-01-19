import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", 
    layout="wide"
)

# 2. CSS CUSTOM UNTUK TAMPILAN WEB PRO (PERBAIKAN KOTAK DOBEL)
st.markdown("""
    <style>
    /* Dasar Web */
    .stApp { background-color: #FDFCF0; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem !important; }
    
    /* Header */
    .custom-header { text-align: left; margin-bottom: 20px; }
    .custom-header img { width: 100%; max-width: 400px; height: auto; }

    /* FIX KOTAK DOBEL: Menghapus border bawaan container luar Streamlit */
    div[data-baseweb="calendar"], div[data-baseweb="select"], .stNumberInput div {
        border: none !important;
    }

    /* STYLING INPUT DATA JADI PRO - Ramping & Tanpa Double Border */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        height: 42px !important;
        font-size: 14px !important;
        transition: all 0.2s ease;
    }
    
    /* Efek Focus */
    .stTextInput input:focus, .stDateInput div[data-baseweb="input"]:focus-within {
        border-color: #1A2A3A !important;
        box-shadow: 0 0 0 1px #1A2A3A !important;
    }

    /* Label Input - Dibuat lebih bersih */
    .stWidgetLabel p { 
        font-weight: 700 !important; 
        color: #4B5563 !important; 
        font-size: 11px !important;
        text-transform: uppercase;
        margin-bottom: -10px !important;
    }

    /* Tab Header */
    .stTabs [data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1A2A3A !important;
        border-bottom: 3px solid #1A2A3A !important;
    }

    /* Tombol Simpan Pro */
    div.stButton > button {
        background-color: #1A2A3A !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 6px !important;
        width: 100%;
        height: 50px;
        border: none;
        margin-top: 20px;
    }

    /* Hide Streamlit Decor */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stStatusWidget"] { display: none !important; }
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# 3. LOGIC DATA (URL API Bapak)
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1, show_spinner=False)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            all_data = response.json()
            for item in all_data:
                if 'status' not in item: item['status'] = "Belum Bayar"
            return all_data
        return []
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
    if not data:
        st.info("Menunggu data dari Google Sheets...")
    else:
        df = pd.DataFrame(data)
        st.write("---")
        col_f1, col_f2 = st.columns([1, 1.5]) 
        with col_f1:
            status_filter = st.radio("Status:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
        with col_f2:
            df_filtered = df[df['status'] == status_filter] if status_filter != "Semua" else df
            selected_cust = st.selectbox("Pilih Customer:", sorted(df_filtered['customer'].unique())) if not df_filtered.empty else None
        st.write("---")
        
        if selected_cust and not df_filtered.empty:
            row = df_filtered[df_filtered['customer'] == selected_cust].iloc[-1]
            b_val = extract_number(row['weight'])
            h_val = extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            kata_terbilang = terbilang(t_val) + " Rupiah"

            # INVOICE HTML (100% ASLI TETAP DIJAGA)
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
    st.markdown("<h3 style='text-align: center; color: #1A2A3A; margin-bottom: 25px;'>NEW DISPATCH ENTRY</h3>", unsafe_allow_html=True)
    
    with st.form("input_form", clear_on_submit=True):
        # BARIS 1
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("📅 TANGGAL PENGIRIMAN", value=datetime.now())
        with c2: v_cust = st.text_input("🏢 NAMA CUSTOMER", placeholder="Contoh: PT. MAJU JAYA")

        # BARIS 2
        v_desc = st.text_input("📦 KETERANGAN BARANG", placeholder="Contoh: SPAREPART MESIN")

        # BARIS 3
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("📍 ASAL (ORIGIN)", placeholder="SBY")
        with c4: v_dest = st.text_input("🏁 TUJUAN (DESTINATION)", placeholder="PAPUA")

        # BARIS 4
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("📦 KOLLI", placeholder="0")
        with c6: v_harga = st.text_input("💰 HARGA / KG", placeholder="0")
        with c7: v_weight = st.text_input("⚖️ BERAT (KG)", placeholder="0")

        # BARIS 5
        v_status = st.selectbox("💳 STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])

        # TOMBOL
        submit = st.form_submit_button("🚀 SIMPAN DATA KE DATABASE")

        if submit:
            if not v_cust or not v_harga:
                st.error("Nama Customer dan Harga wajib diisi!")
            else:
                try:
                    h_num = float(v_harga)
                    w_num = float(v_weight) if v_weight else 0
                    payload = {
                        "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                        "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                        "harga": h_num, "weight": w_num, "total": h_num * w_num, "status": v_status
                    }
                    resp = requests.post(API_URL, json=payload)
                    if resp.status_code == 200:
                        st.success(f"Berhasil Tersimpan!")
                        st.rerun()
                    else: st.error("Gagal simpan.")
                except:
                    st.error("Input Harga/Berat harus angka!")
