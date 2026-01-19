import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="3G Logistics Premium", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png",
    layout="wide"
)

# 2. CSS ULTRA-PREMIUM & MEWAH
st.markdown("""
    <style>
    /* Import Font Modern */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global Style */
    .stApp { 
        background-color: #F8F9FA; 
        font-family: 'Inter', sans-serif; 
    }
    
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding-top: 2rem !important; max-width: 900px !important; }

    /* Glassmorphism Card Effect untuk Form */
    div[data-testid="stForm"] {
        background: white !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04) !important;
        padding: 30px !important;
    }

    /* Label Mewah: Tipis, Spasi Lebar, Abu-abu Gelap */
    .stWidgetLabel p { 
        font-weight: 600 !important; 
        color: #4A4A4A !important; 
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: -5px !important;
    }

    /* Input Minimalis: Tanpa Border Tebal, Hanya Garis Bawah saat Fokus */
    .stTextInput input, .stDateInput div, .stSelectbox div[data-baseweb="select"] {
        background-color: #FDFDFD !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        font-weight: 400 !important;
        color: #2C3E50 !important;
        height: 45px !important;
        transition: all 0.4s ease-in-out;
    }

    .stTextInput input:focus {
        border-color: #1A2A3A !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    /* Tombol Premium: Elegan & Berwibawa */
    div.stButton > button {
        background: linear-gradient(135deg, #1A2A3A 0%, #34495E 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        padding: 0.7rem 2rem !important;
        transition: all 0.3s ease;
        width: 100%;
        height: 50px;
        text-transform: uppercase;
        font-size: 13px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(26, 42, 58, 0.3) !important;
    }

    /* Tab Style Modern */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        font-weight: 400 !important;
        color: #95A5A6 !important;
        font-size: 14px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1A2A3A !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #1A2A3A !important;
    }

    /* Rapat & Simpel */
    .stVerticalBlock { gap: 1.2rem !important; }
    
    /* Logo Header */
    .custom-header { text-align: center; margin-bottom: 30px; }
    .custom-header img { width: 100%; max-width: 250px; filter: grayscale(20%); }

    /* Hide Running Status */
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
            return all_data if all_data else []
        return []
    except:
        return []

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', '').replace('Kg', ''))
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
    return ""

# --- TABS ---
tab1, tab2 = st.tabs(["INVOICE CENTER", "NEW DISPATCH"])

# --- TAB 1: INVOICE ---
with tab1:
    raw_data = get_data()
    if not raw_data:
        st.write("---")
        st.caption("Synchronizing database...")
    else:
        df = pd.DataFrame(raw_data)
        st.write("")
        c_filter1, c_filter2 = st.columns([1, 2]) 
        with c_filter1:
            status_f = st.radio("", ["Semua", "Belum Bayar", "Lunas"], horizontal=True, label_visibility="collapsed")
        with c_filter2:
            df_f = df[df['status'] == status_f] if status_f != "Semua" else df
            if not df_f.empty:
                v_cust = st.selectbox("", sorted(df_f['customer'].unique()), label_visibility="collapsed")
            else:
                v_cust = None
        
        st.markdown("<hr style='margin:10px 0; opacity:0.1;'>", unsafe_allow_html=True)
        
        if v_cust:
            row = df_f[df_f['customer'] == v_cust].iloc[-1]
            b_val = extract_number(row.get('weight', 0))
            h_val = extract_number(row.get('harga', 0))
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row.get('date', '')).split('T')[0]
            try: tgl_i = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d %b %Y')
            except: tgl_i = tgl_raw
            
            invoice_html = f"""
            <div style="background:#FFF; padding:40px; border-radius:15px; box-shadow:0 20px 50px rgba(0,0,0,0.05); color:#2C3E50; font-family:sans-serif; max-width:750px; margin:auto; border:1px solid #EEE;">
                <div style="text-align:center; margin-bottom:30px;">
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:280px;">
                    <h2 style="letter-spacing:8px; font-weight:300; margin-top:20px; border-top:1px solid #EEE; border-bottom:1px solid #EEE; padding:10px 0;">INVOICE</h2>
                </div>
                <table style="width:100%; font-size:12px; margin-bottom:20px;">
                    <tr><td><b>CLIENT</b><br>{row['customer']}</td><td style="text-align:right;"><b>DATE</b><br>{tgl_i}</td></tr>
                </table>
                <table style="width:100%; border-collapse:collapse; font-size:12px;">
                    <thead><tr style="background:#F8F9FA; color:#7F8C8D;"><th style="padding:12px; border-bottom:1px solid #EEE;">DESCRIPTION</th><th style="padding:12px; border-bottom:1px solid #EEE;">DESTINATION</th><th style="padding:12px; border-bottom:1px solid #EEE;">TOTAL</th></tr></thead>
                    <tbody><tr><td style="padding:15px; border-bottom:1px solid #F8F9FA;">{row['description']}</td><td style="padding:15px; border-bottom:1px solid #F8F9FA; text-align:center;">{row['destination']}</td><td style="padding:15px; border-bottom:1px solid #F8F9FA; text-align:right; font-weight:bold;">IDR {t_val:,}</td></tr></tbody>
                </table>
                <div style="margin-top:40px; display:flex; justify-content:space-between; align-items:flex-end;">
                    <div style="font-size:10px; color:#95A5A6;"><b>PAYMENT INFO</b><br>BCA 6720422334<br>A.G. SAPUTRI</div>
                    <div style="text-align:center; font-size:10px;">
                        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:80px; opacity:0.8;"><br>
                        <b>KELVINITO JAYADI</b><br>Managing Director
                    </div>
                </div>
            </div>
            """
            st.components.v1.html(invoice_html + f"<button onclick=\"window.print()\" style=\"width:100%; margin-top:20px; background:#1A2A3A; color:white; border:none; padding:15px; border-radius:8px; cursor:pointer; font-weight:bold; letter-spacing:1px;\">EXPORT TO CLOUD</button>", height=750)

# --- TAB 2: INPUT ---
with tab2:
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("TRANS_DATE")
        with c2: v_cust = st.text_input("CLIENT_NAME")
        
        v_desc = st.text_input("CARGO_DESCRIPTION")
        
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("ORIGIN")
        with c4: v_dest = st.text_input("DESTINATION")
        
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("QTY")
        with c6: v_harga = st.text_input("RATE")
        with c7: v_weight = st.text_input("WEIGHT")
        
        v_status = st.selectbox("PAYMENT_STATUS", ["Belum Bayar", "Lunas"])
        
        st.write("")
        submit = st.form_submit_button("CONFIRM & SAVE DATA")

        if submit:
            if v_cust and v_harga:
                payload = {
                    "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                    "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                    "harga": float(v_harga), "weight": float(v_weight) if v_weight else 0, 
                    "total": float(v_harga) * (float(v_weight) if v_weight else 1), "status": v_status
                }
                requests.post(API_URL, json=payload)
                st.success("Transaction Logged Successfully.")
                st.rerun()
