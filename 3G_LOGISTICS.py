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

# 2. CSS SAKTI: DESAIN PROFESIONAL & ELEGAN
st.markdown("""
    <style>
    /* Background & Font */
    .stApp { background-color: #FDFCF0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Header & Navigasi */
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    
    /* TEKS LABEL PROFESIONAL */
    .stWidgetLabel p { 
        font-weight: 700 !important; 
        color: #2C3E50 !important; 
        font-size: 13px !important;
        margin-bottom: -10px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* KOLOM INPUT ELEGAN */
    .stTextInput input, .stDateInput div, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D5DBDB !important; /* Garis tipis modern */
        border-radius: 6px !important;
        font-weight: 500 !important;
        color: #1C2833 !important;
        height: 38px !important;
        transition: all 0.3s ease;
    }

    /* Efek Saat Input Diklik (Focus) */
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #3498DB !important;
        box-shadow: 0 0 5px rgba(52, 152, 219, 0.3) !important;
    }

    /* Tombol Simpan PRO */
    div.stButton > button {
        background-color: #1A2A3A !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5rem 2rem !important;
        transition: 0.3s;
        width: 100%;
        height: 38px;
    }
    
    div.stButton > button:hover {
        background-color: #2C3E50 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    /* Rapat & Minimalis */
    .stVerticalBlock { gap: 0.6rem !important; }
    .stRadio > div { margin-top: -20px; gap: 20px; }
    
    /* Header Gambar */
    .custom-header { text-align: left; margin-bottom: 5px; }
    .custom-header img { width: 100%; max-width: 380px; height: auto; }
    
    /* Sembunyikan Running Widget */
    [data-testid="stStatusWidget"] { display: none !important; }
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# URL API
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1, show_spinner=False)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            all_data = response.json()
            if not all_data: return []
            for item in all_data:
                if 'status' not in item: item['status'] = "Belum Bayar"
            return all_data
        return []
    except:
        return []

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

# --- TABS ---
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

# --- TAB 1: CETAK INVOICE ---
with tab1:
    raw_data = get_data()
    if not raw_data:
        st.info("Menghubungkan ke Database...")
    else:
        df = pd.DataFrame(raw_data)
        st.write("---")
        col_f1, col_f2 = st.columns([1, 1.5]) 
        with col_f1:
            status_filter = st.radio("", ["Semua", "Belum Bayar", "Lunas"], horizontal=True, label_visibility="collapsed")
        with col_f2:
            df_filtered = df[df['status'] == status_filter] if status_filter != "Semua" else df
            if not df_filtered.empty:
                selected_cust = st.selectbox("", sorted(df_filtered['customer'].unique()), label_visibility="collapsed")
            else:
                selected_cust = None
                st.caption("Tidak ada data")
        
        st.write("---")
        
        if selected_cust:
            row = df_filtered[df_filtered['customer'] == selected_cust].iloc[-1]
            b_val = extract_number(row.get('weight', 0))
            h_val = extract_number(row.get('harga', 0))
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row.get('date', '')).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            
            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <style>
                    body {{ background: #f4f7f6; padding: 10px; font-family: sans-serif; }}
                    #inv {{ background: white; padding: 30px; width: 750px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); color: black; }}
                    .header-img {{ width: 100%; height: auto; }}
                    .title {{ text-align: center; border-top: 2px solid #000; border-bottom: 2px solid #000; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px; }}
                    .info-table {{ width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold; }}
                    .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }}
                    .data-table th, .data-table td {{ border: 1px solid black; padding: 8px; }}
                    .footer-table {{ width: 100%; margin-top: 30px; font-size: 12px; }}
                    .btn-dl {{ width: 750px; display: block; margin: 20px auto; background: #273746; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }}
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
                            <tr style="background:#f2f2f2;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td>
                                <td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div style="border:1px solid black; padding:10px; margin-top:10px; font-size:12px;"><b>Terbilang:</b> {terbilang(t_val)} Rupiah</div>
                    <table class="footer-table">
                        <tr>
                            <td style="width:60%;"><b>PAYMENT INFO:</b><br>BCA <b>6720422334</b><br><b>ADITYA GAMA SAPUTRI</b></td>
                            <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:100px;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</td>
                        </tr>
                    </table>
                </div>
                <button class="btn-dl" onclick="savePDF()">📥 DOWNLOAD INVOICE (PDF)</button>
                <script>
                    function savePDF() {{
                        const e = document.getElementById('inv');
                        html2pdf().set({{ margin: 0.2, filename: 'Inv_{selected_cust}.pdf', image: {{ type: 'jpeg', quality: 0.98 }}, html2canvas: {{ scale: 3, useCORS: true }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                    }}
                </script>
            </body>
            </html>
            """
            components.html(invoice_html, height=850, scrolling=True)

# --- TAB 2: TAMBAH DATA (DESIGN PRO) ---
with tab2:
    st.markdown("### ➕ INPUT PENGIRIMAN")
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("TANGGAL")
        with c2: v_cust = st.text_input("NAMA CUSTOMER")
        
        v_desc = st.text_input("KETERANGAN BARANG / JENIS MUATAN")
        
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("KOTA ASAL (ORIGIN)")
        with c4: v_dest = st.text_input("KOTA TUJUAN (DESTINATION)")
        
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("JUMLAH KOLLI")
        with c6: v_harga = st.text_input("HARGA SATUAN (RP)")
        with c7: v_weight = st.text_input("BERAT TOTAL (KG)")
        
        c8, c9 = st.columns([2, 1])
        with c8:
            v_status = st.selectbox("STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])
        with c9:
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 SIMPAN KE DATABASE")

        if submit:
            if not v_cust or not v_harga:
                st.error("Mohon isi Nama Customer dan Harga.")
            else:
                h_num = float(v_harga) if v_harga else 0
                w_num = float(v_weight) if v_weight else 0
                payload = {
                    "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                    "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                    "harga": h_num, "weight": w_num, "total": h_num * w_num, "status": v_status
                }
                try:
                    resp = requests.post(API_URL, json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Data Berhasil Disimpan!")
                        st.rerun()
                except:
                    st.error("❌ Gagal terhubung ke server.")
