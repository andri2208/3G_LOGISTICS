import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics Pro", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", 
    layout="wide"
)

# 2. CSS CUSTOM: FULL COLOR DENGAN TEKS PUTIH TERANG (ANTI-SCROLL)
st.markdown("""
    <style>
    /* Dasar Web */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
    
    /* PANEL INPUT DATA (NAVY DARK) */
    [data-testid="stForm"] {
        background-color: #1A2A3A !important;
        padding: 15px 25px !important; /* Dipersempit agar muat 1 layar */
        border-radius: 15px !important;
        border: 2px solid #B8860B !important; 
    }

    /* LABEL INPUT (PUTIH TERANG) */
    .stWidgetLabel p { 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        font-size: 12px !important; /* Font sedikit dikecilkan agar rapat */
        text-transform: uppercase;
        margin-bottom: -15px !important;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* KOTAK INPUT (PUTIH BERSIH, TEKS HITAM) */
    .stTextInput input, .stDateInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #B8860B !important;
        border-radius: 8px !important;
        height: 38px !important; /* Tinggi kotak dioptimalkan */
        color: #000000 !important;
        font-size: 14px !important;
        font-weight: 700 !important;
    }

    /* Memastikan teks dalam tanggal & selectbox berwarna HITAM */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Menghilangkan Border Ganda */
    div[data-baseweb="input"], div[data-baseweb="select"] { border: none !important; }

    /* TOMBOL SIMPAN EMAS */
    div.stButton > button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%) !important;
        color: #1A2A3A !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border-radius: 8px !important;
        height: 45px;
        width: 100%;
        border: none !important;
        margin-top: 10px;
    }

    /* Header & Tabs Ramping */
    .custom-header { text-align: left; margin-bottom: 5px; }
    .custom-header img { max-width: 250px; height: auto; }
    .stTabs [aria-selected="true"] { color: #1A2A3A !important; border-bottom: 3px solid #B8860B !important; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
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

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA"])

with tab1:
    # AREA CETAK INVOICE (TIDAK DISENTUH SAMA SEKALI)
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

            invoice_html = f"""
            <div id="inv" style="background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width: 100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                <table style="width: 100%; font-weight: bold; font-size: 14px;">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                </table>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-top: 10px;">
                    <tr style="background: #f2f2f2;">
                        <th style="border: 1px solid black; padding: 5px;">Description</th>
                        <th style="border: 1px solid black; padding: 5px;">Origin</th>
                        <th style="border: 1px solid black; padding: 5px;">Dest</th>
                        <th style="border: 1px solid black; padding: 5px;">KOLLI</th>
                        <th style="border: 1px solid black; padding: 5px;">HARGA</th>
                        <th style="border: 1px solid black; padding: 5px;">WEIGHT</th>
                        <th style="border: 1px solid black; padding: 5px;">TOTAL</th>
                    </tr>
                    <tr>
                        <td style="border: 1px solid black; padding: 5px;">{row['description']}</td>
                        <td style="border: 1px solid black; padding: 5px;">{row['origin']}</td>
                        <td style="border: 1px solid black; padding: 5px;">{row['destination']}</td>
                        <td style="border: 1px solid black; padding: 5px;">{row['kolli']}</td>
                        <td style="border: 1px solid black; padding: 5px;">Rp {int(h_val):,}</td>
                        <td style="border: 1px solid black; padding: 5px;">{row['weight']}</td>
                        <td style="border: 1px solid black; padding: 5px; font-weight: bold;">Rp {t_val:,}</td>
                    </tr>
                </table>
            </div>
            """
            st.components.v1.html(invoice_html, height=500)

with tab2:
    st.markdown("<h4 style='text-align: center; color: #1A2A3A; margin-top: -10px; margin-bottom: 5px;'>NEW DISPATCH ENTRY</h4>", unsafe_allow_html=True)
    
    with st.form("input_form", clear_on_submit=True):
        # Baris 1
        col1, col2 = st.columns(2)
        with col1: v_tgl = st.date_input("📅 TANGGAL PENGIRIMAN")
        with col2: v_cust = st.text_input("🏢 NAMA CUSTOMER")

        # Baris 2
        v_desc = st.text_input("📦 KETERANGAN BARANG")

        # Baris 3
        col3, col4 = st.columns(2)
        with col3: v_orig = st.text_input("📍 ASAL (ORIGIN)")
        with col4: v_dest = st.text_input("🏁 TUJUAN (DESTINATION)")

        # Baris 4
        col5, col6, col7 = st.columns(3)
        with col5: v_kol = st.text_input("📦 JUMLAH KOLLI")
        with col6: v_harga = st.text_input("💰 HARGA PER KG")
        with col7: v_weight = st.text_input("⚖️ BERAT TOTAL")

        # Baris 5
        v_status = st.selectbox("💳 STATUS PEMBAYARAN", ["Belum Bayar", "Lunas"])

        # Tombol
        submit = st.form_submit_button("🚀 SIMPAN DATA KE GOOGLE SHEETS")

        if submit:
            if v_cust and v_harga:
                try:
                    payload = {
                        "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                        "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                        "harga": float(v_harga), "weight": float(v_weight), 
                        "total": float(v_harga) * float(v_weight), "status": v_status
                    }
                    requests.post(API_URL, json=payload)
                    st.success("DATA BERHASIL DISIMPAN!")
                    st.rerun()
                except: st.error("HARGA & BERAT HARUS ANGKA!")
