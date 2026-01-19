import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", layout="wide")

# 2. CSS STABIL (Rapat & Sticky)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 2rem !important; }
    [data-testid="stImage"] { margin-bottom: 10px !important; margin-top: -10px !important; }
    div[data-testid="stTabs"] { position: sticky; top: 0; z-index: 999; background: white; border-bottom: 3px solid #B8860B; }
    .stTabs [data-baseweb="tab"] p { font-weight: 800; font-size: 18px; }
    [data-testid="stForm"] { background: #719dc9; padding: 2.5rem; border-radius: 20px; border: 4px solid #B8860B; }
    .stWidgetLabel p { color: white !important; font-weight: 900; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)

# 4. TABS
tab1, tab2 = st.tabs(["📄 CETAK & UBAH INVOICE", "➕ TAMBAH DATA"])

API_URL = "https://script.google.com/macros/s/AKfycbwRe6CS9qBnlKyTQ422zH_WozMPv3O2X-FlzYWeqXh-gXOH62L8RboutIuWRmlgCEvFPQ/exec"

def get_data():
    try:
        response = requests.get(f"{API_URL}?t={datetime.now().timestamp()}")
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

with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.write("###")
        c1, c2, c3 = st.columns([1, 1.2, 1.5])
        with c1: f_status = st.radio("STATUS:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
        df_f = df[df['status'] == f_status] if f_status != "Semua" else df
        with c2: 
            cust_list = sorted(df_f['customer'].unique()) if not df_f.empty else []
            s_cust = st.selectbox("CUSTOMER:", cust_list)
        with c3:
            if s_cust:
                sub_df = df_f[df_f['customer'] == s_cust].copy()
                sub_df['label'] = sub_df['date'].astype(str).str.split('T').str[0] + " | " + sub_df['description']
                s_label = st.selectbox("TRANSAKSI:", sub_df['label'].tolist())

        if s_cust and s_label:
            row = sub_df[sub_df['label'] == s_label].iloc[-1]
            
            # --- FORM EDIT ---
            with st.expander("🛠️ UBAH DATA (EDIT MODE)"):
                with st.form("edit_form"):
                    e1, e2 = st.columns(2)
                    v_desc = e1.text_input("ITEM", value=row['description'])
                    v_orig = e1.text_input("ORIGIN", value=row['origin'])
                    v_dest = e1.text_input("DEST", value=row['destination'])
                    v_kol = e1.text_input("KOLLI", value=row['kolli'])
                    v_harga = e2.number_input("HARGA", value=float(extract_number(row['harga'])))
                    v_weight = e2.number_input("WEIGHT", value=float(extract_number(row['weight'])))
                    v_status = e2.selectbox("STATUS", ["Belum Bayar", "Lunas"], index=0 if row['status']=="Belum Bayar" else 1)
                    if st.form_submit_button("💾 SIMPAN PERUBAHAN"):
                        payload = {"action": "edit", "date": row['date'], "customer": row['customer'], "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol, "harga": v_harga, "weight": v_weight, "status": v_status}
                        requests.post(API_URL, json=payload)
                        st.success("Tersimpan!")
                        st.rerun()

            # --- INVOICE ASLI ---
            h_val, w_val = extract_number(row['harga']), extract_number(row['weight'])
            t_val = int(h_val * w_val)
            tgl_indo = str(row['date']).split('T')[0]
            
            invoice_html = f"""
            <div id="inv" style="background: white; padding: 25px; width: 700px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                <table style="width: 100%; font-size: 14px; font-weight: bold;"><tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr></table>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; text-align: center;">
                    <tr style="border: 1px solid black;"><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr style="border: 1px solid black;"><td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td><b>Rp {t_val:,}</b></td></tr>
                </table>
                <div style="margin-top: 20px; font-size: 12px;"><b>Terbilang:</b> {terbilang(t_val)} Rupiah</div>
                <table style="width: 100%; margin-top: 20px; font-size: 12px;">
                    <tr><td>BCA <b>6720422334</b> - <b>ADITYA GAMA SAPUTRI</b></td><td style="text-align:center;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" width="100"><br><b>KELVINITO JAYADI</b></td></tr>
                </table>
            </div>
            """
            components.html(invoice_html, height=800, scrolling=True)

with tab2:
    with st.form("input_baru"):
        r1c1, r1c2, r1c3 = st.columns(3)
        n_tgl = r1c1.date_input("TANGGAL")
        n_cust = r1c2.text_input("CUSTOMER")
        n_item = r1c3.text_input("ITEM")
        r2c1, r2c2, r2c3 = st.columns(3)
        n_orig = r2c1.text_input("ORIGIN")
        n_dest = r2c2.text_input("DEST")
        n_kol = r2c3.text_input("KOLLI")
        r3c1, r3c2, r3c3 = st.columns(3)
        n_hrg = r3c1.number_input("HARGA", value=0.0)
        n_wgt = r3c2.number_input("BERAT", value=0.0)
        n_stat = r3c3.selectbox("STATUS", ["Belum Bayar", "Lunas"])
        if st.form_submit_button("🚀 SIMPAN DATA"):
            payload = {"date": str(n_tgl), "customer": n_cust.upper(), "description": n_item.upper(), "origin": n_orig.upper(), "destination": n_dest.upper(), "kolli": n_kol, "harga": n_hrg, "weight": n_wgt, "status": n_stat}
            requests.post(API_URL, json=payload)
            st.success("Tersimpan!"); st.rerun()
