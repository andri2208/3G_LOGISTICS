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

# 2. CSS STABIL (Sesuai keinginan: Rapat, Sticky, Rapi)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 2rem !important; }
    [data-testid="stImage"] { margin-bottom: 10px !important; margin-top: -10px !important; }
    
    div[data-testid="stTabs"] {
        position: sticky; top: 0; z-index: 999;
        background-color: white; padding-top: 15px;
        padding-bottom: 10px; border-bottom: 3px solid #B8860B;
    }

    .stTabs [data-baseweb="tab"] p { color: #1A2A3A !important; font-weight: 800 !important; font-size: 18px; }

    [data-testid="stForm"] {
        background-color: #719dc9 !important; padding: 2.5rem !important;
        border-radius: 20px !important; border: 4px solid #B8860B !important;
    }

    .stWidgetLabel p { color: white !important; font-weight: 900 !important; }
    #MainMenu, footer {visibility: hidden;}
    
    /* Tombol Update Biru */
    button[kind="secondary"] {
        background-color: #1e3d59 !important; color: white !important;
        font-weight: bold !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AREA HEADER
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)

# 4. TAMPILAN TABS
tab1, tab2 = st.tabs(["📄 CETAK & UBAH INVOICE", "➕ TAMBAH DATA"])

API_URL = "https://script.google.com/macros/s/AKfycbwh5n3RxYYWqX4HV9_DEkOtSPAomWM8x073OME-JttLHeYfuwSha06AAs5fuayvHEludw/exec"

def get_data():
    try:
        response = requests.get(f"{API_URL}?t={datetime.now().timestamp()}")
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

with tab1:
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        st.write("###")
        f_col1, f_col2, f_col3 = st.columns([1, 1.2, 1.5])
        with f_col1:
            status_filter = st.radio("**STATUS:**", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
            df_filtered = df[df['status'] == status_filter] if status_filter != "Semua" else df
        with f_col2:
            cust_list = sorted(df_filtered['customer'].unique()) if not df_filtered.empty else []
            selected_cust = st.selectbox("**NAMA CUSTOMER:**", cust_list)
        with f_col3:
            if selected_cust:
                sub_df = df_filtered[df_filtered['customer'] == selected_cust].copy()
                sub_df['label'] = sub_df['date'].astype(str).str.split('T').str[0] + " | " + sub_df['description']
                selected_label = st.selectbox("**PILIH TRANSAKSI:**", sub_df['label'].tolist())

        if selected_cust and selected_label:
            row = sub_df[sub_df['label'] == selected_label].iloc[-1]
            
            # --- FITUR UBAH DATA (EDIT MODE) ---
            with st.expander("🛠️ UBAH DATA INVOICE INI (Klik untuk edit)"):
                with st.form("edit_form"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        new_desc = st.text_input("ITEM", value=row['description'])
                        new_orig = st.text_input("ORIGIN", value=row['origin'])
                        new_dest = st.text_input("DESTINATION", value=row['destination'])
                    with e_col2:
                        new_harga = st.number_input("HARGA", value=float(extract_number(row['harga'])))
                        new_weight = st.number_input("WEIGHT", value=float(extract_number(row['weight'])))
                        new_status = st.selectbox("STATUS", ["Belum Bayar", "Lunas"], index=0 if row['status']=="Belum Bayar" else 1)
                    
                    if st.form_submit_button("✅ UPDATE DATA"):
                        payload = {
                            "action": "edit", 
                            "date": row['date'], 
                            "customer": row['customer'],
                            "description": new_desc.upper(),
                            "origin": new_orig.upper(),
                            "destination": new_dest.upper(),
                            "harga": new_harga,
                            "weight": new_weight,
                            "status": new_status,
                            "total": new_harga * new_weight
                        }
                        # Kirim ke Apps Script (Pastikan Apps Script Bapak sudah mendukung pencarian & update baris)
                        requests.post(API_URL, json=payload)
                        st.success("Data berhasil diupdate! Merefresh...")
                        st.rerun()

            # --- TAMPILAN INVOICE ---
            b_val, h_val = extract_number(row['weight']), extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            tgl_raw = str(row['date']).split('T')[0]
            try: tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except: tgl_indo = tgl_raw
            kata_terbilang = terbilang(t_val) + " Rupiah"

            invoice_html = f"""
            <div id="inv" style="background: white; padding: 25px; border: 1px solid #ccc; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                <table style="width: 100%; font-weight: bold;"><tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr></table>
                <table style="width: 100%; border-collapse: collapse; margin-top:10px; text-align: center;">
                    <tr style="background:#eee;"><th>Description</th><th>Origin</th><th>Dest</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                    <tr><td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td><b>Rp {t_val:,}</b></td></tr>
                </table>
                <div style="margin-top:20px;">Sincerely,<br><br><br><b>KELVINITO JAYADI</b></div>
            </div>
            """
            st.markdown(invoice_html, unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 style='text-align: center; color: white;'>TAMBAH DATA PENGIRIMAN</h2>", unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        v_tgl = c1.date_input("📅 TANGGAL")
        v_cust = c2.text_input("🏢 CUSTOMER")
        v_desc = c3.text_input("📦 ITEM")
        c4, c5, c6 = st.columns(3)
        v_orig = c4.text_input("📍 ORIGIN")
        v_dest = c5.text_input("🏁 DESTINATION")
        v_harga = c6.number_input("💰 HARGA", value=0.0)
        v_weight = st.number_input("⚖️ BERAT (Kg)", value=0.0)
        v_status = st.selectbox("💳 STATUS", ["Belum Bayar", "Lunas"])
        
        if st.form_submit_button("🚀 SIMPAN SEKARANG"):
            payload = {"date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(), "origin": v_orig.upper(), "destination": v_dest.upper(), "harga": v_harga, "weight": v_weight, "total": v_harga * v_weight, "status": v_status}
            requests.post(API_URL, json=payload)
            st.success("DATA TERSIMPAN!")
            st.rerun()
