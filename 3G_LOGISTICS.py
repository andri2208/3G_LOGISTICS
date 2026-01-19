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

# 2. CSS ULTRA-PREMIUM (DAPUR APLIKASI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .stApp { background-color: #F4F7F9; font-family: 'Inter', sans-serif; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container { padding-top: 1.5rem !important; max-width: 1000px !important; }

    /* Container Form & Tab */
    div[data-testid="stForm"] {
        background: white !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        padding: 40px !important;
    }

    /* Input Style */
    .stTextInput input, .stDateInput div, .stSelectbox div[data-baseweb="select"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        height: 48px !important;
    }
    
    .stWidgetLabel p { 
        font-weight: 700 !important; color: #475569 !important; 
        font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Button Style */
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 50px;
        width: 100%;
        border: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { background: #334155 !important; transform: translateY(-2px); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 14px !important; color: #94A3B8 !important; }
    .stTabs [aria-selected="true"] { color: #1E293B !important; font-weight: 800 !important; border-bottom: 3px solid #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# API CONFIG
API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

@st.cache_data(ttl=1, show_spinner=False)
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        return response.json() if response.status_code == 200 else []
    except: return []

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
t1, t2 = st.tabs(["🏛️ INVOICE CENTER", "📦 NEW SHIPMENT"])

with t1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.markdown("<br>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns([1, 2])
        with c_f1: status_f = st.radio("Status", ["Semua", "Belum Bayar", "Lunas"], horizontal=True, label_visibility="collapsed")
        with c_f2:
            df_f = df[df['status'] == status_f] if status_f != "Semua" else df
            cust = st.selectbox("Client", sorted(df_f['customer'].unique()) if not df_f.empty else ["No Data"], label_visibility="collapsed")
        
        if cust != "No Data":
            row = df_f[df_f['customer'] == cust].iloc[-1]
            h_v = extract_number(row.get('harga', 0))
            w_v = extract_number(row.get('weight', 0))
            total = int(h_v * w_v) if w_v > 0 else int(h_v)
            
            # FORMAT TANGGAL
            tgl_raw = str(row.get('date', '')).split('T')[0]
            try: tgl_f = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d %B %Y')
            except: tgl_f = tgl_raw

            # --- THE CORPORATE INVOICE HTML ---
            inv_html = f"""
            <div id="invoice-box" style="background:white; padding:50px; border:1px solid #EEE; max-width:800px; margin:auto; color:#333; font-family:'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <table style="width:100%; margin-bottom:20px;">
                    <tr>
                        <td style="width:50%"><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:300px;"></td>
                        <td style="text-align:right; vertical-align:top;">
                            <h1 style="margin:0; color:#1A2A3A; letter-spacing:-1px;">INVOICE</h1>
                            <p style="margin:0; font-size:12px; color:#666;">No: INV/3G/{datetime.now().strftime('%Y%m%d')}/{row.name}</p>
                        </td>
                    </tr>
                </table>

                <div style="background:#1A2A3A; height:8px; margin-bottom:30px;"></div>

                <table style="width:100%; margin-bottom:40px; font-size:13px;">
                    <tr>
                        <td style="width:50%;"><b>BILLED TO:</b><br><span style="font-size:18px; color:#1A2A3A;">{row['customer']}</span></td>
                        <td style="text-align:right;"><b>DATE:</b><br>{tgl_f}</td>
                    </tr>
                </table>

                <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                    <thead>
                        <tr style="background:#F8F9FA; text-align:left;">
                            <th style="padding:15px; border-bottom:2px solid #1A2A3A;">DESCRIPTION</th>
                            <th style="padding:15px; border-bottom:2px solid #1A2A3A; text-align:center;">DESTINATION</th>
                            <th style="padding:15px; border-bottom:2px solid #1A2A3A; text-align:right;">AMOUNT</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding:20px 15px; border-bottom:1px solid #EEE;">
                                <b>{row['description']}</b><br>
                                <span style="font-size:11px; color:#666;">Origin: {row['origin']} | Qty: {row['kolli']} | Rate: Rp {int(h_v):,}</span>
                            </td>
                            <td style="padding:20px 15px; border-bottom:1px solid #EEE; text-align:center;">{row['destination']}</td>
                            <td style="padding:20px 15px; border-bottom:1px solid #EEE; text-align:right; font-weight:bold;">Rp {total:,}</td>
                        </tr>
                    </tbody>
                </table>

                <table style="width:100%;">
                    <tr>
                        <td style="width:60%; vertical-align:top;">
                            <div style="background:#F8F9FA; padding:15px; border-radius:5px; font-size:11px;">
                                <b>TERBILANG:</b><br>
                                <i style="text-transform:capitalize;"># {terbilang(total)} Rupiah #</i>
                            </div>
                            <div style="margin-top:20px; font-size:11px;">
                                <b>PAYMENT DETAILS:</b><br>
                                Bank BCA: <b>6720422334</b><br>
                                A/N: <b>ADITYA GAMA SAPUTRI</b>
                            </div>
                        </td>
                        <td style="text-align:center; vertical-align:top;">
                            <div style="position:relative; display:inline-block;">
                                <p style="font-size:12px; margin-bottom:50px;">Sincerely,</p>
                                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="position:absolute; top:20px; left:10px; width:110px; opacity:0.8;">
                                <p style="font-size:13px; font-weight:bold; margin:0;"><u>KELVINITO JAYADI</u></p>
                                <p style="font-size:11px; color:#666; margin:0;">Managing Director</p>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="generatePDF()" style="width:100%; margin-top:20px; background:#1A2A3A; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:14px; letter-spacing:1px;">📥 DOWNLOAD OFFICIAL INVOICE (PDF)</button>
            <script>
                function generatePDF() {{
                    const element = document.getElementById('invoice-box');
                    const opt = {{
                        margin: 0.5,
                        filename: 'Invoice_{row['customer']}.pdf',
                        image: {{ type: 'jpeg', quality: 0.98 }},
                        html2canvas: {{ scale: 2 }},
                        jsPDF: {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
                    }};
                    html2pdf().set(opt).from(element).save();
                }}
            </script>
            """
            components.html(inv_html, height=900, scrolling=True)

with t2:
    st.markdown("### 📝 RECORD SHIPMENT")
    with st.form("ship_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: v_tgl = st.date_input("Date")
        with c2: v_cust = st.text_input("Customer Name")
        v_desc = st.text_input("Cargo Details")
        c3, c4 = st.columns(2)
        with c3: v_orig = st.text_input("Origin")
        with c4: v_dest = st.text_input("Destination")
        c5, c6, c7 = st.columns(3)
        with c5: v_kol = st.text_input("Qty (Kolli)")
        with c6: v_harga = st.text_input("Rate (Price)")
        with c7: v_weight = st.text_input("Weight (Kg)")
        v_status = st.selectbox("Payment Status", ["Belum Bayar", "Lunas"])
        if st.form_submit_button("SAVE TO DATABASE"):
            if v_cust and v_harga:
                payload = {
                    "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                    "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                    "harga": float(v_harga), "weight": float(v_weight) if v_weight else 0,
                    "total": float(v_harga) * (float(v_weight) if v_weight else 1), "status": v_status
                }
                requests.post(API_URL, json=payload)
                st.success("Data secured.")
                st.rerun()
