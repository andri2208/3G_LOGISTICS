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

# 2. CSS ULTRA MINIMALIS & CLEAN
st.markdown("""
    <style>
    /* Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* Header & Padding */
    .block-container { padding-top: 1rem !important; max-width: 1100px !important; }
    .header-logo { margin-bottom: 20px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
    
    /* Input Styling - Dibuat Kecil & Rapi */
    .stTextInput input, .stDateInput div, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: white !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 5px !important;
        height: 38px !important;
        font-size: 14px !important;
    }
    
    /* Label Styling */
    .stWidgetLabel p { 
        font-weight: 700 !important; 
        color: #334155 !important; 
        font-size: 12px !important;
        text-transform: uppercase;
        margin-bottom: -10px !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent !important;
        border-radius: 5px 5px 0 0;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #64748B !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1E293B !important;
        border-bottom: 2px solid #1E293B !important;
    }

    /* Hilangkan Elemen Sampah */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stStatusWidget"] { display: none !important; }

    /* Tombol Simpan Modern */
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        border: none !important;
        padding: 10px 25px !important;
        font-weight: 700 !important;
        border-radius: 5px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { background: #334155 !important; }
    </style>
    
    <div class="header-logo">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" width="350">
    </div>
    """, unsafe_allow_html=True)

# 3. LOGIC DATA
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1, show_spinner=False)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            data = response.json()
            for i in data: i.setdefault('status', 'Belum Bayar')
            return data
        return []
    except: return []

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    m = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', '').replace('Kg', ''))
    return float(m[0]) if m else 0

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

# 4. TAMPILAN TAB
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    raw_data = get_data()
    if raw_data:
        df = pd.DataFrame(raw_data)
        
        # Grid Filter (Sejajar & Rapi)
        col_a, col_b = st.columns([1, 1.5])
        with col_a:
            status_f = st.radio("FILTER STATUS:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
        with col_b:
            df_f = df[df['status'] == status_f] if status_f != "Semua" else df
            cust_list = sorted(df_f['customer'].unique()) if not df_f.empty else []
            sel_cust = st.selectbox("PILIH CUSTOMER:", cust_list) if cust_list else st.info("Tidak ada data")
        
        st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        if sel_cust and not df_f.empty:
            row = df_f[df_f['customer'] == sel_cust].iloc[-1]
            h_v = extract_number(row['harga'])
            w_v = extract_number(row['weight'])
            t_v = int(h_v * w_v) if w_v > 0 else int(h_v)
            
            tgl = str(row['date']).split('T')[0]
            try: tgl_f = datetime.strptime(tgl, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_f = tgl
            
            # INVOICE HTML (Tetap sesuai format Bapak)
            inv_html = f"""
            <div id="inv" style="background:white; padding:30px; border:1px solid #DDD; width:750px; margin:auto; font-family:Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:15px 0; padding:5px; font-weight:bold; font-size:20px;">INVOICE</div>
                <table style="width:100%; font-weight:bold; margin-bottom:10px;">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_f}</td></tr>
                </table>
                <table style="width:100%; border-collapse:collapse; text-align:center; font-size:12px;">
                    <tr style="background:#EEE;">
                        <th style="border:1px solid black; padding:8px;">Description</th>
                        <th style="border:1px solid black; padding:8px;">Origin</th>
                        <th style="border:1px solid black; padding:8px;">Dest</th>
                        <th style="border:1px solid black; padding:8px;">KOLLI</th>
                        <th style="border:1px solid black; padding:8px;">HARGA</th>
                        <th style="border:1px solid black; padding:8px;">WEIGHT</th>
                        <th style="border:1px solid black; padding:8px;">TOTAL</th>
                    </tr>
                    <tr>
                        <td style="border:1px solid black; padding:8px;">{row['description']}</td>
                        <td style="border:1px solid black; padding:8px;">{row['origin']}</td>
                        <td style="border:1px solid black; padding:8px;">{row['destination']}</td>
                        <td style="border:1px solid black; padding:8px;">{row['kolli']}</td>
                        <td style="border:1px solid black; padding:8px;">Rp {int(h_v):,}</td>
                        <td style="border:1px solid black; padding:8px;">{row['weight']}</td>
                        <td style="border:1px solid black; padding:8px; font-weight:bold;">Rp {t_v:,}</td>
                    </tr>
                    <tr style="font-weight:bold;">
                        <td colspan="6" style="border:1px solid black; text-align:right; padding:8px;">TOTAL BAYAR</td>
                        <td style="border:1px solid black; padding:8px;">Rp {t_v:,}</td>
                    </tr>
                </table>
                <div style="border:1px solid black; padding:10px; margin-top:10px; font-style:italic; font-size:12px;"><b>Terbilang:</b> {terbilang(t_v)} Rupiah</div>
                <table style="width:100%; margin-top:20px; font-size:12px;">
                    <tr>
                        <td><b>TRANSFER TO:</b><br>BCA 6720422334<br>ADITYA GAMA SAPUTRI</td>
                        <td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" width="100"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</td>
                    </tr>
                </table>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="savePDF()" style="width:750px; display:block; margin:20px auto; background:#1A2A3A; color:white; padding:12px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">📥 DOWNLOAD PDF</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('inv');
                    html2pdf().set({{ margin:0, filename:'Inv_{sel_cust}.pdf', image:{{type:'jpeg', quality:0.98}}, html2canvas:{{scale:3, useCORS:true}}, jsPDF:{{unit:'in', format:'a5', orientation:'landscape'}} }}).from(e).save();
                }}
            </script>
            """
            components.html(inv_html, height=800, scrolling=True)

with tab2:
    st.markdown("### ➕ Input Pengiriman Baru")
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("TANGGAL")
        with c2: v_cust = st.text_input("NAMA CUSTOMER")
        
        v_desc = st.text_input("KETERANGAN BARANG")
        
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("ASAL (ORIGIN)")
        with c4: v_dest = st.text_input("TUJUAN (DESTINATION)")
        
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("KOLLI")
        with c6: v_harga = st.number_input("HARGA/KG", min_value=0)
        with c7: v_weight = st.number_input("BERAT (KG)", min_value=0.0)
        
        v_status = st.selectbox("STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])
        
        if st.form_submit_button("🚀 SIMPAN DATA"):
            if v_cust and v_harga:
                payload = {
                    "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                    "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                    "harga": v_harga, "weight": v_weight, "total": v_harga * v_weight, "status": v_status
                }
                requests.post(API_URL, json=payload)
                st.success("Berhasil!")
                st.rerun()
