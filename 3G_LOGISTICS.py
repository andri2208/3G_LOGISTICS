import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import requests
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", page_icon="3G.png", layout="wide")

st.markdown("""
    <style>
    @media print {
        header, .stSidebar, .stTabs [data-baseweb="tab-list"], .stActionButton, button { display: none !important; }
        .main .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. URL CONFIG ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzXgo5VKAEzx3WhjB4RIq91oG-N5dKA3sAHGCTNaUOj_f6CGRDHSe12UOL9aZYCuKk_/exec"

# --- 3. FUNGSI PENDUKUNG ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return str(int(n))

logo_base = get_image_base64("3G.png")
stempel_base = get_image_base64("STEMPEL.png")
ttd_base = get_image_base64("TTD.png")

# --- 4. KONEKSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip() 
        return df
    except:
        return pd.DataFrame()

# --- 5. HEADER ---
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="data:image/png;base64,{logo_base}" width="80">
        <div>
            <h1 style="margin: 0; color: #1a3d8d; font-size: 28px;">PT. GAMA GEMAH GEMILANG</h1>
            <p style="margin: 0; color: #d62828; font-weight: bold;">Logistics Management System</p>
        </div>
    </div>
    <hr style="border-top: 3px solid #1a3d8d;">
""", unsafe_allow_html=True)

# --- 6. TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Tambah Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("Nomor Resi")
            customer = st.text_input("Nama Customer")
            produk = st.text_input("Deskripsi Barang")
        with col2:
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
            kolli = st.number_input("Kolli", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0, step=100)
            berat = st.number_input("Berat (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("🚀 SIMPAN DATA"):
            if resi and customer:
                payload = {
                    "Tanggal": tgl.strftime('%d-%b-%y'), "Resi": str(resi),
                    "Pengirim": str(customer), "Produk": str(produk),
                    "Origin": str(origin), "Destination": str(dest),
                    "Kolli": str(int(kolli)), "Harga": str(int(harga)), "Berat": str(float(berat))
                }
                try:
                    resp = requests.post(APPS_SCRIPT_URL, json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Data Berhasil Tersimpan!")
                        st.cache_data.clear()
                    else: st.error("Gagal mengirim data.")
                except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Isi Resi dan Customer!")

with tab2:
    data = fetch_data()
    if not data.empty: st.dataframe(data, use_container_width=True)
    else: st.info("Database kosong.")

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty and 'Resi' in df_inv.columns:
        resi_list = df_inv['Resi'].dropna().unique()
        pilih_resi = st.selectbox("Pilih Resi", resi_list)
        
        if pilih_resi:
            d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
            
            # --- SOLUSI HARGA 4000 (CLEANING) ---
            raw_h = str(d.get('Harga', '0')).split('.')[0]
            h_val = float("".join(filter(str.isdigit, raw_h))) if any(c.isdigit() for c in raw_h) else 0.0
            
            b_val = pd.to_numeric(d.get('Berat', 0), errors='coerce')
            total_float = h_val * (float(b_val) if not pd.isna(b_val) else 0.0)

            html_content = f"""
            <div style="border:1px solid #000; padding:30px; background:white; color:black; font-family:Arial;">
                <table style="width:100%;">
                    <tr>
                        <td style="width:100px;"><img src="data:image/png;base64,{logo_base}" width="100"></td>
                        <td>
                            <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                            <p style="font-size:11px;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.</p>
                        </td>
                        <td style="text-align:right; vertical-align:top;">
                            <h1 style="margin:0; color:#d62828;">INVOICE</h1>
                            <p><b>No: {d.get('Resi','-')}</b></p>
                        </td>
                    </tr>
                </table>
                <hr style="border-top:3px solid #1a3d8d;">
                <p><b>KEPADA:</b> {str(d.get('Pengirim','-')).upper()} <br> <b>TANGGAL:</b> {d.get('Tanggal','-')}</p>
                <table style="width:100%; border-collapse:collapse; border:1px solid black; text-align:center;">
                    <tr style="background:#1a3d8d; color:white;">
                        <th style="border:1px solid black; padding:8px;">Deskripsi</th>
                        <th style="border:1px solid black;">Origin</th>
                        <th style="border:1px solid black;">Dest</th>
                        <th style="border:1px solid black;">Kolli</th>
                        <th style="border:1px solid black;">Berat</th>
                        <th style="border:1px solid black;">Harga</th>
                        <th style="border:1px solid black;">Total</th>
                    </tr>
                    <tr>
                        <td style="border:1px solid black; padding:10px; text-align:left;">{d.get('Produk','-')}</td>
                        <td style="border:1px solid black;">{d.get('Origin','-')}</td>
                        <td style="border:1px solid black;">{d.get('Destination','-')}</td>
                        <td style="border:1px solid black;">{d.get('Kolli',0)}</td>
                        <td style="border:1px solid black;">{b_val} Kg</td>
                        <td style="border:1px solid black;">Rp {h_val:,.0f}</td>
                        <td style="border:1px solid black;"><b>Rp {total_float:,.0f}</b></td>
                    </tr>
                </table>
                <div style="text-align:right; margin-top:15px;">
                    <h3 style="color:#d62828;">TOTAL: Rp {total_float:,.0f}</h3>
                    <p><i>Terbilang: {terbilang(total_float)} Rupiah</i></p>
                </div>
                <table style="width:100%; margin-top:30px;">
                    <tr>
                        <td style="font-size:12px;"><b>TRANSFER:</b><br>BCA: 6720422334<br>A/N: ADITYA GAMA SAPUTRI</td>
                        <td style="text-align:center;">
                            Gresik, {d.get('Tanggal','-')}<br><b>PT. GAMA GEMAH GEMILANG</b><br><br>
                            <img src="data:image/png;base64,{stempel_base}" width="120">
                        </td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.button("Print (Ctrl+P)")
    else: st.warning("Isi data terlebih dahulu.")
